from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.ml.model import get_grade, get_pass_fail, predict_marks
from app.models.prediction import Prediction
from app.models.user import User
from app.schemas.prediction import DashboardOut, PredictionCreate


def _active_predictions_query(db: Session, current_user: User):
    return db.query(Prediction).filter(
        Prediction.user_id == current_user.id,
        Prediction.is_deleted.is_(False),
    )


def _deleted_predictions_query(db: Session, current_user: User):
    return db.query(Prediction).filter(
        Prediction.user_id == current_user.id,
        Prediction.is_deleted.is_(True),
    )


def _get_owned_prediction(db: Session, prediction_id: int, current_user: User) -> Prediction:
    prediction = (
        db.query(Prediction)
        .filter(Prediction.id == prediction_id, Prediction.user_id == current_user.id)
        .first()
    )
    if prediction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found.",
        )
    return prediction


def create_prediction(
    db: Session,
    prediction_in: PredictionCreate,
    current_user: User,
) -> Prediction:
    predicted_marks = predict_marks(
        hours_studied=prediction_in.hours_studied,
        attendance=prediction_in.attendance,
        previous_marks=prediction_in.previous_marks,
    )

    prediction = Prediction(
        user_id=current_user.id,
        student_name=prediction_in.student_name,
        hours_studied=prediction_in.hours_studied,
        attendance=prediction_in.attendance,
        previous_marks=prediction_in.previous_marks,
        predicted_marks=predicted_marks,
        grade=get_grade(predicted_marks),
        status=get_pass_fail(predicted_marks),
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction


def list_user_predictions(db: Session, current_user: User) -> list[Prediction]:
    return (
        _active_predictions_query(db, current_user)
        .order_by(Prediction.created_at.desc(), Prediction.id.desc())
        .all()
    )


def list_deleted_predictions(db: Session, current_user: User) -> list[Prediction]:
    return (
        _deleted_predictions_query(db, current_user)
        .order_by(Prediction.deleted_at.desc(), Prediction.id.desc())
        .all()
    )


def soft_delete_prediction(db: Session, prediction_id: int, current_user: User) -> Prediction:
    prediction = _get_owned_prediction(db, prediction_id, current_user)
    if prediction.is_deleted:
        return prediction

    prediction.is_deleted = True
    prediction.deleted_at = datetime.now(timezone.utc).replace(tzinfo=None)
    prediction.deleted_by = current_user.id
    db.commit()
    db.refresh(prediction)
    return prediction


def restore_prediction(db: Session, prediction_id: int, current_user: User) -> Prediction:
    prediction = _get_owned_prediction(db, prediction_id, current_user)
    if not prediction.is_deleted:
        return prediction

    prediction.is_deleted = False
    prediction.deleted_at = None
    prediction.deleted_by = None
    db.commit()
    db.refresh(prediction)
    return prediction


def permanently_delete_prediction(db: Session, prediction_id: int, current_user: User) -> None:
    prediction = _get_owned_prediction(db, prediction_id, current_user)
    if not prediction.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Move this prediction to Trash before deleting it permanently.",
        )

    db.delete(prediction)
    db.commit()


def get_dashboard(db: Session, current_user: User) -> DashboardOut:
    base_query = _active_predictions_query(db, current_user)

    total_predictions = base_query.count()
    pass_count = base_query.filter(Prediction.status == "Pass").count()
    fail_count = base_query.filter(Prediction.status == "Fail").count()
    average_predicted_marks = (
        db.query(func.avg(Prediction.predicted_marks))
        .filter(Prediction.user_id == current_user.id, Prediction.is_deleted.is_(False))
        .scalar()
        or 0.0
    )
    latest_predictions = (
        base_query.order_by(Prediction.created_at.desc(), Prediction.id.desc()).limit(5).all()
    )

    return DashboardOut(
        total_predictions=total_predictions,
        pass_count=pass_count,
        fail_count=fail_count,
        average_predicted_marks=round(float(average_predicted_marks), 2),
        latest_predictions=latest_predictions,
    )
