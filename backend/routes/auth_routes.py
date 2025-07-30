from flask import Flask, Blueprint, jsonify, request, current_app
from threading import Lock, Thread
from utils.face_auth import authenticate_face, socketio

auth_lock = Lock()

auth_bp = Blueprint('auth_bp', __name__)
@auth_bp.route('/face/start', methods=["POST"])
def start_auth():
    shared_state = current_app.config['shared_state']
    data = request.get_json()
    password = data.get("password")
    user_id = data.get("user_id")

    if not user_id or not password :
        return jsonify({"error":"Missing password or user_id"})
    
    if user_id not in shared_state :
        with auth_lock:
            shared_state[user_id] = {
                "aes_key": None,
                "authenticated": False,
                "terminate": False
            }
    thread = Thread(target=authenticate_face, args=(shared_state[user_id],password,user_id), daemon=True)
    thread.start()

    return jsonify({"message":"Auth Thread started."}),200

@auth_bp.route('/face/stop', methods=["POST"])
def stop_auth():
    shared_state = current_app.config['shared_state']
    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id or user_id not in shared_state:
        return jsonify({"error":"Invalid user_id"}), 400
    
    with auth_lock:
        shared_state[user_id]["terminate"] = True
        shared_state.pop(user_id, None)
    return jsonify({"message":"Auth thread stopped"}), 200

@auth_bp.route('/status/<user_id>', methods=["POST"])
def check_auth():
    shared_status = current_app.config['shared_status']
    user_id = data.get("user_id")
    return jsonify({"status" : f"{shared_state[user_id]["terminate"]}"})
