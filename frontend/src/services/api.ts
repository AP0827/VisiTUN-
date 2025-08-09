const API_BASE_URL = 'http://localhost:5000';

export class ApiService {
  private static async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Network error' }));
      throw new Error(error.error || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Auth endpoints
  static async register(username: string, password: string) {
    return this.request('/user/register', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  }

  static async login(username: string, password: string) {
    return this.request('/user/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  }

  static async startFaceAuth(user_id: string, password: string) {
    return this.request('/auth/face/start', {
      method: 'POST',
      body: JSON.stringify({ user_id, password }),
    });
  }

  static async stopFaceAuth(user_id: string) {
    return this.request('/auth/face/stop', {
      method: 'POST',
      body: JSON.stringify({ user_id }),
    });
  }

  static async getAuthStatus(user_id: string) {
    return this.request(`/auth/status/${user_id}`, {
      method: 'GET',
    });
  }

  // Message endpoints
  static async sendMessage(sender_id: string, receiver_id: string, message: string) {
    return this.request('/chat/send', {
      method: 'POST',
      body: JSON.stringify({ sender_id, receiver_id, message }),
    });
  }

  static async getConversation(user1_id: string, user2_id: string, requesting_user: string) {
    return this.request(`/chat/conversation/${user1_id}/${user2_id}?user_id=${requesting_user}`, {
      method: 'GET',
    });
  }

  static async clearConversation(user1_id: string, user2_id: string, requesting_user: string) {
    return this.request(`/chat/clear/${user1_id}/${user2_id}?user_id=${requesting_user}`, {
      method: 'DELETE',
    });
  }
}