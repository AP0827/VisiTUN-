from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
import threading
from utils import face_auth

from routes.auth_routes import auth_bp
from routes.message_routes import msg_bp
from routes.user_routes import user_bp
from routes.socketio_events import register_socket_event

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'super-secret'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Set socketio reference in face_auth module
face_auth.socketio = socketio

# Global shared state for all users
shared_state = {}
app.config['shared_state'] = shared_state

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(msg_bp, url_prefix='/chat')
app.register_blueprint(user_bp, url_prefix='/user')

# Register socketio events with proper shared state
register_socket_event(socketio, face_auth.auth_lock, shared_state)

@app.route('/')
def root():
    """Root endpoint for testing"""
    return jsonify({
        "message": "VisiTUN Backend is running!",
        "endpoints": {
            "auth": "/auth",
            "users": "/user", 
            "chat": "/chat"
        }
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "VisiTUN backend is operational"})

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)



