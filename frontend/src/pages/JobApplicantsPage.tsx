import React, { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useApi } from '../hooks/useApi';
import api from '../services/api';
import { LoadingSpinner } from '../components/LoadingSpinner';

interface ApplicationItem {
  id: string;
  student_id: string;
  student_email?: string;
  applied_at: string;
  status: string;
}

interface ApplicantsResponse {
  job_id: string;
  job_title: string;
  company_name: string;
  total_applications: number;
  applications: ApplicationItem[];
}

export const JobApplicantsPage: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const { data, loading, error, execute } = useApi<ApplicantsResponse>();

  useEffect(() => {
    if (!jobId) return;
    execute(async () => {
      const res = await api.get<ApplicantsResponse>(`/jobs/${jobId}/applications`);
      return res.data;
    });
  }, [jobId, execute]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Job Applicants</h1>
        <p className="mt-2 text-gray-600">View candidates who applied to this job.</p>
      </div>

      {loading && (
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner size="lg" />
        </div>
      )}

      {!loading && error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800 text-sm">
          Failed to load applicants. Please try again.
        </div>
      )}

      {!loading && !error && data && (
        <div className="card">
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-gray-900">{data.job_title}</h3>
            <p className="text-sm text-gray-600">{data.company_name}</p>
            <p className="text-sm text-gray-500 mt-1">{data.total_applications} applications</p>
          </div>
          <div className="divide-y divide-gray-200">
            {data.applications.map((app) => (
              <div key={app.id} className="py-3 flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">{app.student_id}</p>
                  <p className="text-xs text-gray-500">{new Date(app.applied_at).toLocaleString()}</p>
                </div>
                <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-700">{app.status}</span>
              </div>
            ))}
            {data.applications.length === 0 && (
              <p className="text-sm text-gray-600">No applications yet.</p>
            )}
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default JobApplicantsPage;
