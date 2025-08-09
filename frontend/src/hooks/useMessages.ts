import { useState, useEffect, useCallback } from 'react';
import { ApiService } from '../services/api';
import { socketService } from '../services/socket';
import type { Message, User } from '../types';

export const useMessages = (currentUser: User | null, otherUser: User | null) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadMessages = useCallback(async () => {
    if (!currentUser || !otherUser) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await ApiService.getConversation(
        currentUser.user_id,
        otherUser.user_id,
        currentUser.user_id
      );
      setMessages(response.messages || []);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load messages';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [currentUser, otherUser]);

  const sendMessage = useCallback(async (messageText: string) => {
    if (!currentUser || !otherUser || !messageText.trim()) return;
    
    try {
      await ApiService.sendMessage(currentUser.user_id, otherUser.user_id, messageText);
      // Message will be added via socket event
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);
      throw err;
    }
  }, [currentUser, otherUser]);

  const clearConversation = useCallback(async () => {
    if (!currentUser || !otherUser) return;
    
    try {
      await ApiService.clearConversation(
        currentUser.user_id,
        otherUser.user_id,
        currentUser.user_id
      );
      // Messages will be cleared via socket event
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to clear conversation';
      setError(errorMessage);
      throw err;
    }
  }, [currentUser, otherUser]);

  // Listen for new messages and conversation events
  useEffect(() => {
    if (!currentUser || !otherUser) return;

    const handleNewMessage = (data: { 
      message_id: string; 
      sender_id: string; 
      receiver_id: string; 
      timestamp: string 
    }) => {
      // Reload messages when a new message is received
      if (data.sender_id === otherUser.user_id || data.receiver_id === otherUser.user_id) {
        loadMessages();
      }
    };

    const handleConversationCleared = (data: { user1_id: string; user2_id: string }) => {
      if ((data.user1_id === currentUser.user_id && data.user2_id === otherUser.user_id) ||
          (data.user1_id === otherUser.user_id && data.user2_id === currentUser.user_id)) {
        setMessages([]);
      }
    };

    socketService.on('new_message', handleNewMessage);
    socketService.on('conversation_cleared', handleConversationCleared);

    return () => {
      socketService.off('new_message', handleNewMessage);
      socketService.off('conversation_cleared', handleConversationCleared);
    };
  }, [currentUser, otherUser, loadMessages]);

  // Load messages when users change
  useEffect(() => {
    loadMessages();
  }, [loadMessages]);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearConversation,
    refreshMessages: loadMessages,
    clearError: () => setError(null),
  };
};