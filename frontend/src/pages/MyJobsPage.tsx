import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Briefcase, Plus, MapPin, Calendar, Building2 } from 'lucide-react';
import { useApi } from '../hooks/useApi';
import { recruiterService } from '../services/recruiterService';
import type { Job } from '../types';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const MyJobsPage: React.FC = () => {
  const navigate = useNavigate();
  const { data, loading, error, execute } = useApi<{ recruiter: string; total_jobs: number; jobs: Job[] }>();

  useEffect(() => {
    execute(() => recruiterService.getMyJobs());
  }, [execute]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">My Jobs</h1>
          <p className="mt-2 text-gray-600">Manage and review all jobs you've posted.</p>
        </div>
        <button className="btn-primary" onClick={() => navigate('/post-job')}>
          <Plus className="h-4 w-4 mr-2" /> Post a Job
        </button>
      </div>

      {loading && (
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner size="lg" />
        </div>
      )}

      {!loading && error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800 text-sm">
          Failed to load jobs. Please try again.
        </div>
      )}

      {!loading && !error && (
        <div className="space-y-4">
          {data?.jobs?.length ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {data.jobs.map((job) => (
                <div key={job.id} className="card hover:shadow-lg transition-shadow">
                  <div className="flex items-start justify-between">
                    <div className="space-y-1">
                      <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                        <Briefcase className="h-5 w-5 text-primary-600 mr-2" /> {job.title}
                      </h3>
                      <div className="text-sm text-gray-600 flex items-center">
                        <Building2 className="h-4 w-4 mr-1" /> {job.company_name}
                      </div>
                      <div className="text-sm text-gray-600 flex items-center">
                        <MapPin className="h-4 w-4 mr-1" /> {job.location}
                      </div>
                      <div className="text-xs text-gray-500 flex items-center">
                        <Calendar className="h-4 w-4 mr-1" />
                        {job.created_at ? new Date(job.created_at).toLocaleDateString() : '—'}
                      </div>
                    </div>
                    <span
                      className={`px-2 py-1 text-xs rounded-full ${
                        job.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      {job.status || 'draft'}
                    </span>
                  </div>
                  {job.skills_required?.length ? (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {job.skills_required.slice(0, 6).map((s) => (
                        <span key={s} className="px-2 py-0.5 text-xs bg-gray-100 text-gray-700 rounded">
                          {s}
                        </span>
                      ))}
                      {job.skills_required.length > 6 && (
                        <span className="text-xs text-gray-500">+{job.skills_required.length - 6} more</span>
                      )}
                    </div>
                  ) : null}
                </div>
              ))}
            </div>
          ) : (
            <div className="card text-center py-10">
              <Briefcase className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-lg font-semibold text-gray-900">No jobs posted yet</h3>
              <p className="mt-1 text-gray-600">Post your first job to start receiving applications.</p>
              <div className="mt-4">
                <button className="btn-primary" onClick={() => navigate('/post-job')}>
                  <Plus className="h-4 w-4 mr-2" /> Post a Job
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </motion.div>
  );
};
