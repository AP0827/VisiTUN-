import React, { useState, useRef, useEffect } from 'react';
import { Send, Trash2, RefreshCw, User, Shield } from 'lucide-react';
import type { Message, User as UserType } from '../types';

interface ChatInterfaceProps {
  currentUser: UserType;
  otherUser: UserType;
  messages: Message[];
  onSendMessage: (message: string) => Promise<void>;
  onClearConversation: () => Promise<void>;
  onRefresh: () => Promise<void>;
  isLoading: boolean;
  error: string | null;
  isAuthenticated: boolean;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  currentUser,
  otherUser,
  messages,
  onSendMessage,
  onClearConversation,
  onRefresh,
  isLoading,
  error,
  isAuthenticated,
}) => {
  const [newMessage, setNewMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMessage.trim() || isSending || !isAuthenticated) return;

    setIsSending(true);
    try {
      await onSendMessage(newMessage.trim());
      setNewMessage('');
    } catch (err) {
      // Error handled by parent
    } finally {
      setIsSending(false);
    }
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className="card h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
            <User className="w-5 h-5 text-gray-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{otherUser.username}</h3>
            <p className="text-sm text-gray-500">Secure Chat</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
            title="Refresh messages"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
          
          <button
            onClick={onClearConversation}
            disabled={isLoading || !isAuthenticated}
            className="p-2 text-gray-400 hover:text-error-600 rounded-lg hover:bg-error-50 transition-colors"
            title="Clear conversation"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Authentication Warning */}
      {!isAuthenticated && (
        <div className="mt-4 p-3 bg-warning-50 border border-warning-200 rounded-lg flex items-center space-x-2">
          <Shield className="w-4 h-4 text-warning-600" />
          <span className="text-sm text-warning-700">
            Face authentication required to send messages
          </span>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto py-4 space-y-4 scrollbar-thin">
        {messages.length === 0 ? (
          <div className="text-center py-8">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Shield className="w-8 h-8 text-gray-400" />
            </div>
            <p className="text-gray-500">No messages yet</p>
            <p className="text-sm text-gray-400 mt-1">
              Start a secure conversation with {otherUser.username}
            </p>
          </div>
        ) : (
          messages.map((message) => {
            const isOwn = message.sender_id === currentUser.user_id;
            return (
              <div
                key={message.message_id}
                className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    isOwn
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-200 text-gray-900'
                  }`}
                >
                  <p className="text-sm">{message.message}</p>
                  <p
                    className={`text-xs mt-1 ${
                      isOwn ? 'text-primary-100' : 'text-gray-500'
                    }`}
                  >
                    {formatTime(message.sent_at)}
                  </p>
                </div>
              </div>
            );
          })
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-3 bg-error-50 border border-error-200 rounded-lg text-error-700 text-sm">
          {error}
        </div>
      )}

      {/* Message Input */}
      <form onSubmit={handleSendMessage} className="flex space-x-2 pt-4 border-t border-gray-200">
        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder={
            isAuthenticated 
              ? `Message ${otherUser.username}...` 
              : "Authenticate to send messages..."
          }
          className="input flex-1"
          disabled={isSending || !isAuthenticated}
        />
        <button
          type="submit"
          disabled={!newMessage.trim() || isSending || !isAuthenticated}
          className="btn-primary px-4"
        >
          {isSending ? (
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <Send className="w-4 h-4" />
          )}
        </button>
      </form>
    </div>
  );
};