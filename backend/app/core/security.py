"""
Security utilities:
- Password hashing & verification (bcrypt via passlib)
- JWT access token creation & decoding
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# ----------------------------------------------------------------------
# Password hashing
# ----------------------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against its bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ----------------------------------------------------------------------
# JWT tokens
# ----------------------------------------------------------------------
def create_access_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    """
    Create a signed JWT access token.

    `subject` is typically the user's email or id and is stored in the
    standard "sub" claim.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode: dict[str, Any] = {"sub": str(subject), "exp": expire}
    if extra_claims:
        to_encode.update(extra_claims)

    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """
    Decode and validate a JWT access token.
    Returns the payload dict if valid, otherwise None.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None
