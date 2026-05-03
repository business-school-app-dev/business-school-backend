# app/api/routes/scraping_events.py

import json
from pathlib import Path
from datetime import datetime, timedelta, timezone, date

from flask import Blueprint, jsonify, request, current_app
from app.models import Event  # <-- IMPORTANT: import Event model

scraping_events_bp = Blueprint("scraping_events", __name__)

# (you can keep ROOT_DIR, EVENTS_JSON_PATH, _load_events, _parse_event_date;
# they are no longer used for this endpoint but do not break anything)


@scraping_events_bp.route("/scraping/events", methods=["GET"])
def get_scraping_events():
    """
    GET /api/v1/scraping/events?days=N

    NOW READS FROM POSTGRESQL DATABASE.
    """

    days = request.args.get("days", default=60, type=int)
    if days is None or days <= 0:
        days = 60

    today = datetime.now(timezone.utc).date()
    end_date = today + timedelta(days=days)

    # Get DB session from the Flask app (same session used in ingestion script)
    session = current_app.session

    # --- QUERY POSTGRES ---
    db_events = (
        session.query(Event)
        .filter(Event.date >= today, Event.date <= end_date)
        .order_by(Event.date.asc(), Event.time.asc())
        .all()
    )

    # --- PRINT FIRST 5 EVENTS TO TERMINAL ---
    print("\n====== DEBUG: FIRST 5 EVENTS FROM POSTGRESQL ======")
    for e in db_events[:5]:
        print(
            f"Title: {e.title} | Date: {e.date} | Time: {e.time} | URL: {e.url}"
        )
    print("===================================================\n")

    # --- FORMAT RESPONSE ---
    result = []
    for e in db_events:
        result.append({
            "title": e.title,
            # Convert date back to readable string like the original JSON
            "date": e.date.strftime("%A, %B %d, %Y") if isinstance(e.date, date) else str(e.date),
            "time": e.time,
            "description": e.description,
            "url": e.url,
        })

    return jsonify(result), 200
