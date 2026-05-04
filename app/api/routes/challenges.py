from flask import Flask, request, jsonify, Blueprint, current_app
import logging
import sys
import random
from datetime import datetime, timezone, timedelta
import pytz
from sqlalchemy import func
from app.models import Questions, User, QuizScore

# Get logger - inherits from root logger configured in app/__init__.py
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Flask(__name__)
# challenges_bp = Blueprint("challenges", __name__, url_prefix="/challenges")
challenges_bp = Blueprint("challenges", __name__)

def get_difficulty():
    session = current_app.session
    easy = []
    medium =[]
    hard = []

    selected_questions = []
    selected_questions.append(session.query(Questions).filter_by(question_difficulty = 1).order_by(func.random()).first())
    selected_questions.append(session.query(Questions).filter_by(question_difficulty = 2).order_by(func.random()).first())
    selected_questions.append(session.query(Questions).filter_by(question_difficulty = 3).order_by(func.random()).first())
    

    return selected_questions

@challenges_bp.route('/challenges/can-play', methods=['GET'])
def can_play_quiz():
    """Check if user can play the quiz based on their last submission time."""
    logger.info("/challenges/can-play endpoint called")
    session = current_app.session
    username = request.args.get('username', '').strip()
    logger.info(f"Username: {username}")
    
    if not username:
        return jsonify({
            "success": True,
            "can_play": True,
            "message": "No username provided, can play"
        }), 200
    
    user = session.query(QuizScore).filter_by(username=username).one_or_none()
    
    if not user or not user.updated_at:
        return jsonify({
            "success": True,
            "can_play": True,
            "message": "First time playing"
        }), 200
    
    # Get current time in EST
    est = pytz.timezone('America/New_York')
    now_est = datetime.now(est)
    
    # Convert last submission time to EST
    last_submission = user.updated_at
    if last_submission.tzinfo is None:
        last_submission = pytz.utc.localize(last_submission)
    last_submission_est = last_submission.astimezone(est)
    
    # Calculate next midnight EST after last submission
    next_midnight = (last_submission_est + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    
    can_play = now_est >= next_midnight
    
    response = {
        "success": True,
        "can_play": can_play,
        "next_available": next_midnight.isoformat() if not can_play else None,
        "message": "You can play!" if can_play else f"Please wait until {next_midnight.strftime('%I:%M %p')} EST to play again."
    }
    logger.info(f"/challenges/can-play response: {response}")
    return jsonify(response), 200

@challenges_bp.route('/challenges/questions', methods=['GET'])
def get_questions():
    logger.info("/challenges/questions endpoint called")
    logger.info(f"Request headers: {dict(request.headers)}")
    
    try:
        daily_questions = get_difficulty()
        logger.info(f"Retrieved {len([q for q in daily_questions if q])} questions from database")
        
        questions_list = []
        
        for question in daily_questions:
            if question is not None:
                questions_list.append({
                    "id": question.id,
                    "text": question.question,
                    "difficulty": question.question_difficulty,
                    "options": question.question_choices,
                    "correct_answer": question.correct_answer,
                })
        
        logger.info(f"Returning {len(questions_list)} questions")
        response = {
            "success": True,
            "questions": questions_list
        }
        logger.info(f"Response: {response}")
        return jsonify(response), 200
    except Exception as e:
        logger.exception("Exception in /challenges/questions")
        return jsonify({"success": False, "error": str(e)}), 500

# batch submission
@challenges_bp.route('/challenges/submit-batch', methods=['POST'])
def submit_batch_answers():
    logger.info("/challenges/submit-batch endpoint called")
    session = current_app.session
    data = request.get_json()
    logger.info(f"Request data: {data}")
    
    # Check for required fields: username and answers array
    username = (data.get("username") or "").strip()
    user_answers = data.get("answers")
    logger.info(f"Username: {username}, Answers count: {len(user_answers) if user_answers else 0}")
    
    if not username or not user_answers:
        logger.info("Missing username or answers array")
        return jsonify({
            "success": False,
            "error": "Missing username or answers array"
        }), 400

    # Look up by username (not primary key) and create the row if it does not exist yet.
    user = session.query(QuizScore).filter_by(username=username).one_or_none()
    if not user:
        logger.info(f"Creating new user: {username}")
        user = QuizScore(username=username, score=0)
        session.add(user)
        session.flush()  # ensure we have an id before updating score

    total_trophies_gained = 0
    results = []
    num_correct = 0

    # 2. Process all answers in the batch sent by the mobile app
    for answer_data in user_answers:
        question_id = answer_data.get("questionId")
        submitted_answer = answer_data.get("answer")

        time_taken = answer_data.get("timeTaken")
        
        question = session.get(Questions, question_id)
        is_correct = False
        
        # Determine correctness and calculate trophies
        if question and question.correct_answer == submitted_answer:
            is_correct = True
            num_correct += 1
            
            # Map difficulty to trophies
            if question.question_difficulty == 1:
                trophies = 25
            elif question.question_difficulty == 2:
                trophies = 50
            elif question.question_difficulty == 3:
                trophies = 100
            else:
                trophies = 0 

            #calculates the new trophy amount based off of the time taken
            if time_taken is not None and time_taken > 0:
                multiplier = 0.9 ** time_taken
                if multiplier < 0.2:
                    multiplier = 0.2
                new_trophies = int(trophies * multiplier)
            else:
                new_trophies = trophies


            total_trophies_gained += new_trophies
        
        results.append({
            "question_id": question_id,
            "is_correct": is_correct
        })

    # 3. Update user trophies and commit ONCE
    user.score += total_trophies_gained
    session.commit()
    logger.info(f"User {username} score updated: +{total_trophies_gained} trophies, correct answers: {num_correct}")
    
    return jsonify({
        "success": True,
        "message": "Answers processed successfully.",
        "trophies_gained": total_trophies_gained,
        "results": results,
        "score" : num_correct
    }), 200

@challenges_bp.route('/topten', methods=['GET'])
def get_top_ten():
    logger.info("/topten endpoint called")
    session = current_app.session

    top_ten = session.query(QuizScore).order_by(QuizScore.score.desc()).limit(10).all()
    logger.info(f"Retrieved {len(top_ten)} users from leaderboard")

    users_list = [
            {
                "username": user.username,
                "score": user.score
            }
            for user in top_ten
        ]
    response = {
        "success": True,
        "users": users_list,
    }
    logger.info(f"/topten response: {response}")
    return jsonify(response), 200

@challenges_bp.route('/challenges/user-stats', methods=['GET'])
def get_user_stats():
    """Get a specific user's rank and score."""
    logger.info("/challenges/user-stats endpoint called")
    session = current_app.session
    username = request.args.get('username', '').strip()
    logger.info(f"Username: {username}")
    
    if not username:
        logger.info("No username provided")
        return jsonify({
            "success": False,
            "message": "Username is required"
        }), 400
    
    # Find the user
    user = session.query(QuizScore).filter_by(username=username).one_or_none()
    logger.info(f"User found: {user is not None}")
    
    if not user:
        logger.info(f"User '{username}' not found in database")
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404
    
    # Calculate rank by counting users with higher scores
    rank = session.query(func.count(QuizScore.id)).filter(
        QuizScore.score > user.score
    ).scalar() + 1
    logger.info(f"User rank: {rank}, score: {user.score}")
    
    response = {
        "success": True,
        "user": {
            "username": user.username,
            "score": user.score,
            "rank": rank
        }
    }
    logger.info(f"/challenges/user-stats response: {response}")
    return jsonify(response), 200
