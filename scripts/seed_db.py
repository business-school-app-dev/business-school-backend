"""
Central seeding script to populate the database with:
- Questions from app/scripts/load_questions_from_csv.py
- Events from app/scraping/ingest_events.py

Run with:
    python scripts/seed_db.py
"""

import sys
from pathlib import Path

# scripts/seed_db.py -> parent is .../src
CURRENT_DIR = Path(__file__).resolve().parent        # .../src/scripts
PROJECT_ROOT = CURRENT_DIR.parent                    # .../src

# Make sure project root is on sys.path so `import app` works
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ---- Now these imports will see the `app` package ----
from app import create_app
from app.scripts.load_questions_from_csv import load_questions
from app.scraping.ingest_events import load_events_from_json


def main():
    print("=== DB SEED START ===")

    # 1) Seed questions
    print("\n[1/2] Seeding questions from CSV...")
    load_questions()
    print("[1/2] ✅ Questions seeding complete.")

    # 2) Seed events
    print("\n[2/2] Seeding events from JSON...")

    app = create_app()

    # optional debug to see which DB you're hitting
    try:
        print(f"[DEBUG] Engine URL: {app.engine.url}")
    except Exception:
        pass

    # if load_events_from_json uses app.app_context() internally, this is fine:
    load_events_from_json(app)

    print("[2/2] ✅ Events seeding complete.")
    print("\n=== DB SEED FINISHED SUCCESSFULLY ===")


if __name__ == "__main__":
    main()
