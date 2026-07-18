"""
User ORM model — maps to the `users` table in MySQL.
"""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)  # bcrypt hash
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # One user has many predictions. `cascade="all, delete-orphan"` means
    # deleting a user also deletes their prediction history.
    predictions = relationship(
        "Prediction",
        back_populates="owner",
        cascade="all, delete-orphan",
        foreign_keys="Prediction.user_id",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"
