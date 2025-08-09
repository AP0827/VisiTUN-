import { io, Socket } from 'socket.io-client';
import type { SocketEvents } from '../types';

class SocketService {
  private socket: Socket | null = null;
  private readonly url = 'http://localhost:5000';

  connect(): Socket {
    if (this.socket?.connected) {
      return this.socket;
    }

    this.socket = io(this.url, {
      transports: ['websocket', 'polling'],
      timeout: 20000,
    });

    this.socket.on('connect', () => {
      console.log('Connected to server');
    });

    this.socket.on('disconnect', () => {
      console.log('Disconnected from server');
    });

    this.socket.on('connect_error', (error) => {
      console.error('Connection error:', error);
    });

    return this.socket;
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  joinRoom(user_id: string): void {
    if (this.socket) {
      this.socket.emit('join', { user_id });
    }
  }

  leaveRoom(user_id: string): void {
    if (this.socket) {
      this.socket.emit('leave', { user_id });
    }
  }

  on<K extends keyof SocketEvents>(event: K, callback: SocketEvents[K]): void {
    if (this.socket) {
      this.socket.on(event, callback);
    }
  }

  off<K extends keyof SocketEvents>(event: K, callback?: SocketEvents[K]): void {
    if (this.socket) {
      this.socket.off(event, callback);
    }
  }

  emit(event: string, data: any): void {
    if (this.socket) {
      this.socket.emit(event, data);
    }
  }

  get connected(): boolean {
    return this.socket?.connected ?? false;
  }
}

export const socketService = new SocketService();