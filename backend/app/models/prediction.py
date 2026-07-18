from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    student_name: Mapped[str] = mapped_column(String(100), nullable=False)
    hours_studied: Mapped[float] = mapped_column(Float, nullable=False)
    attendance: Mapped[float] = mapped_column(Float, nullable=False)
    previous_marks: Mapped[float] = mapped_column(Float, nullable=False)

    predicted_marks: Mapped[float] = mapped_column(Float, nullable=False)
    grade: Mapped[str] = mapped_column(String(5), nullable=False)
    status: Mapped[str] = mapped_column(String(10), nullable=False)  # "Pass" | "Fail"

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0", index=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    owner = relationship("User", back_populates="predictions", foreign_keys=[user_id])
    deleted_by_user = relationship("User", foreign_keys=[deleted_by])

    def __repr__(self) -> str:
        return f"<Prediction id={self.id} student={self.student_name!r} marks={self.predicted_marks}>"
