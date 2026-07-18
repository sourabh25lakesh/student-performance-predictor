"""
SQLAlchemy database setup for MySQL.

Exposes:
- `engine`      : the SQLAlchemy engine connected to MySQL
- `SessionLocal`: a session factory for creating DB sessions
- `Base`        : the declarative base all ORM models inherit from
- `get_db`      : a FastAPI dependency that yields a DB session per request
"""

import logging

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

# `pool_pre_ping=True` avoids "MySQL server has gone away" errors on
# long-lived connections by checking liveness before use.
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


def get_db():
    """
    FastAPI dependency that provides a database session for the duration
    of a single request, and always closes it afterwards.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Create all database tables that don't already exist.

    Note: for a production-grade project you would typically use Alembic
    migrations instead of `create_all`. `create_all` is used here to keep
    setup simple and let the app "just run" after configuring the DB.
    """
    # Import models here so they are registered on Base.metadata
    # before create_all() is called.
    from app.models import prediction, user  # noqa: F401

    logger.info("Creating database tables (if they do not already exist)...")
    Base.metadata.create_all(bind=engine)
    _ensure_prediction_soft_delete_columns()
    logger.info("Database tables ready.")


def _ensure_prediction_soft_delete_columns() -> None:
    """
    Lightweight schema upgrade for existing local/demo databases.

    SQLAlchemy create_all() creates missing tables but does not alter existing
    tables. A production deployment should use Alembic migrations; this keeps
    the student project self-healing when the soft-delete feature is added.
    """
    inspector = inspect(engine)
    if "predictions" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("predictions")}
    dialect_name = engine.dialect.name

    if dialect_name == "mysql":
        statements = {
            "is_deleted": "ALTER TABLE predictions ADD COLUMN is_deleted BOOL NOT NULL DEFAULT FALSE",
            "deleted_at": "ALTER TABLE predictions ADD COLUMN deleted_at DATETIME NULL",
            "deleted_by": "ALTER TABLE predictions ADD COLUMN deleted_by INT NULL",
        }
        index_statement = (
            "CREATE INDEX idx_predictions_is_deleted ON predictions (is_deleted)"
        )
    else:
        statements = {
            "is_deleted": "ALTER TABLE predictions ADD COLUMN is_deleted BOOLEAN NOT NULL DEFAULT 0",
            "deleted_at": "ALTER TABLE predictions ADD COLUMN deleted_at DATETIME NULL",
            "deleted_by": "ALTER TABLE predictions ADD COLUMN deleted_by INTEGER NULL",
        }
        index_statement = (
            "CREATE INDEX IF NOT EXISTS idx_predictions_is_deleted ON predictions (is_deleted)"
        )

    with engine.begin() as connection:
        for column_name, statement in statements.items():
            if column_name not in existing_columns:
                logger.info("Adding missing predictions.%s column...", column_name)
                connection.execute(text(statement))

        if "is_deleted" not in existing_columns:
            connection.execute(text(index_statement))
