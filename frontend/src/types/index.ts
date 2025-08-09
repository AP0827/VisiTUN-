export interface User {
  user_id: string;
  username: string;
  profile_picture?: string;
}

export interface Message {
  message_id: string;
  sender_id: string;
  receiver_id: string;
  message: string;
  sent_at: string;
}

export interface AuthStatus {
  authenticated: boolean;
  terminate: boolean;
}

export interface SocketEvents {
  connect: () => void;
  disconnect: () => void;
  auth_status: (data: { user_id: string; authenticated: boolean }) => void;
  new_message: (data: { 
    message_id: string; 
    sender_id: string; 
    receiver_id: string; 
    timestamp: string 
  }) => void;
  conversation_cleared: (data: { user1_id: string; user2_id: string }) => void;
  auth_terminated: (data: { user_id: string }) => void;
}