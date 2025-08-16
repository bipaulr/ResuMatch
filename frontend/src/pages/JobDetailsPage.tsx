import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ArrowLeft, Building, MapPin, DollarSign, Clock, Users, 
  Briefcase, CheckCircle, Calendar, Share2 
} from 'lucide-react';
import { useApi } from '../hooks/useApi';
import { jobService } from '../services/jobService';
import { studentService } from '../services/studentService';
import { LoadingSpinner } from '../components/LoadingSpinner';
import type { Job } from '../types';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import { getAxiosErrorMessage } from '../utils/helpers';

export const JobDetailsPage: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  const [isApplying, setIsApplying] = useState(false);
  const [hasApplied, setHasApplied] = useState(false);
  const { data: job, loading, error, execute: fetchJobDetails } = useApi<Job>();
  const { user } = useAuth();

  useEffect(() => {
    if (jobId) {
      fetchJobDetails(() => jobService.getJobDetails(jobId));
      if (user?.role === 'student') {
        checkApplicationStatus();
      }
    }
  }, [jobId, fetchJobDetails, user?.role]);

  const checkApplicationStatus = async () => {
    if (!jobId) return;
    try {
      const applications = await studentService.getApplications();
      const hasApplicationForJob = applications.some(app => app.job.id === jobId);
      setHasApplied(hasApplicationForJob);
    } catch (error) {
      // If we can't check application status, assume not applied
      setHasApplied(false);
    }
  };

  const handleApply = async () => {
    if (!jobId || !job) return;
    
    try {
      setIsApplying(true);
      toast.loading('Submitting application...', { id: 'apply' });
      const result = await studentService.applyToJob(jobId);
      toast.success(result.message || 'Application submitted successfully!', { id: 'apply' });
      setHasApplied(true);
    } catch (error: any) {
      const errorMsg = getAxiosErrorMessage(error, 'Failed to submit application');
      toast.error(errorMsg, { id: 'apply' });
    } finally {
      setIsApplying(false);
    }
  };  const handleShare = async () => {
    if (navigator.share && job) {
      try {
        await navigator.share({
          title: `${job.title} at ${job.company_name}`,
          text: `Check out this job opportunity: ${job.title} at ${job.company_name}`,
          url: window.location.href,
        });
      } catch (error) {
        // Fallback to clipboard
        await navigator.clipboard.writeText(window.location.href);
        toast.success('Job link copied to clipboard!');
      }
    } else {
      // Fallback to clipboard
      await navigator.clipboard.writeText(window.location.href);
      toast.success('Job link copied to clipboard!');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error || !job) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="text-center py-12"
      >
        <div className="bg-red-50 border border-red-200 rounded-lg p-8 max-w-md mx-auto">
          <h3 className="text-lg font-medium text-red-900 mb-2">Job Not Found</h3>
          <p className="text-red-700 mb-4">
            The job you're looking for doesn't exist or has been removed.
          </p>
          <button
            onClick={() => navigate('/jobs')}
            className="btn-primary"
          >
            Browse All Jobs
          </button>
        </div>
      </motion.div>
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
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate(-1)}
          className="btn-secondary p-2"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-gray-900">{job.title}</h1>
          <p className="mt-2 text-gray-600 flex items-center space-x-2">
            <Building className="h-4 w-4" />
            <span>{job.company_name}</span>
            <span>•</span>
            <MapPin className="h-4 w-4" />
            <span>{job.location}</span>
          </p>
        </div>
        <button
          onClick={handleShare}
          className="btn-secondary p-2"
        >
          <Share2 className="h-5 w-5" />
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Job Overview */}
          <div className="card">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="flex items-center space-x-2">
                <Briefcase className="h-5 w-5 text-gray-500" />
                <div>
                  <p className="text-sm text-gray-500">Experience</p>
                  <p className="font-medium">{job.experience_level}</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <Clock className="h-5 w-5 text-gray-500" />
                <div>
                  <p className="text-sm text-gray-500">Status</p>
                  <p className="font-medium capitalize">{job.status}</p>
                </div>
              </div>

              {job.salary_range && (
                <div className="flex items-center space-x-2">
                  <DollarSign className="h-5 w-5 text-gray-500" />
                  <div>
                    <p className="text-sm text-gray-500">Salary</p>
                    <p className="font-medium">{job.salary_range}</p>
                  </div>
                </div>
              )}

              <div className="flex items-center space-x-2">
                <Calendar className="h-5 w-5 text-gray-500" />
                <div>
                  <p className="text-sm text-gray-500">Posted</p>
                  <p className="font-medium">
                    {new Date(job.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </div>

            {/* Application Status */}
            {hasApplied && (
              <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span className="font-medium text-green-800">Application Submitted</span>
                </div>
                <p className="text-green-700 text-sm mt-1">
                  Your application has been submitted successfully. The recruiter will review it soon.
                </p>
              </div>
            )}

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Job Description</h3>
              <div className="prose max-w-none">
                <p className="text-gray-700 whitespace-pre-line">{job.description}</p>
              </div>
            </div>
          </div>

          {/* Required Skills */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Required Skills</h3>
            <div className="flex flex-wrap gap-2">
              {job.skills_required.map((skill, index) => (
                <span
                  key={index}
                  className="px-3 py-2 bg-primary-100 text-primary-800 rounded-lg text-sm font-medium"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Apply Section (students only) */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Apply for this job</h3>
            {user?.role !== 'student' ? (
              <div className="text-sm text-gray-600">Recruiters can view job details here. Applications are student-only.</div>
            ) : hasApplied ? (
              <div className="text-center py-4">
                <CheckCircle className="mx-auto h-12 w-12 text-green-600 mb-3" />
                <p className="font-medium text-green-800">Already Applied</p>
                <p className="text-sm text-green-600 mt-1">
                  Application submitted successfully
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                <button
                  onClick={handleApply}
                  disabled={isApplying}
                  className="w-full btn-primary flex items-center justify-center space-x-2"
                >
                  {isApplying ? (
                    <LoadingSpinner size="sm" />
                  ) : (
                    <>
                      <Users className="h-4 w-4" />
                      <span>Apply Now</span>
                    </>
                  )}
                </button>
                <p className="text-xs text-gray-500 text-center">
                  By clicking Apply, you agree to our terms and conditions
                </p>
              </div>
            )}
          </div>

          {/* Company Info */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">About {job.company_name}</h3>
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Building className="h-4 w-4 text-gray-500" />
                <span className="text-sm text-gray-600">Technology Company</span>
              </div>
              <div className="flex items-center space-x-2">
                <MapPin className="h-4 w-4 text-gray-500" />
                <span className="text-sm text-gray-600">{job.location}</span>
              </div>
              <div className="flex items-center space-x-2">
                <Users className="h-4 w-4 text-gray-500" />
                <span className="text-sm text-gray-600">Actively hiring</span>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
            <div className="space-y-2">
              <button
                onClick={() => navigate('/jobs')}
                className="w-full btn-secondary text-left"
              >
                View Similar Jobs
              </button>
              <button
                onClick={() => navigate('/resume-upload')}
                className="w-full btn-secondary text-left"
              >
                Analyze Resume Match
              </button>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};
