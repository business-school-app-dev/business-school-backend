"""
Central seeding script to populate the database with:
- Questions from app/scripts/load_questions.py
- Events from scraping/<your_events_script>.py

Run with:
    python scripts/seed_db.py
"""

import sys
from pathlib import Path

# Make sure project root is on sys.path so `app` and `scraping` are importable
ROOT_DIR = Path(__file__).resolve().parents[1]  # project-root/
sys.path.append(str(ROOT_DIR))

# ---- Import seeding entrypoints from your existing scripts ----

# 1) Questions loader (you already have this with main())
from app.scripts.load_questions_from_csv import main as load_questions

# 2) Events loader: adjust this import to match your actual filename
#    For example, if your file is scraping/load_events_from_json.py
#    and it has a `main()` at the bottom, do:
#       from scraping.load_events_from_json import main as load_events_main
from app.scraping.ingest_events import main as load_events_from_json  # <-- change name if needed


def main():
    print("=== DB SEED START ===")

    # Load questions from questions.csv
    print("\n[1/2] Seeding questions from CSV...")
    load_questions()
    print("[1/2] ✅ Questions seeding complete.")

    # Load events from events_enriched.json
    print("\n[2/2] Seeding events from JSON...")
    load_events_from_json()
    print("[2/2] ✅ Events seeding complete.")

    print("\n=== DB SEED FINISHED SUCCESSFULLY ===")


if __name__ == "__main__":
    main()
