import React, { useState } from 'react';
import { Camera, Shield, ShieldCheck, ShieldX, Eye, EyeOff, Play, Square } from 'lucide-react';
import type { AuthStatus } from '../types';

interface FaceAuthPanelProps {
  authStatus: AuthStatus;
  onStartAuth: (password: string) => Promise<void>;
  onStopAuth: () => Promise<void>;
  isLoading: boolean;
  error: string | null;
}

export const FaceAuthPanel: React.FC<FaceAuthPanelProps> = ({
  authStatus,
  onStartAuth,
  onStopAuth,
  isLoading,
  error,
}) => {
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isAuthActive, setIsAuthActive] = useState(false);

  const handleStartAuth = async () => {
    if (!password.trim()) return;
    
    try {
      await onStartAuth(password);
      setIsAuthActive(true);
    } catch (err) {
      // Error handled by parent
    }
  };

  const handleStopAuth = async () => {
    try {
      await onStopAuth();
      setIsAuthActive(false);
      setPassword('');
    } catch (err) {
      // Error handled by parent
    }
  };

  const getStatusIcon = () => {
    if (authStatus.authenticated) {
      return <ShieldCheck className="w-5 h-5 text-success-600" />;
    } else if (isAuthActive && !authStatus.terminate) {
      return <Shield className="w-5 h-5 text-warning-500 animate-pulse" />;
    } else {
      return <ShieldX className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusText = () => {
    if (authStatus.authenticated) {
      return 'Face Authenticated';
    } else if (isAuthActive && !authStatus.terminate) {
      return 'Authenticating...';
    } else {
      return 'Not Authenticated';
    }
  };

  const getStatusColor = () => {
    if (authStatus.authenticated) {
      return 'text-success-600';
    } else if (isAuthActive && !authStatus.terminate) {
      return 'text-warning-600';
    } else {
      return 'text-gray-500';
    }
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
            <Camera className="w-5 h-5 text-primary-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">Face Authentication</h3>
            <div className={`flex items-center space-x-2 text-sm ${getStatusColor()}`}>
              {getStatusIcon()}
              <span>{getStatusText()}</span>
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          {authStatus.authenticated && (
            <div className="status-online animate-pulse-slow" />
          )}
          {isAuthActive && !authStatus.authenticated && (
            <div className="status-authenticating" />
          )}
          {!isAuthActive && !authStatus.authenticated && (
            <div className="status-offline" />
          )}
        </div>
      </div>

      {!isAuthActive ? (
        <div className="space-y-4">
          <div>
            <label htmlFor="auth-password" className="block text-sm font-medium text-gray-700 mb-2">
              Authentication Password
            </label>
            <div className="relative">
              <input
                id="auth-password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input pr-10"
                placeholder="Enter your face auth password"
                disabled={isLoading}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                disabled={isLoading}
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <button
            onClick={handleStartAuth}
            disabled={isLoading || !password.trim()}
            className="btn-primary w-full"
          >
            {isLoading ? (
              <div className="flex items-center justify-center">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                Starting...
              </div>
            ) : (
              <div className="flex items-center justify-center">
                <Play className="w-4 h-4 mr-2" />
                Start Face Authentication
              </div>
            )}
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="p-4 bg-primary-50 border border-primary-200 rounded-lg">
            <div className="flex items-center space-x-2 text-primary-700 mb-2">
              <Camera className="w-4 h-4" />
              <span className="text-sm font-medium">Camera Active</span>
            </div>
            <p className="text-sm text-primary-600">
              Face authentication is running. Make sure you're visible to your camera.
            </p>
          </div>

          <button
            onClick={handleStopAuth}
            disabled={isLoading}
            className="btn-error w-full"
          >
            <div className="flex items-center justify-center">
              <Square className="w-4 h-4 mr-2" />
              Stop Authentication
            </div>
          </button>
        </div>
      )}

      {error && (
        <div className="mt-4 p-3 bg-error-50 border border-error-200 rounded-lg text-error-700 text-sm animate-slide-up">
          {error}
        </div>
      )}

      <div className="mt-4 p-3 bg-gray-50 rounded-lg">
        <p className="text-xs text-gray-600">
          <strong>Note:</strong> Face authentication uses your camera to continuously verify your identity. 
          Only authenticated users can send and receive encrypted messages.
        </p>
      </div>
    </div>
  );
};