"""
Authentication service layer.

Contains the business logic for registering users, authenticating
credentials, and resolving the "current user" from a JWT bearer token.
Keeping this logic out of the API layer makes it independently testable
and keeps app/api/auth.py focused on HTTP concerns only.
"""

import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token, hash_password, verify_password
from app.database.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate

logger = logging.getLogger(__name__)

# tokenUrl points at the login endpoint; used only for Swagger UI's
# "Authorize" button, the client itself just needs any bearer token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def register_user(db: Session, user_in: UserCreate) -> User:
    """
    Create a new user account.
    Raises HTTPException(400) if the email is already registered.
    """
    existing_user = get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    new_user = User(
        name=user_in.name,
        email=user_in.email,
        password=hash_password(user_in.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info("New user registered: %s", new_user.email)
    return new_user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """
    Verify credentials. Returns the User if valid, else None.
    """
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency: decodes the bearer token, validates it, and loads
    the corresponding user from the database. Used to protect routes.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if token is None:
        raise credentials_exception

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    email: str | None = payload.get("sub")
    if email is None:
        raise credentials_exception

    user = get_user_by_email(db, email)
    if user is None:
        raise credentials_exception

    return user
