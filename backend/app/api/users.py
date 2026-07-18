"""
User endpoints:
- GET /users/me   (protected route example)
"""

from fastapi import APIRouter, Depends

from app.models.user import User
from app.schemas.user import UserOut
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserOut,
    summary="Get the currently authenticated user's profile",
)
def read_current_user(current_user: User = Depends(get_current_user)):
    """
    Protected route. Requires a valid JWT bearer token.
    Returns the profile of the currently logged-in user.
    """
    return current_user
