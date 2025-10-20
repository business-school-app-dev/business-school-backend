from flask import Flask, request
app = Flask(__name__)
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):