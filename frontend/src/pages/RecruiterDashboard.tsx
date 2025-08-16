import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Plus, Briefcase, Users, MessageCircle, Eye } from 'lucide-react';
import { useApi } from '../hooks/useApi';
import { recruiterService, type RecruiterDashboardData } from '../services/recruiterService';
import { LoadingSpinner } from '../components/LoadingSpinner';
import toast from 'react-hot-toast';

export const RecruiterDashboard: React.FC = () => {
  const navigate = useNavigate();
  const { data: dashboardData, loading, error, execute: fetchDashboard } = useApi<RecruiterDashboardData>();

  useEffect(() => {
    fetchDashboard(() => recruiterService.getDashboardData()).catch(() => {
      console.log('Could not fetch dashboard data, using defaults');
    });
  }, [fetchDashboard]);

  const handleQuickAction = (action: string) => {
    switch (action) {
      case 'post-job':
        navigate('/post-job');
        break;
      case 'view-jobs':
        navigate('/my-jobs');
        break;
      case 'chat':
        navigate('/chat');
        break;
      default:
        toast(`${action} feature coming soon!`);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const stats = dashboardData?.stats || {
    active_jobs: 0,
    total_applications: 0,
    pending_interviews: 0,
    unread_messages: 0
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="space-y-6"
    >
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Recruiter Dashboard</h1>
        <p className="mt-2 text-gray-600">
          {dashboardData?.message || 'Manage your job postings and connect with candidates.'}
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Active Jobs */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="card"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Active Jobs</h3>
            <Briefcase className="h-6 w-6 text-primary-600" />
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-primary-600">{stats.active_jobs}</div>
            <p className="text-sm text-gray-500">Currently posted</p>
          </div>
        </motion.div>

        {/* Applications */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="card"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Applications</h3>
            <Users className="h-6 w-6 text-green-600" />
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">{stats.total_applications}</div>
            <p className="text-sm text-gray-500">Total received</p>
          </div>
        </motion.div>

        {/* Messages */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="card"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Messages</h3>
            <MessageCircle className="h-6 w-6 text-purple-600" />
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600">{stats.unread_messages}</div>
            <p className="text-sm text-gray-500">Unread</p>
          </div>
        </motion.div>
      </div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="card"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <button 
            onClick={() => handleQuickAction('post-job')}
            className="btn-primary flex items-center justify-center space-x-2"
          >
            <Plus className="h-4 w-4" />
            <span>Post New Job</span>
          </button>
          <button 
            onClick={() => handleQuickAction('view-jobs')}
            className="btn-secondary flex items-center justify-center space-x-2"
          >
            <Eye className="h-4 w-4" />
            <span>View My Jobs</span>
          </button>
          <button 
            onClick={() => handleQuickAction('chat')}
            className="btn-secondary flex items-center justify-center space-x-2"
          >
            <MessageCircle className="h-4 w-4" />
            <span>Chat with Candidates</span>
          </button>
        </div>
      </motion.div>

      {/* Error handling */}
      {error && !loading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="bg-red-50 border border-red-200 rounded-lg p-4"
        >
          <p className="text-red-800 text-sm">
            Unable to load dashboard data. Please try refreshing the page.
          </p>
        </motion.div>
      )}
    </motion.div>
  );
};
