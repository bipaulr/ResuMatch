import api from './api';
import type { Job, ResumeAnalysis, MockInterviewResponse } from '../types';

export interface StudentStats {
  resume_score: number | null;
  job_matches: number;
  applications: number;
  recent_activity: Array<{
    id: string;
    type: 'application' | 'message' | 'analysis';
    title: string;
    timestamp: string;
  }>;
}

export interface ResumeUploadResponse {
  message: string;
  filename: string;
  resume_uploaded: boolean;
  raw_text: string;
  extracted_text: string;
  extracted_fields: string[];
  score: number;
  suggested_edits: string[];
  matching_jobs: Array<{
    job_id: string;
    title: string;
    company_name: string;
    location: string;
    match_percent: number;
    matching_skills: string[];
    missing_skills: string[];
  }>;
}

export const studentService = {
  async getStats(): Promise<StudentStats> {
    const response = await api.get('/student/stats');
    return response.data;
  },

  async uploadResume(file: File): Promise<ResumeUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/student/upload-resume', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  async getResumeAnalysis(): Promise<ResumeAnalysis | null> {
    try {
      const response = await api.get('/student/resume-analysis');
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null; // No resume uploaded yet
      }
      throw error;
    }
  },

  async getJobRecommendations(): Promise<Job[]> {
    const response = await api.get('/student/job-recommendations');
    return response.data;
  },

  async applyToJob(jobId: string): Promise<{ message: string; application_id: string; job_title: string; company_name: string; chat_room_id: string }> {
    const response = await api.post(`/student/jobs/${jobId}/apply`);
    return response.data;
  },

  async getApplications(): Promise<Array<{
    id: string;
    job: Job;
    status: string;
    applied_at: string;
  }>> {
    const response = await api.get('/student/applications');
    return response.data;
  },

  async mockInterview(role: string, jobDescription?: string): Promise<{ role: string; result: MockInterviewResponse }>{
    const form = new FormData();
    form.append('role', role);
    if (jobDescription) form.append('job_description', jobDescription);
    // Ensure proper multipart Content-Type so FastAPI Form(...) parses correctly
    const response = await api.post('/student/mock-interview', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  async startMockInterview(formData: FormData): Promise<{ session_id: string; first_question: string; status: string }> {
    const response = await api.post('/student/mock-interview/start', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  async respondToInterview(sessionId: string, formData: FormData): Promise<{ 
    next_question?: string; 
    status: string; 
    is_complete: boolean; 
    message?: string;
    feedback?: any;
  }> {
    const response = await api.post(`/student/mock-interview/${sessionId}/respond`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  async getInterviewFeedback(sessionId: string): Promise<{
    overall_score: {
      value: number;
      description: string;
    };
    strengths: string[];
    weaknesses: string[];
    detailed_feedback: {
      communication: { score: number; feedback: string };
      technical_competency: { score: number; feedback: string };
      cultural_fit: { score: number; feedback: string };
      problem_solving: { score: number; feedback: string };
    };
    question_analysis: Array<{
      question: string;
      candidate_answer: string;
      feedback: string;
      suggested_improvement: string;
      sample_answer: string;
    }>;
    key_recommendations: string[];
    next_steps: string[];
  }> {
    const response = await api.get(`/student/mock-interview/${sessionId}/feedback`);
    // Backend returns { session_id, role, completed_at, feedback }
    // We need to extract just the feedback object
    return response.data.feedback;
  },

  async getInterviewSession(sessionId: string): Promise<{
    _id: string;
    student_id: string;
    role: string;
    job_description?: string;
    status: 'active' | 'completed';
    messages: Array<{
      type: 'question' | 'answer';
      content: string;
      timestamp: string;
    }>;
  }> {
    const response = await api.get(`/student/mock-interview/${sessionId}`);
    return response.data;
  },
};
