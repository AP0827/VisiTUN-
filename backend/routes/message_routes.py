from flask import Blueprint, jsonify, request, current_app
from models.message_model import MessageModel
from utils.encryption import encrypt, decrypt
from utils.face_auth import load_key, get_key_filename
import json

msg_bp = Blueprint('msg_bp', __name__)
message_model = MessageModel()

@msg_bp.route('/send', methods=['POST'])
def send_message():
    shared_state = current_app.config['shared_state']
    data = request.get_json()
    sender_id = data.get('sender_id')
    receiver_id = data.get('receiver_id') 
    plain_message = data.get('message')
    
    # Validate input
    if not all([sender_id, receiver_id, plain_message]):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Check if sender is authenticated
    if sender_id not in shared_state or not shared_state[sender_id].get("authenticated"):
        return jsonify({"error": "Sender not authenticated"}), 401
    
    try:
        # Get receiver's face key from their key file
        receiver_key_filename = get_key_filename(receiver_id)
        receiver_key = load_key(receiver_key_filename)
        
        if not receiver_key:
            return jsonify({"error": "Receiver's face key not found"}), 404
        
        # Encrypt message using receiver's face key
        encrypted_message, nonce, tag = encrypt(plain_message, receiver_key)
        
        # Store encrypted message in database
        message_id = message_model.create_message(
            sender_id, receiver_id, encrypted_message, nonce, tag
        )
        
        if not message_id:
            return jsonify({"error": "Failed to store message"}), 500
        
        # Emit real-time update via SocketIO
        from utils.face_auth import socketio
        socketio.emit('new_message', {
            'message_id': message_id,
            'sender_id': sender_id,
            'receiver_id': receiver_id,
            'timestamp': 'now'  # You can add proper timestamp
        }, room=receiver_id)
        
        return jsonify({
            "message_id": message_id, 
            "status": "sent"
        }), 201
        
    except Exception as e:
        print(f"Error sending message: {e}")
        return jsonify({"error": "Failed to send message"}), 500

@msg_bp.route('/conversation/<int:user1_id>/<int:user2_id>', methods=['GET'])
def get_conversation(user1_id, user2_id):
    shared_state = current_app.config['shared_state']
    
    # Check if requesting user is authenticated
    requesting_user = request.args.get('user_id')  # Add this to your frontend request
    if requesting_user not in shared_state or not shared_state[requesting_user].get("authenticated"):
        return jsonify({"error": "User not authenticated"}), 401
    
    try:
        # Get encrypted messages from database
        messages = message_model.get_messages_between_users(user1_id, user2_id)
        
        if not messages:
            return jsonify({"messages": []}), 200
        
        # Decrypt each message using sender's face key
        decrypted_messages = []
        for msg in messages:
            try:
                # Get sender's face key
                sender_key_filename = get_key_filename(msg['sender_id'])
                sender_key = load_key(sender_key_filename)
                
                if sender_key:
                    # Decrypt the message
                    decrypted_text = decrypt(
                        msg['tag'],
                        msg['message_text'],
                        msg['nonce'],
                        sender_key
                    )
                    
                    decrypted_messages.append({
                        'message_id': msg['message_id'],
                        'sender_id': msg['sender_id'],
                        'receiver_id': msg['receiver_id'],
                        'message': decrypted_text,
                        'sent_at': msg['sent_at']
                    })
                else:
                    # If sender's key not found, skip this message
                    continue
                    
            except Exception as e:
                print(f"Error decrypting message {msg['message_id']}: {e}")
                continue
        
        return jsonify({"messages": decrypted_messages}), 200
        
    except Exception as e:
        print(f"Error getting conversation: {e}")
        return jsonify({"error": "Failed to get conversation"}), 500

@msg_bp.route('/clear/<int:user1_id>/<int:user2_id>', methods=['DELETE'])
def clear_conversation(user1_id, user2_id):
    shared_state = current_app.config['shared_state']
    
    # Check if requesting user is authenticated
    requesting_user = request.args.get('user_id')  # Add this to your frontend request
    if requesting_user not in shared_state or not shared_state[requesting_user].get("authenticated"):
        return jsonify({"error": "User not authenticated"}), 401
    
    try:
        # Clear messages from database
        success = message_model.clear_messages_between_users(user1_id, user2_id)
        
        if success:
            # Emit clear event via SocketIO
            from utils.face_auth import socketio
            socketio.emit('conversation_cleared', {
                'user1_id': user1_id,
                'user2_id': user2_id
            }, room=user1_id)
            socketio.emit('conversation_cleared', {
                'user1_id': user1_id,
                'user2_id': user2_id
            }, room=user2_id)
            
            return jsonify({"status": "conversation cleared"}), 200
        else:
            return jsonify({"error": "Failed to clear conversation"}), 500
            
    except Exception as e:
        print(f"Error clearing conversation: {e}")
        return jsonify({"error": "Failed to clear conversation"}), 500