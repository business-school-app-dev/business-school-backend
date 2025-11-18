# app/config.py
import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    USE_CELERY: str = os.getenv("USE_CELERY")
    PARAMETER_SET_KEY: str = os.getenv("PARAMETER_SET_KEY")
