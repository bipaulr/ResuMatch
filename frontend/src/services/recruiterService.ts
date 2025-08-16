import api from './api';
import type { Job } from '../types';

export interface RecruiterStats {
  active_jobs: number;
  total_applications: number;
  pending_interviews: number;
  unread_messages: number;
}

export interface RecruiterDashboardData {
  message: string;
  role: string;
  email: string;
  stats: RecruiterStats;
  recent_activity: Array<{
    id: string;
    type: 'application' | 'message' | 'interview';
    title: string;
    timestamp: string;
  }>;
}

export interface PostJobData {
  title: string;
  description: string;
  company_name: string;
  location: string;
  skills_required: string[];
  experience_level: string;
  salary_range?: string;
  job_type: string;
}

export interface MockInterviewRequest {
  resume_text: string;
  job_description: string;
}

export interface MockInterviewResponse {
  questions: Array<{
    question: string;
    category: string;
    difficulty: string;
  }>;
  tips: string[];
  focus_areas: string[];
}

export const recruiterService = {
  async getDashboardData(): Promise<RecruiterDashboardData> {
    const response = await api.get('/recruiter/dashboard');
    return response.data;
  },

  async getStats(): Promise<RecruiterStats> {
    const response = await api.get('/recruiter/stats');
    return response.data;
  },

  async postJob(jobData: PostJobData): Promise<{ message: string; job_id: string }> {
    const response = await api.post('/recruiter/post-job', jobData);
    return response.data;
  },

  async getMyJobs(): Promise<{ recruiter: string; total_jobs: number; jobs: Job[] }> {
    const response = await api.get('/recruiter/my-jobs');
    return response.data;
  },

  async getMockInterview(data: MockInterviewRequest): Promise<MockInterviewResponse> {
    const response = await api.post('/recruiter/mock-interview', data);
    return response.data;
  },

  async getChatHistory(roomId: string): Promise<any> {
    const response = await api.get(`/recruiter/chat-history/${roomId}`);
    return response.data;
  },
};
