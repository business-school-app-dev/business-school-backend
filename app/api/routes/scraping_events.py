# app/api/routes/scraping_events.py

import json
import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone, date

from flask import Blueprint, jsonify, request, current_app
from app.models import Event  # <-- IMPORTANT: import Event model

# Get logger - inherits from root logger configured in app/__init__.py
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

scraping_events_bp = Blueprint("scraping_events", __name__)

# (you can keep ROOT_DIR, EVENTS_JSON_PATH, _load_events, _parse_event_date;
# they are no longer used for this endpoint but do not break anything)


@scraping_events_bp.route("/scraping/events", methods=["GET"])
def get_scraping_events():
    """
    GET /api/v1/scraping/events?days=N

    NOW READS FROM POSTGRESQL DATABASE.
    """
    logger.info("/scraping/events endpoint called")
    logger.info(f"Request headers: {dict(request.headers)}")

    try:
        days = request.args.get("days", default=60, type=int)
        logger.info(f"Days parameter: {days}")
        
        if days is None or days <= 0:
            days = 60
            logger.info(f"Days adjusted to: {days}")

        today = datetime.now(timezone.utc).date()
        end_date = today + timedelta(days=days)
        logger.info(f"Date range: {today} to {end_date}")

        # Get DB session from the Flask app (same session used in ingestion script)
        session = current_app.session

        # --- QUERY POSTGRES ---
        db_events = (
            session.query(Event)
            .filter(Event.date >= today, Event.date <= end_date)
            .order_by(Event.date.asc(), Event.time.asc())
            .all()
        )
        logger.info(f"Retrieved {len(db_events)} events from database")

        # --- PRINT FIRST 5 EVENTS TO TERMINAL ---
        logger.info("====== FIRST 5 EVENTS FROM POSTGRESQL ======")
        for e in db_events[:5]:
            logger.info(f"Title: {e.title} | Date: {e.date} | Time: {e.time} | URL: {e.url}")
        logger.info("==============================================")

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

        logger.info(f"Returning {len(result)} formatted events")
        if result:
            logger.info(f"Response sample: {result[0]}")
        return jsonify(result), 200
    
    except Exception as e:
        logger.exception("Exception in /scraping/events")
        return jsonify({"error": str(e)}), 500
