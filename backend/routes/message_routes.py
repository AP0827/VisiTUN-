from flask import Flask, Blueprint, jsonify, request, current_app
from models.message_model import MessageModel
from utils.encryption import encrypt,decrypt

msg_bp = Blueprint('msg_bp', __name__)
message_model = MessageModel()

msg_bp.route('/send', methods=["POST"])
def send_message():
    data = request.get_json()
    message = data["message_text"]
    sender = data["sender_id"]
    receiver = data["receiver_id"]


    
