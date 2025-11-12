from flask import Flask, request, jsonify, Blueprint, current_app
app = Flask(__name__)
import random
from sqlalchemy import func
from app.models import Questions, User

challenges_bp = Blueprint("challenges", __name__, url_prefix="/challenges")



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

@challenges_bp.route('/questions', methods=['GET'])
def get_questions():
    daily_questions = get_difficulty()

    
    questions_list = []
    
    for question in daily_questions:
        questions_list.append({
            "id": question.id,
            "text": question.question,
            "difficulty": question.question_difficulty,
            "options": question.question_choices,
        })
    
    return jsonify({
        "success": True,
        "questions": questions_list
    }), 200



@challenges_bp.route('/answers', methods=['POST'])
def submit_answer():
    session = current_app.session
    is_correct = False
    question_found = None
    data = request.get_json()
    # needs to get: {"user_id": "user123", "question_id": 5, "answer": 1}

    question = session.get(Questions, data["question_id"])
    if not question:
        return jsonify({
            "success": False,
            "error": "Question not found"
        }), 404
    if question.correct_answer == data["answer"]:
        is_correct = True
        if not add_trophies(data["user_id"], question.question_difficulty):
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404
    
    return jsonify({
        "success": True,
        "is_correct": is_correct,
        
    }), 200
def add_trophies(user_id, question_difficulty):
    session = current_app.session

    user = session.get(User, user_id)
    if not user:
        return False

    if question_difficulty == 1:
        user.trophies += 5
    elif question_difficulty == 2:
        user.trophies += 10
    elif question_difficulty == 3:
        user.trophies += 20
    
    session.commit()
    
    return True
    

@challenges_bp.route('/topten', methods=['GET'])
def get_top_ten():
    session = current_app.session

    top_ten = session.query(User).order_by(User.trophies.desc()).limit(10).all()

    users_list = [
            {
                "id": user.id,
                "username": user.username,
                "trophies": user.trophies
            }
            for user in top_ten
        ]
    return jsonify({
        "success": True,
        "users": users_list,
    }), 200


'''



@app.route('/topten'm methods=['GET'])
def get_top_ten():
    count = session.query(userData.userID).count()
    users = select(userData).order_by(desc(userData.c.trophies))
    
    # Experimental code to get the top 10 users from the database using sql alchemy
    if(count < 10) {
        top_users = users[0:count]
    } else {
        top_users = users[:10]
    }

    return jsonify({
        "success": True,
        "user_list": top_users
    })
'''