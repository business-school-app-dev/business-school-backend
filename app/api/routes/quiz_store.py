from flask import Blueprint, jsonify, request, current_app
from sqlalchemy.exc import SQLAlchemyError

from app.models import QuizScore

quiz_store_bp = Blueprint("quiz", __name__)

BAD_USERNAMES = {"n/a", "na", "none", "-"}


@quiz_store_bp.route("/quiz/score", methods=["POST"])
def upsert_quiz_score():
    """
    Create or update a quiz score for a username.
    Expects JSON: {"username": "<name>", "score": <int>}
    """
    payload = request.get_json() or {}
    username = (payload.get("username") or "").strip()
    score = payload.get("score")

    if score is None:
        return (
            jsonify({"success": False, "error": "username and score are required"}),
            400,
        )

    # If the client chose not to provide a username (e.g., skip leaderboard), do nothing.
    if not username or username.lower() in BAD_USERNAMES:
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Score not recorded because no username was provided",
                }
            ),
            200,
        )

    try:
        # Ensure the table exists in case migrations haven't been run yet.
        QuizScore.__table__.create(current_app.engine, checkfirst=True)

        session = current_app.session
        existing = session.query(QuizScore).filter_by(username=username).one_or_none()

        if existing:
            existing.score = score
        else:
            session.add(QuizScore(username=username, score=score))

        session.commit()

        return jsonify(
            {
                "success": True,
                "username": username,
                "score": score,
                "message": "Score saved",
            }
        ), 200

    except SQLAlchemyError as exc:
        # Roll back to leave the session clean for the next request.
        current_app.session.rollback()
        return (
            jsonify({"success": False, "error": "Database error", "detail": str(exc)}),
            500,
        )
