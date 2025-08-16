export interface User {
  id: string;
  username: string;
  email: string;
  role: 'student' | 'recruiter' | 'admin';
  created_at?: string;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string; originalError?: any }>;
  signup: (userData: SignupData) => Promise<void>;
  logout: () => void;
  loading: boolean;
  error: string | null;
}

export interface SignupData {
  username: string;
  email: string;
  password: string;
  role: 'student' | 'recruiter';
}

export interface LoginData {
  email: string;
  password: string;
}

export interface Job {
  id: string;
  title: string;
  company_name: string;
  location: string;
  description: string;
  skills_required: string[];
  experience_level: string;
  salary_range?: string;
  status: 'active' | 'inactive';
  recruiter_id: string;
  recruiter_email: string;
  created_at: string;
}

export interface ResumeAnalysis {
  gemini_analysis: {
    missing_keywords: string[];
    profile_summary: string;
    resume_quality_score: number;
    tone_style_score: number;
    content_score: number;
    structure_score: number;
    percentage_match: number;
    top_job_suggestions: string[];
    keyword_optimization: string;
    ats_resume_score: number;
    ats_improvement_suggestions: string[];
  };
  extracted_skills: string[];
  top_job_suggestions: Job[];
  skill_match_details: {
    match_percent: number;
    matching_skills: string[];
    missing_skills: string[];
    extra_skills: string[];
    total_required_skills: number;
    total_matching_skills: number;
  };
  scores: {
    resume_quality_score: { value: number; color: string };
    tone_style_score: { value: number; color: string };
    content_score: { value: number; color: string };
    structure_score: { value: number; color: string };
  };
}

export interface Message {
  id: string;
  room_id: string;
  sender_id: string;
  receiver_id: string;
  content: string;
  timestamp: string;
  read: boolean;
}

export interface ChatRoom {
  id: string;
  job_id: string;
  student_id?: string;
  recruiter_id?: string;
  job_title: string;
  company_name: string;
  participants: string[];
  created_at: string;
  last_message?: {
    content: string;
    sender_id: string;
    timestamp: string;
  };
  unread_count: number;
}

export interface MockInterviewResponse {
  technical_questions: string[];
  behavioral_questions: string[];
  fit_analysis: string;
  focus_areas: string[];
}

export interface ApiResponse<T> {
  data?: T;
  message?: string;
  error?: string;
}

export interface LoadingState {
  isLoading: boolean;
  error: string | null;
}
