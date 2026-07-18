from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.prediction import DashboardOut
from app.services.auth_service import get_current_user
from app.services.prediction_service import get_dashboard

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "",
    response_model=DashboardOut,
    summary="Get dashboard summary for the current user",
)
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_dashboard(db, current_user)
