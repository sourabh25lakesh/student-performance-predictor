"""
Pydantic schemas related to JWT authentication tokens.
"""

from pydantic import BaseModel


class Token(BaseModel):
    """Response body returned after a successful login."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Data decoded from a JWT token's payload."""

    email: str | None = None
