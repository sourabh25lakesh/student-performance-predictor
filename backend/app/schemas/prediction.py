from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PredictionCreate(BaseModel):
    student_name: str = Field(..., min_length=2, max_length=100, examples=["Aarav Sharma"])
    hours_studied: float = Field(..., ge=0, le=24, examples=[6.5])
    attendance: float = Field(..., ge=0, le=100, examples=[82.0])
    previous_marks: float = Field(..., ge=0, le=100, examples=[74.0])

    @field_validator("student_name")
    @classmethod
    def normalize_student_name(cls, value: str) -> str:
        value = " ".join(value.strip().split())
        if len(value) < 2:
            raise ValueError("Student name must contain at least 2 characters.")
        return value


class PredictionOut(BaseModel):
    id: int
    user_id: int
    student_name: str
    hours_studied: float
    attendance: float
    previous_marks: float
    predicted_marks: float
    grade: str
    status: str
    created_at: datetime
    is_deleted: bool
    deleted_at: datetime | None = None
    deleted_by: int | None = None

    model_config = ConfigDict(from_attributes=True)


class PredictionResult(BaseModel):
    prediction: PredictionOut
    message: str = "Prediction saved successfully."


class PredictionActionResult(BaseModel):
    message: str
    prediction: PredictionOut | None = None


class DashboardOut(BaseModel):
    total_predictions: int
    pass_count: int
    fail_count: int
    average_predicted_marks: float
    latest_predictions: list[PredictionOut]
