import api from './api';
import type { ResumeAnalysis, MockInterviewResponse } from '../types';

export const resumeService = {
  async getResumeAnalysis(): Promise<ResumeAnalysis | null> {
    try {
      const response = await api.get('/student/resume-analysis');
      return response.data;
    } catch (error: any) {
      if (error?.response?.status === 404) return null;
      throw error;
    }
  },
  async uploadResume(file: File): Promise<{
    filename: string;
    raw_text: string;
    extracted_text: string;
    extracted_fields: string[];
  }> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/student/upload-resume', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  async analyzeResume(
    file: File,
    companyName: string,
    jobTitle: string,
    jobDescription: string
  ): Promise<ResumeAnalysis> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('company_name', companyName);
    formData.append('job_title', jobTitle);
    formData.append('job_description', jobDescription);
    
    const response = await api.post('/student/analyze-resume', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  async improveResume(file: File, jobDescription: string): Promise<{ result: string }> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('job_description', jobDescription);
    
    const response = await api.post('/student/improve-resume', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  async getMissingKeywords(file: File, jobDescription: string): Promise<{ result: string }> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('job_description', jobDescription);
    
    const response = await api.post('/student/missing-keywords', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  async getPercentageMatch(file: File, jobDescription: string): Promise<{ result: string }> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('job_description', jobDescription);
    
    const response = await api.post('/student/percentage-match', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  async downloadReport(filename: string): Promise<Blob> {
    const response = await api.get(`/student/download-report?filename=${filename}`, {
      responseType: 'blob',
    });
    
    return response.data;
  },

  // Recruiter operations
  async getMockInterview(resumeText: string, jobDescription: string): Promise<MockInterviewResponse> {
    const response = await api.post('/recruiter/mock-interview', {
      resume_text: resumeText,
      job_description: jobDescription,
    });
    
    return response.data;
  },
};
