import os
import csv
import json

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.models import Questions  # adjust if your model class is named differently


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://fwc_user:fwc_pass@localhost:5433/fwc_db",
)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # .../app
CSV_PATH = os.path.join(BASE_DIR, "questions.csv")

print(">>> Using DATABASE_URL:", DATABASE_URL)
print(">>> CSV path:", CSV_PATH, "exists?", os.path.exists(CSV_PATH))

engine = create_engine(DATABASE_URL, future=True)


def load_questions(engine=None):
    if engine is None:
        engine = create_engine(DATABASE_URL, future=True)
    with Session(engine) as session:
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            print(">>> Number of rows read from CSV:", len(rows))

            if rows:
                print(">>> First row from CSV:", rows[0])

            inserted = 0
            for i, row in enumerate(rows, start=1):
                try:
                    q = Questions(
                        # ⚠️ If id is autoincrement in DB, comment this out:
                        # id=int(row["id"]),
                        question_difficulty=int(row["question_difficulty"]),
                        question=row["question"],
                        # If question_choices is JSON like '["A","B","C"]':
                        question_choices=json.loads(row["question_choices"]),
                        correct_answer=int(row["correct_answer"]),
                    )
                    session.add(q)
                    inserted += 1
                except Exception as e:
                    print(f"!!! Error on row {i}: {e}")
                    # optionally: print(row)

        session.commit()
        print(">>> Rows attempted to insert:", inserted)

        # Double-check using ORM
        total_orm = session.query(Questions).count()
        print(">>> Total rows in Questions table (SQLAlchemy):", total_orm)

        # Double-check using raw SQL
        result = session.execute(text("SELECT COUNT(*) FROM questions"))
        total_sql = result.scalar_one()
        print(">>> Total rows in questions (raw SQL):", total_sql)


if __name__ == "__main__":
    load_questions()
