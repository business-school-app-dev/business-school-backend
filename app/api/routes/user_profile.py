from flask import Flask, request
app = Flask(__name__)
id = 2
users = [
    {
        "id" : 0,
        "name" : "Name1",
        "username" : "username1",
        "email" : "email@umd.edu",
        "trophies" : 0,
        "retirement age" : 60,
        "employment age" : 23,
        "career name" : "software engineer",
    },
    {
        "id" : 1,
        "name" : "Name2",
        "username" : "username2",
        "email" : "email@umd.edu",
        "trophies" : 1,
        "retirement age" : 64,
        "employment age" : 23,
        "career name" : "software engineer",
    },
    {
        "id" : 2,
        "name" : "Name3",
        "username" : "username3",
        "email" : "email@umd.edu",
        "trophies" : 0,
        "retirement age" : 60,
        "employment age" : 23,
        "career name" : "software engineer",
    },

]
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = None # need a sql alchemy connection here to fetch a user
    for u in users: 
        if (user["id"] == id):
            user = u
    if not user:
        return jsonify({"error": "User does not exist"}), 404
    return jsonify(user) # assuming the sql connection comes back as a user object

@app.route('/users/', methods=['POST'])
def create_user():
    username = request.args.get('username')
    email = request.args.get('email') # will likely have some sort of random generation for this
    name = request.args.get('name')
    trophies = 0
    retirement_age = request.args.get('retirement_age')
    employment_age = request.args.get('employment_age')
    career_name = request.args.get('career_name')
    id+= 1
    user = {
        "id" : id,
        "name" : name,
        "username" : username,
        "email" : email,
        "trophies" : 0,
        "retirement age" :retirement_age,
        "employment age" : employment_age,
        "career name" : career_name,
    }
    users.append(user)
    return jsonify({"message" : "Successful addition"}), 200


