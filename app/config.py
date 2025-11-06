# app/config.py
import os
from pydantic import BaseModel

class Settings(BaseModel):
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://fwc_user:fwc_pass@localhost:5432/fwc_db",
    )
    USE_CELERY: str = os.getenv("USE_CELERY", "0")
    PARAMETER_SET_KEY: str = os.getenv("PARAMETER_SET_KEY", "baseline_2026")
