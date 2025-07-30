from flask import Flask, Blueprint, jsonify, request, current_app
from models.user_model import UserModel

user_bp = Blueprint('user_bp',__name__)
user_model = UserModel()

user_bp.route('/register', methods=["POST"])
def register_user():
    shared_state = current_app.config['shared_state']
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "Missing Username/Password"})
    
    userID = user_model.create_user(username,password)
    if userID is None:
        return jsonify({"error":"Username already exists"}), 409
    shared_state[userID] = {
        "aes_key" : None,
        "terminate" : False,
        "authenticate" : False
    }
    return jsonify({"userID" : f"{userID}", "username":f"{username}"})

user_bp.route('/login', methods=["POST"])
def user_login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = user_model.authenticate_user(username, password)
    if user is None:
        return jsonify({"error":"Invalid Credentials"}), 401
    return jsonify(user), 200


