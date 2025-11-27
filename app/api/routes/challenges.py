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

# batch submission
@challenges_bp.route('/challenges/submit-batch', methods=['POST'])
def submit_batch_answers():
    session = current_app.session
    data = request.get_json()
    
    # Check for required fields: user_id (expected to be the numeric ID) and answers array
    user_id = data.get("user_id")
    user_answers = data.get("answers")
    
    if user_id is None or not user_answers:
        return jsonify({
            "success": False,
            "error": "Missing user_id or answers array"
        }), 400

    user = session.get(User, user_id)
    if not user:
        return jsonify({
            "success": False,
            "error": f"User with ID {user_id} not found."
        }), 404

    total_trophies_gained = 0
    results = []

    # 2. Process all answers in the batch sent by the mobile app
    for answer_data in user_answers:
        question_id = answer_data.get("questionId")
        submitted_answer = answer_data.get("answer")
        
        question = session.get(Questions, question_id)
        is_correct = False
        
        # Determine correctness and calculate trophies
        if question and question.correct_answer == submitted_answer:
            is_correct = True
            
            # Map difficulty to trophies
            if question.question_difficulty == 1:
                trophies = 5
            elif question.question_difficulty == 2:
                trophies = 10
            elif question.question_difficulty == 3:
                trophies = 20
            else:
                trophies = 0 
                
            total_trophies_gained += trophies
        
        results.append({
            "question_id": question_id,
            "is_correct": is_correct
        })

    # 3. Update user trophies and commit ONCE
    user.trophies += total_trophies_gained
    session.commit()
    
    return jsonify({
        "success": True,
        "message": "Answers processed successfully.",
        "trophies_gained": total_trophies_gained,
        "results": results
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