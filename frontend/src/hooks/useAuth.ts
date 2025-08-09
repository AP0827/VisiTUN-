import { useState, useEffect, useCallback } from 'react';
import { ApiService } from '../services/api';
import { socketService } from '../services/socket';
import type { User, AuthStatus } from '../types';

export const useAuth = () => {
  const [user, setUser] = useState<User | null>(null);
  const [authStatus, setAuthStatus] = useState<AuthStatus>({ 
    authenticated: false, 
    terminate: false 
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const login = useCallback(async (username: string, password: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const userData = await ApiService.login(username, password);
      setUser(userData);
      
      // Connect to socket and join user's room
      socketService.connect();
      socketService.joinRoom(userData.user_id);
      
      return userData;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Login failed';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const register = useCallback(async (username: string, password: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const userData = await ApiService.register(username, password);
      return userData;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Registration failed';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const startFaceAuth = useCallback(async (password: string) => {
    if (!user) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      await ApiService.startFaceAuth(user.user_id, password);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Face auth failed to start';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [user]);

  const stopFaceAuth = useCallback(async () => {
    if (!user) return;
    
    try {
      await ApiService.stopFaceAuth(user.user_id);
      setAuthStatus({ authenticated: false, terminate: true });
    } catch (err) {
      console.error('Failed to stop face auth:', err);
    }
  }, [user]);

  const logout = useCallback(() => {
    if (user) {
      socketService.leaveRoom(user.user_id);
      socketService.disconnect();
      stopFaceAuth();
    }
    setUser(null);
    setAuthStatus({ authenticated: false, terminate: false });
    setError(null);
  }, [user, stopFaceAuth]);

  // Listen for auth status updates via socket
  useEffect(() => {
    if (!user) return;

    const handleAuthStatus = (data: { user_id: string; authenticated: boolean }) => {
      if (data.user_id === user.user_id) {
        setAuthStatus(prev => ({ ...prev, authenticated: data.authenticated }));
      }
    };

    const handleAuthTerminated = (data: { user_id: string }) => {
      if (data.user_id === user.user_id) {
        setAuthStatus({ authenticated: false, terminate: true });
      }
    };

    socketService.on('auth_status', handleAuthStatus);
    socketService.on('auth_terminated', handleAuthTerminated);

    return () => {
      socketService.off('auth_status', handleAuthStatus);
      socketService.off('auth_terminated', handleAuthTerminated);
    };
  }, [user]);

  return {
    user,
    authStatus,
    isLoading,
    error,
    login,
    register,
    startFaceAuth,
    stopFaceAuth,
    logout,
    clearError: () => setError(null),
  };
};