import time
from threading import Thread
from flask_socketio import emit

def register_socket_event(socketio, auth_lock, shared_state):
    """Register basic SocketIO event handlers"""
    
    @socketio.on('connect')
    def handle_connect():
        print('Client connected')
        emit('connected', {'status': 'connected'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')
    
    @socketio.on('join')
    def handle_join(data):
        """Join a user to their room for private messages"""
        user_id = data.get('user_id')
        if user_id:
            from flask_socketio import join_room
            join_room(user_id)
            print(f'User {user_id} joined their room')
            emit('joined', {'user_id': user_id, 'status': 'joined'})
    
    @socketio.on('leave')
    def handle_leave(data):
        """Leave a user's room"""
        user_id = data.get('user_id')
        if user_id:
            from flask_socketio import leave_room
            leave_room(user_id)
            print(f'User {user_id} left their room')
            emit('left', {'user_id': user_id, 'status': 'left'})

