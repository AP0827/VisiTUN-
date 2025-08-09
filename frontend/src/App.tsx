import React, { useState } from 'react';
import { LogOut, Shield, MessageCircle } from 'lucide-react';
import { AuthForm } from './components/AuthForm';
import { FaceAuthPanel } from './components/FaceAuthPanel';
import { ChatInterface } from './components/ChatInterface';
import { UserSelector } from './components/UserSelector';
import { useAuth } from './hooks/useAuth';
import { useMessages } from './hooks/useMessages';
import type { User } from './types';

function App() {
  const {
    user,
    authStatus,
    isLoading: authLoading,
    error: authError,
    login,
    register,
    startFaceAuth,
    stopFaceAuth,
    logout,
    clearError: clearAuthError,
  } = useAuth();

  const [selectedUser, setSelectedUser] = useState<User | null>(null);

  const {
    messages,
    isLoading: messagesLoading,
    error: messagesError,
    sendMessage,
    clearConversation,
    refreshMessages,
    clearError: clearMessagesError,
  } = useMessages(user, selectedUser);

  // Clear errors when they change
  React.useEffect(() => {
    if (authError) {
      const timer = setTimeout(clearAuthError, 5000);
      return () => clearTimeout(timer);
    }
  }, [authError, clearAuthError]);

  React.useEffect(() => {
    if (messagesError) {
      const timer = setTimeout(clearMessagesError, 5000);
      return () => clearTimeout(timer);
    }
  }, [messagesError, clearMessagesError]);

  if (!user) {
    return (
      <AuthForm
        onLogin={login}
        onRegister={register}
        isLoading={authLoading}
        error={authError}
      />
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900">VisiTUN</h1>
              <p className="text-sm text-gray-500">Secure Communication</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                <span className="text-sm font-medium text-gray-600">
                  {user.username.charAt(0).toUpperCase()}
                </span>
              </div>
              <span className="text-sm font-medium text-gray-700">{user.username}</span>
            </div>
            
            <button
              onClick={logout}
              className="p-2 text-gray-400 hover:text-error-600 rounded-lg hover:bg-error-50 transition-colors"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto p-4">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-120px)]">
          {/* Left Panel - Auth & User Selection */}
          <div className="space-y-6">
            <FaceAuthPanel
              authStatus={authStatus}
              onStartAuth={startFaceAuth}
              onStopAuth={stopFaceAuth}
              isLoading={authLoading}
              error={authError}
            />
            
            <UserSelector
              currentUser={user}
              selectedUser={selectedUser}
              onUserSelect={setSelectedUser}
            />
          </div>

          {/* Right Panel - Chat Interface */}
          <div className="lg:col-span-2">
            {selectedUser ? (
              <ChatInterface
                currentUser={user}
                otherUser={selectedUser}
                messages={messages}
                onSendMessage={sendMessage}
                onClearConversation={clearConversation}
                onRefresh={refreshMessages}
                isLoading={messagesLoading}
                error={messagesError}
                isAuthenticated={authStatus.authenticated}
              />
            ) : (
              <div className="card h-full flex items-center justify-center">
                <div className="text-center">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <MessageCircle className="w-8 h-8 text-gray-400" />
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Select a Chat Partner
                  </h3>
                  <p className="text-gray-500 max-w-sm">
                    Choose someone to start a secure, face-authenticated conversation with.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;