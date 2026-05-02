# app/api/routes/health.py
from flask import Blueprint, jsonify, current_app

health_bp = Blueprint("health", __name__)

@health_bp.get("/health")
def health():
    return jsonify({"status": "ok"})


@health_bp.get("/health/db-status")
def db_status():
    """
    Diagnostic endpoint to check database connectivity and data population.
    Helps identify why quiz questions and events are not loading.
    """
    try:
        session = current_app.session
        
        from app.models import Questions, Event, QuizScore
        
        questions_count = session.query(Questions).count()
        events_count = session.query(Event).count()
        quiz_scores_count = session.query(QuizScore).count()
        
        return jsonify({
            "status": "ok",
            "database": "connected",
            "questions_loaded": questions_count > 0,
            "questions_count": questions_count,
            "events_loaded": events_count > 0,
            "events_count": events_count,
            "quiz_scores_count": quiz_scores_count,
            "message": "✅ All systems operational" if questions_count > 0 and events_count > 0 else "⚠️ Missing data - run seed scripts"
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "database": "connection_failed",
            "error": str(e),
            "message": "Database connection failed - check DATABASE_URL environment variable"
        }), 500
