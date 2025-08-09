import React, { useState } from 'react';
import { Users, Plus, User } from 'lucide-react';
import type { User as UserType } from '../types';

interface UserSelectorProps {
  currentUser: UserType;
  selectedUser: UserType | null;
  onUserSelect: (user: UserType) => void;
}

export const UserSelector: React.FC<UserSelectorProps> = ({
  currentUser,
  selectedUser,
  onUserSelect,
}) => {
  const [customUserId, setCustomUserId] = useState('');
  const [customUsername, setCustomUsername] = useState('');
  const [showCustomForm, setShowCustomForm] = useState(false);

  // For demo purposes, we'll allow manual user creation
  // In a real app, you'd fetch users from an API
  const handleAddCustomUser = () => {
    if (!customUserId.trim() || !customUsername.trim()) return;
    
    const newUser: UserType = {
      user_id: customUserId.trim(),
      username: customUsername.trim(),
    };
    
    onUserSelect(newUser);
    setCustomUserId('');
    setCustomUsername('');
    setShowCustomForm(false);
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
            <Users className="w-5 h-5 text-primary-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">Chat Partner</h3>
            <p className="text-sm text-gray-500">Select who to chat with</p>
          </div>
        </div>
        
        <button
          onClick={() => setShowCustomForm(!showCustomForm)}
          className="p-2 text-gray-400 hover:text-primary-600 rounded-lg hover:bg-primary-50 transition-colors"
          title="Add user"
        >
          <Plus className="w-4 h-4" />
        </button>
      </div>

      {selectedUser ? (
        <div className="p-4 bg-primary-50 border border-primary-200 rounded-lg">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-primary-200 rounded-full flex items-center justify-center">
              <User className="w-4 h-4 text-primary-700" />
            </div>
            <div>
              <p className="font-medium text-primary-900">{selectedUser.username}</p>
              <p className="text-sm text-primary-600">ID: {selectedUser.user_id}</p>
            </div>
          </div>
          
          <button
            onClick={() => onUserSelect(null as any)}
            className="mt-3 text-sm text-primary-600 hover:text-primary-700 font-medium"
          >
            Change partner
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {showCustomForm ? (
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  User ID
                </label>
                <input
                  type="text"
                  value={customUserId}
                  onChange={(e) => setCustomUserId(e.target.value)}
                  className="input"
                  placeholder="Enter user ID"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Username
                </label>
                <input
                  type="text"
                  value={customUsername}
                  onChange={(e) => setCustomUsername(e.target.value)}
                  className="input"
                  placeholder="Enter username"
                />
              </div>
              
              <div className="flex space-x-2">
                <button
                  onClick={handleAddCustomUser}
                  disabled={!customUserId.trim() || !customUsername.trim()}
                  className="btn-primary flex-1"
                >
                  Add User
                </button>
                <button
                  onClick={() => {
                    setShowCustomForm(false);
                    setCustomUserId('');
                    setCustomUsername('');
                  }}
                  className="btn-secondary flex-1"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <div className="text-center py-6">
              <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <User className="w-6 h-6 text-gray-400" />
              </div>
              <p className="text-gray-500 mb-2">No chat partner selected</p>
              <p className="text-sm text-gray-400">
                Click the + button to add a user to chat with
              </p>
            </div>
          )}
        </div>
      )}

      <div className="mt-4 p-3 bg-gray-50 rounded-lg">
        <p className="text-xs text-gray-600">
          <strong>Note:</strong> In this demo, you manually add users by their ID. 
          Both users need to be registered and authenticated to exchange messages.
        </p>
      </div>
    </div>
  );
};