import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, XCircle, Clock, Wifi, Database, Shield } from 'lucide-react';
import api from '../services/api';

interface ConnectionStatus {
  backend: 'connected' | 'disconnected' | 'checking';
  database: 'connected' | 'disconnected' | 'checking';
  auth: 'valid' | 'invalid' | 'checking';
}

export const ConnectionTest: React.FC = () => {
  const [status, setStatus] = useState<ConnectionStatus>({
    backend: 'checking',
    database: 'checking',
    auth: 'checking',
  });

  useEffect(() => {
    testConnections();
  }, []);

  const testConnections = async () => {
    // Test backend connection
    try {
      await api.get('/');
      setStatus(prev => ({ ...prev, backend: 'connected' }));
    } catch (error) {
      setStatus(prev => ({ ...prev, backend: 'disconnected' }));
    }

    // Test database connection (via health endpoint)
    try {
      await api.get('/health');
      setStatus(prev => ({ ...prev, database: 'connected' }));
    } catch (error) {
      setStatus(prev => ({ ...prev, database: 'disconnected' }));
    }

    // Test auth status
    try {
      const token = localStorage.getItem('token');
      if (token) {
        await api.get('/auth/profile');
        setStatus(prev => ({ ...prev, auth: 'valid' }));
      } else {
        setStatus(prev => ({ ...prev, auth: 'invalid' }));
      }
    } catch (error) {
      setStatus(prev => ({ ...prev, auth: 'invalid' }));
    }
  };

  const getStatusIcon = (connectionStatus: string) => {
    switch (connectionStatus) {
      case 'connected':
      case 'valid':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'disconnected':
      case 'invalid':
        return <XCircle className="h-5 w-5 text-red-600" />;
      default:
        return <Clock className="h-5 w-5 text-yellow-600 animate-spin" />;
    }
  };

  const getStatusText = (connectionStatus: string) => {
    switch (connectionStatus) {
      case 'connected':
        return 'Connected';
      case 'valid':
        return 'Valid';
      case 'disconnected':
        return 'Disconnected';
      case 'invalid':
        return 'Invalid';
      default:
        return 'Checking...';
    }
  };

  const getStatusColor = (connectionStatus: string) => {
    switch (connectionStatus) {
      case 'connected':
      case 'valid':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'disconnected':
      case 'invalid':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="max-w-2xl mx-auto space-y-6"
    >
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">Connection Test</h1>
        <p className="mt-2 text-gray-600">
          Testing frontend-backend connectivity and authentication status
        </p>
      </div>

      <div className="space-y-4">
        {/* Backend Connection */}
        <div className={`p-4 rounded-lg border ${getStatusColor(status.backend)}`}>
          <div className="flex items-center space-x-3">
            <Wifi className="h-6 w-6" />
            <div className="flex-1">
              <h3 className="font-semibold">Backend API</h3>
              <p className="text-sm opacity-75">FastAPI server connectivity</p>
            </div>
            <div className="flex items-center space-x-2">
              {getStatusIcon(status.backend)}
              <span className="font-medium">{getStatusText(status.backend)}</span>
            </div>
          </div>
        </div>

        {/* Database Connection */}
        <div className={`p-4 rounded-lg border ${getStatusColor(status.database)}`}>
          <div className="flex items-center space-x-3">
            <Database className="h-6 w-6" />
            <div className="flex-1">
              <h3 className="font-semibold">Database</h3>
              <p className="text-sm opacity-75">MongoDB connection status</p>
            </div>
            <div className="flex items-center space-x-2">
              {getStatusIcon(status.database)}
              <span className="font-medium">{getStatusText(status.database)}</span>
            </div>
          </div>
        </div>

        {/* Authentication */}
        <div className={`p-4 rounded-lg border ${getStatusColor(status.auth)}`}>
          <div className="flex items-center space-x-3">
            <Shield className="h-6 w-6" />
            <div className="flex-1">
              <h3 className="font-semibold">Authentication</h3>
              <p className="text-sm opacity-75">JWT token validation</p>
            </div>
            <div className="flex items-center space-x-2">
              {getStatusIcon(status.auth)}
              <span className="font-medium">{getStatusText(status.auth)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-center space-x-4">
        <button
          onClick={testConnections}
          className="btn-primary px-6 py-2"
        >
          Retest Connections
        </button>
        <button
          onClick={() => window.location.href = '/'}
          className="btn-secondary px-6 py-2"
        >
          Go to Dashboard
        </button>
      </div>

      {/* Connection Details */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="font-semibold text-gray-900 mb-2">Connection Details</h4>
        <div className="text-sm text-gray-600 space-y-1">
          <p><strong>Frontend:</strong> http://localhost:5175</p>
          <p><strong>Backend:</strong> http://127.0.0.1:8000</p>
          <p><strong>Auth Token:</strong> {localStorage.getItem('token') ? 'Present' : 'Not found'}</p>
        </div>
      </div>
    </motion.div>
  );
};
