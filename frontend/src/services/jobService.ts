import api from './api';
import type { Job } from '../types';

export const jobService = {
  // Student job operations
  async getJobs(params?: {
    skip?: number;
    limit?: number;
    location?: string;
    company?: string;
    skills?: string[];
  }): Promise<Job[]> {
    // Use public jobs listing to support both students and recruiters
    const response = await api.get('/jobs', { params });
    return response.data;
  },

  async getJobDetails(jobId: string): Promise<Job> {
    // Use public job details endpoint for both roles
    const response = await api.get(`/jobs/${jobId}`);
    return response.data;
  },

  async applyToJob(jobId: string): Promise<{ message: string; application_id: string; job_title: string; company_name: string; chat_room_id: string }> {
    const response = await api.post(`/student/jobs/${jobId}/apply`);
    return response.data;
  },

  // Recruiter job operations
  async postJob(jobData: Omit<Job, 'id' | 'recruiter_id' | 'recruiter_email' | 'created_at'>): Promise<{ message: string; job_id: string }> {
    const response = await api.post('/recruiter/post-job', jobData);
    return response.data;
  },

  async getMyJobs(): Promise<{ recruiter: string; total_jobs: number; jobs: Job[] }> {
    const response = await api.get('/recruiter/my-jobs');
    return response.data;
  },
};
