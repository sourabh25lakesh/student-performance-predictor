"""
Authentication endpoints:
- POST /auth/register
- POST /auth/login
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.database.database import get_db
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserLogin, UserOut
from app.services.auth_service import authenticate_user, register_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account.

    - **name**: full name of the user
    - **email**: must be unique
    - **password**: minimum 6 characters (stored as a bcrypt hash)
    """
    user = register_user(db, user_in)
    return user


@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate and receive a JWT access token",
)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate with email + password and receive a JWT bearer token.
    Use this token in the `Authorization: Bearer <token>` header for
    protected routes.
    """
    user = authenticate_user(db, credentials.email, credentials.password)
    if not user:
        logger.warning("Failed login attempt for email: %s", credentials.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.email)
    logger.info("User logged in: %s", user.email)
    return Token(access_token=access_token)


@router.post(
    "/logout",
    summary="Logout (client-side token discard)",
)
def logout():
    """
    JWTs are stateless, so "logout" simply means the client discards the
    token (e.g. removes it from localStorage). This endpoint exists for
    a consistent API surface and to allow future blacklist support.
    """
    return {"message": "Logout successful. Please discard your access token."}
