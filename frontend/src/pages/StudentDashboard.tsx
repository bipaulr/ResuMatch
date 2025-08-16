import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Upload, Briefcase, MessageCircle, TrendingUp, FileText, Target, Brain } from 'lucide-react';
import { useApi } from '../hooks/useApi';
import { studentService, type StudentStats } from '../services/studentService';
import { LoadingSpinner } from '../components/LoadingSpinner';
import toast from 'react-hot-toast';
import { getAxiosErrorMessage } from '../utils/helpers';

export const StudentDashboard: React.FC = () => {
  const { data: stats, loading, error, execute: fetchStats } = useApi<StudentStats>();
  const [hasResume, setHasResume] = useState(false);

  useEffect(() => {
    fetchStats(() => studentService.getStats()).catch(() => {
      // If stats endpoint fails, continue with default values
      console.log('Could not fetch stats, using defaults');
    });

    // Check if user has uploaded a resume
    checkResumeStatus();
  }, [fetchStats]);

  const checkResumeStatus = async () => {
    try {
      const analysis = await studentService.getResumeAnalysis();
      setHasResume(analysis !== null);
    } catch (error) {
      setHasResume(false);
    }
  };

  const handleQuickAction = async (action: string) => {
    switch (action) {
      case 'upload':
        // Navigate to upload page or open file dialog
        document.getElementById('resume-upload')?.click();
        break;
      case 'jobs':
        // Will be handled by Link component
        break;
      case 'chat':
        // Will be handled by Link component
        break;
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (file.type !== 'application/pdf') {
      toast.error('Please upload a PDF file');
      return;
    }

    if (file.size > 10 * 1024 * 1024) { // 10MB limit
      toast.error('File size should be less than 10MB');
      return;
    }

    try {
      toast.loading('Uploading and analyzing resume...', { id: 'upload' });
      await studentService.uploadResume(file);
      toast.success('Resume uploaded and analyzed successfully!', { id: 'upload' });
      // Refresh stats and resume status
      fetchStats(() => studentService.getStats());
      setHasResume(true);
    } catch (error: any) {
      toast.error(getAxiosErrorMessage(error, 'Failed to upload resume'), { id: 'upload' });
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="space-y-6"
    >
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 transition-colors duration-200">Student Dashboard</h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400 transition-colors duration-200">
          Welcome to your dashboard. Upload your resume and find matching jobs.
        </p>
      </div>

      {/* Resume Status Alert */}
      {!hasResume && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-yellow-50 border border-yellow-200 rounded-lg p-4"
        >
          <div className="flex items-center space-x-2">
            <FileText className="h-5 w-5 text-yellow-600" />
            <span className="font-medium text-yellow-800">No resume uploaded</span>
          </div>
          <p className="text-yellow-700 text-sm mt-1">
            Upload your resume to get personalized job matches and see your compatibility scores.
          </p>
        </motion.div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Resume Score Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="card"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Resume Score</h3>
            <FileText className="h-6 w-6 text-primary-600" />
          </div>
          <div className="text-center">
            <div className={`text-3xl font-bold ${
              hasResume && stats?.resume_score ? 'text-primary-600' : 'text-gray-400'
            }`}>
              {hasResume && stats?.resume_score ? `${stats.resume_score}%` : '--'}
            </div>
            <p className="text-sm text-gray-500">
              {hasResume ? 'Resume quality score' : 'Upload resume to get score'}
            </p>
          </div>
        </motion.div>

        {/* Job Matches */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="card"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Job Matches</h3>
            <Target className="h-6 w-6 text-green-600" />
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">
              {hasResume ? (stats?.job_matches ?? 0) : '--'}
            </div>
            <p className="text-sm text-gray-500">
              {hasResume ? 'Matching opportunities' : 'Analyze resume for matches'}
            </p>
          </div>
        </motion.div>

        {/* Applications */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="card"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Applications</h3>
            <TrendingUp className="h-6 w-6 text-blue-600" />
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">
              {stats?.applications ?? 0}
            </div>
            <p className="text-sm text-gray-500">Jobs applied to</p>
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
        <div className="space-y-3">
          <button 
            onClick={() => handleQuickAction('upload')}
            className="w-full btn-primary text-left flex items-center space-x-3"
          >
            <Upload className="h-5 w-5" />
            <span>{hasResume ? 'Update Resume' : 'Upload Resume for Analysis'}</span>
          </button>
          
          <Link
            to="/resume-upload"
            className="w-full btn-secondary text-left flex items-center space-x-3"
          >
            <FileText className="h-5 w-5" />
            <span>Advanced Resume Analysis</span>
          </Link>
          
          <Link
            to="/jobs"
            className="w-full btn-secondary text-left flex items-center space-x-3"
          >
            <Briefcase className="h-5 w-5" />
            <span>Browse Job Opportunities</span>
          </Link>

          <Link
            to="/mock-interview"
            className={`w-full text-left flex items-center space-x-3 ${
              hasResume ? 'btn-secondary' : 'btn-secondary opacity-50 cursor-not-allowed'
            }`}
          >
            <Brain className="h-5 w-5" />
            <span>Mock Interview Practice</span>
            {!hasResume && <span className="text-xs">(Upload resume first)</span>}
          </Link>
          
          <Link
            to="/chat"
            className="w-full btn-secondary text-left flex items-center space-x-3"
          >
            <MessageCircle className="h-5 w-5" />
            <span>View Chat Messages</span>
          </Link>
        </div>
      </motion.div>

      {/* Hidden file input for resume upload */}
      <input
        id="resume-upload"
        type="file"
        accept=".pdf"
        onChange={handleFileUpload}
        className="hidden"
      />

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
