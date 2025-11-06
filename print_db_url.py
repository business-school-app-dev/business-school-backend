import os

DEFAULT_URL = "postgresql+psycopg://fwc_user:fwc_pass@localhost:5433/fwc_db"

db_url = os.getenv("DATABASE_URL", DEFAULT_URL)

print("DATABASE_URL env var:", os.getenv("DATABASE_URL"))
print("Effective URL Alembic should use:", db_url)