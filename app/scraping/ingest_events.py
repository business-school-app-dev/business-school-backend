import json
import uuid
from pathlib import Path
from datetime import datetime

# DEBUG prints to know if imports succeed
print("[DEBUG] Importing create_app...")
from app import create_app

print("[DEBUG] Importing Event model...")
from app.models import Event

# Path to events file
EVENTS_JSON_PATH = Path(__file__).resolve().parent / "events_enriched.json"
print(f"[DEBUG] JSON Path: {EVENTS_JSON_PATH}")


def parse_event_date(date_str: str):
    print(f"[DEBUG] Parsing date: {date_str}")
    return datetime.strptime(date_str, "%A, %B %d, %Y").date()


def load_events_from_json(app):
    print("[DEBUG] Creating DB session...")
    session = app.session  # get session from create_app()

    print("[DEBUG] Opening JSON file...")
    with EVENTS_JSON_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"[DEBUG] Loaded {len(data)} events from JSON")

    # 🔥 Optional: clear existing rows so each run replaces the table
    print("[DEBUG] Clearing existing events from DB...")
    session.query(Event).delete()

    try:
        for idx, item in enumerate(data):
            print(f"[DEBUG] Processing event #{idx + 1}: {item['title']}")

            # ❌ No longer using item["id"] from JSON
            # ✅ Generate a fresh UUID for the primary key
            event_id = uuid.uuid4()

            event_date = parse_event_date(item["date"])
            time_str = item.get("time")
            time_updated = datetime.fromisoformat(item["time_updated"])

            print(f"[DEBUG] Creating new event with generated id: {event_id}")
            new_event = Event(
                id=event_id,
                title=item["title"],
                date=event_date,
                time=time_str,
                description=item.get("description"),
                url=item["url"],
                time_updated=time_updated,
            )
            session.add(new_event)

        print("[DEBUG] Committing session...")
        session.commit()
        print("[DEBUG] SUCCESS: Events loaded into DB.")

    except Exception as e:
        print(f"[ERROR] Exception during DB insertion: {e}")
        session.rollback()
        raise

    finally:
        print("[DEBUG] Closing DB session...")
        session.close()


if __name__ == "__main__":
    print("[DEBUG] Calling create_app()...")
    app = create_app()

    # Show exactly which DB URL the engine is using
    print(f"[DEBUG] Engine URL: {app.engine.url}")

    print("[DEBUG] Entering app context...")
    with app.app_context():
        print("[DEBUG] Starting event ingestion...")
        load_events_from_json(app)
        print("[DEBUG] FINISHED ingestion.")
