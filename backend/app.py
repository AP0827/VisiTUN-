from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
import threading
from threading import Lock, Thread
from utils.face_auth import cam_video, authenticate_face
from utils import face_auth

from routes.auth_routes import auth_bp
from routes.socketio_events import register_socket_event


app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'super-secret'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

app.register_blueprint(auth_bp, url_prefix='/auth')
register_socket_event(socketio, face_auth.auth_lock, face_auth.shared_state, face_auth.auth_lock)

face_auth.socketio = socketio



