from flask import Flask, request, jsonify
app = Flask(__name__)
import random

questions = [
    {
        "id": 0,
        "text": "What is financial literacy?",
        "difficulty": 'e',
        "options": [
            "The ability to understand and use financial skills",
            "The study of literature about finance",
            "A type of bank account",
            "A financial certification program"
        ],
        "correct_answer": 0
    },
    {
        "id": 1,
        "text": "What does APR stand for in finance?",
        "difficulty": 'e',
        "options": [
            "Annual Payment Rate",
            "Annual Percentage Rate",
            "Average Price Ratio",
            "Automatic Payment Return"
        ],
        "correct_answer": 1
    },
    {
        "id": 2,
        "text": "What is a budget?",
        "difficulty": 'e',
        "options": [
            "A financial plan for income and expenses",
            "A type of savings account",
            "A credit card limit",
            "A loan repayment schedule"
        ],
        "correct_answer": 0
    },
    {
        "id": 3,
        "text": "What is compound interest?",
        "difficulty": 'm',
        "options": [
            "Interest calculated only on the principal",
            "Interest that decreases over time",
            "Interest calculated on principal plus accumulated interest",
            "A type of loan penalty"
        ],
        "correct_answer": 2
    },
    {
        "id": 4,
        "text": "What is a credit score used for?",
        "difficulty": 'e',
        "options": [
            "Measuring how much debt you have",
            "Evaluating creditworthiness for loans and credit",
            "Calculating your annual income",
            "Determining your tax bracket"
        ],
        "correct_answer": 1
    },
    {
        "id": 5,
        "text": "What is diversification in investing?",
        "difficulty": 'm',
        "options": [
            "Investing all money in one stock",
            "Spreading investments across different assets",
            "Only investing in foreign markets",
            "Selling all investments at once"
        ],
        "correct_answer": 1
    },
    {
        "id": 6,
        "text": "What is an emergency fund?",
        "difficulty": 'e',
        "options": [
            "Money saved for unexpected expenses",
            "A government assistance program",
            "A type of insurance policy",
            "A credit card for emergencies only"
        ],
        "correct_answer": 0
    },
    {
        "id": 7,
        "text": "What does it mean to live paycheck to paycheck?",
        "difficulty": 'e',
        "options": [
            "Getting paid twice a month",
            "Having no savings and spending all income before the next paycheck",
            "Receiving payments via check only",
            "Working two jobs simultaneously"
        ],
        "correct_answer": 1
    },
    {
        "id": 8,
        "text": "What is a 401(k)?",
        "difficulty": 'm',
        "options": [
            "A type of credit card",
            "A retirement savings plan sponsored by employers",
            "A government bond",
            "A student loan program"
        ],
        "correct_answer": 1
    },
    {
        "id": 9,
        "text": "What is inflation?",
        "difficulty": 'm',
        "options": [
            "The decrease in prices over time",
            "The increase in general price levels over time",
            "A type of investment return",
            "A banking fee"
        ],
        "correct_answer": 1
    },
    {
        "id": 10,
        "text": "What is the difference between a debit and credit card?",
        "difficulty": 'e',
        "options": [
            "No difference, they work the same way",
            "Debit uses your own money, credit borrows from the bank",
            "Credit cards are only for businesses",
            "Debit cards have higher interest rates"
        ],
        "correct_answer": 1
    },
    {
        "id": 11,
        "text": "What is equity in a home?",
        "difficulty": 'm',
        "options": [
            "The monthly mortgage payment",
            "The difference between home value and what you owe",
            "The interest rate on your mortgage",
            "The property tax amount"
        ],
        "correct_answer": 1
    },
    {
        "id": 12,
        "text": "What is a stock?",
        "difficulty": 'e',
        "options": [
            "A type of savings account",
            "Ownership share in a company",
            "A government issued bond",
            "A loan to a corporation"
        ],
        "correct_answer": 1
    },
    {
        "id": 13,
        "text": "What does ROI stand for?",
        "difficulty": 'm',
        "options": [
            "Rate of Income",
            "Return on Investment",
            "Risk of Inflation",
            "Revenue Operating Index"
        ],
        "correct_answer": 1
    },
    {
        "id": 14,
        "text": "What is a mutual fund?",
        "difficulty": 'm',
        "options": [
            "A bank savings account",
            "A pooled investment vehicle managed by professionals",
            "A type of insurance policy",
            "A personal loan program"
        ],
        "correct_answer": 1
    },
    {
        "id": 15,
        "text": "What is net worth?",
        "difficulty": 'm',
        "options": [
            "Your annual salary",
            "Total assets minus total liabilities",
            "The value of your home",
            "Your monthly income after taxes"
        ],
        "correct_answer": 1
    },
    {
        "id": 16,
        "text": "What is a tax deduction?",
        "difficulty": 'm',
        "options": [
            "A penalty for not paying taxes",
            "An expense that reduces taxable income",
            "A type of investment account",
            "A government refund program"
        ],
        "correct_answer": 1
    },
    {
        "id": 17,
        "text": "What does FICO score measure?",
        "difficulty": 'm',
        "options": [
            "Your income level",
            "Your credit risk and payment history",
            "Your investment portfolio size",
            "Your net worth"
        ],
        "correct_answer": 1
    },
    {
        "id": 18,
        "text": "What is liquidity in finance?",
        "difficulty": 'h',
        "options": [
            "How much debt you have",
            "How easily an asset can be converted to cash",
            "The interest rate on savings",
            "The total value of your investments"
        ],
        "correct_answer": 1
    },
    {
        "id": 19,
        "text": "What is dollar-cost averaging?",
        "difficulty": 'h',
        "options": [
            "Investing all money at once",
            "Investing fixed amounts at regular intervals",
            "Only buying stocks when prices are low",
            "Selling investments monthly"
        ],
        "correct_answer": 1
    },
    {
        "id": 20,
        "text": "What is the 50/30/20 budget rule?",
        "difficulty": 'm',
        "options": [
            "50% savings, 30% needs, 20% wants",
            "50% needs, 30% wants, 20% savings",
            "50% investments, 30% expenses, 20% cash",
            "50% rent, 30% food, 20% utilities"
        ],
        "correct_answer": 1
    }
]



def get_difficulty():
    easy = []
    medium =[]
    hard = []

    for question in questions:
        if question["difficulty"] == "e":
            easy.append(question)
    
    for question in questions:
        if question["difficulty"] == "m":
            medium.append(question)

    for question in questions:
        if question["difficulty"] == "h":
            hard.append(question)
    
    # easy = session.query(questions).filter_by(difficulty = 'e')
    # medium = session.query(questions).filter_by(difficulty = 'm')
    # hard = session.query(questions).filter_by(difficulty = 'h')

    # Experimental code to get easy, medium, and hard questions from the database
    selected_questions = []
    if easy:
        selected_questions.append(random.choice(easy))
    if medium:
        selected_questions.append(random.choice(medium))
    if hard:
        selected_questions.append(random.choice(hard))
    
    return selected_questions

@app.route('/questions', methods=['GET'])
def get_questions():
    daily_questions = get_difficulty()

    questions_list = []
    for question in daily_questions:
        questions_list.append({
            "id": question["id"],
            "text": question["text"],
            "difficulty": question["difficulty"],
            "options": question["options"],
            "correct_answer": question["correct_answer"]
        })
    
    return jsonify({
        "success": True,
        "questions": questions_list
    }), 200


# Maybe look into validating answers in the front end

@app.route('/answers', methods=['POST'])
def submit_answer():
    is_correct = False
    question_found = None
    data = request.get_json()
    # needs to get: {"user_id": "user123", "question_id": 5, "answer": 1}

    for question in questions:
        if question["id"] == data["question_id"]:
            question_found = question
            if question["correct_answer"] == data["answer"]:
                is_correct = True
                # update user trophy
            break
    
    if not question_found:
        return jsonify({
            "success": False,
            "error": "Question not found"
        }), 404
    
    return jsonify({
        "success": True,
        "is_correct": is_correct,
        "correct_answer": question_found["correct_answer"]
    }), 200

@app.route('/topten'm methods=['GET'])
def get_top_ten():
    # count = session.query(userData.userID).count()
    # users = select(userData).order_by(desc(userData.c.trophies))
    
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