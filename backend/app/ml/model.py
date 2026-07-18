from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from app.core.config import settings

logger = logging.getLogger(__name__)

FEATURE_COLUMNS = ["hours_studied", "attendance", "previous_marks"]
TARGET_COLUMN = "final_marks"


def _backend_dir() -> Path:
    return Path(__file__).resolve().parents[2]


def _resolve_backend_path(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return (_backend_dir() / path).resolve()


def _resolve_dataset_path(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return (_backend_dir() / path).resolve()


def train_and_save_model() -> Pipeline:
    dataset_path = _resolve_dataset_path(settings.DATASET_PATH)
    model_path = _resolve_backend_path(settings.MODEL_PATH)

    if not dataset_path.exists():
        raise FileNotFoundError(f"Training dataset not found: {dataset_path}")

    data = pd.read_csv(dataset_path)
    missing_columns = set(FEATURE_COLUMNS + [TARGET_COLUMN]) - set(data.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Training dataset is missing required columns: {missing}")

    x = data[FEATURE_COLUMNS]
    y = data[TARGET_COLUMN]

    model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("regressor", LinearRegression()),
        ]
    )
    model.fit(x, y)

    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    logger.info("Trained Linear Regression model and saved it to %s", model_path)
    return model


@lru_cache(maxsize=1)
def load_model() -> Pipeline:
    model_path = _resolve_backend_path(settings.MODEL_PATH)
    if not model_path.exists():
        logger.warning("ML model not found at %s. Training a new model.", model_path)
        return train_and_save_model()

    logger.info("Loading ML model from %s", model_path)
    return joblib.load(model_path)


def predict_marks(hours_studied: float, attendance: float, previous_marks: float) -> float:
    model = load_model()
    features = pd.DataFrame(
        [
            {
                "hours_studied": hours_studied,
                "attendance": attendance,
                "previous_marks": previous_marks,
            }
        ],
        columns=FEATURE_COLUMNS,
    )
    prediction = float(model.predict(features)[0])
    return round(max(0.0, min(100.0, prediction)), 2)


def get_grade(marks: float) -> str:
    if marks >= 90:
        return "A+"
    if marks >= 80:
        return "A"
    if marks >= 70:
        return "B"
    if marks >= 60:
        return "C"
    if marks >= 50:
        return "D"
    return "F"


def get_pass_fail(marks: float) -> str:
    return "Pass" if marks >= settings.PASS_MARKS else "Fail"
