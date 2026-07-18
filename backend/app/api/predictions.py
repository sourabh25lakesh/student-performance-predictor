from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.prediction import PredictionActionResult, PredictionCreate, PredictionOut, PredictionResult
from app.services.auth_service import get_current_user
from app.services.prediction_service import (
    create_prediction,
    list_deleted_predictions,
    list_user_predictions,
    permanently_delete_prediction,
    restore_prediction,
    soft_delete_prediction,
)

router = APIRouter(tags=["Predictions"])


@router.post(
    "/predict",
    response_model=PredictionResult,
    status_code=status.HTTP_201_CREATED,
    summary="Predict final marks and save the result",
)
def predict_student_marks(
    prediction_in: PredictionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prediction = create_prediction(db, prediction_in, current_user)
    return PredictionResult(prediction=prediction)


@router.get(
    "/predictions",
    response_model=list[PredictionOut],
    summary="Get prediction history for the current user",
)
def prediction_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_user_predictions(db, current_user)


@router.get(
    "/predictions/trash",
    response_model=list[PredictionOut],
    summary="Get deleted predictions for the current user",
)
def prediction_trash(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_deleted_predictions(db, current_user)


@router.patch(
    "/predictions/{prediction_id}/soft-delete",
    response_model=PredictionActionResult,
    summary="Move a prediction to Trash",
)
def move_prediction_to_trash(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prediction = soft_delete_prediction(db, prediction_id, current_user)
    return PredictionActionResult(message="Prediction moved to Trash.", prediction=prediction)


@router.patch(
    "/predictions/{prediction_id}/restore",
    response_model=PredictionActionResult,
    summary="Restore a deleted prediction",
)
def restore_deleted_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prediction = restore_prediction(db, prediction_id, current_user)
    return PredictionActionResult(message="Prediction restored successfully.", prediction=prediction)


@router.delete(
    "/predictions/{prediction_id}/permanent",
    response_model=PredictionActionResult,
    summary="Permanently delete a prediction from Trash",
)
def delete_prediction_permanently(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    permanently_delete_prediction(db, prediction_id, current_user)
    return PredictionActionResult(message="Prediction permanently deleted.")
