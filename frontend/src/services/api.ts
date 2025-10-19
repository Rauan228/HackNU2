import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Types
export interface User {
  id: number;
  email: string;
  full_name: string;
  phone?: string;
  user_type: 'job_seeker' | 'employer';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Job {
  id: number;
  title: string;
  description: string;
  requirements?: string;
  salary_min?: number;
  salary_max?: number;
  salary_currency?: string;
  location?: string;
  employment_type?: string;
  experience_level?: string;
  company_name: string;
  is_active: boolean;
  employer_id: number;
  created_at: string;
  updated_at: string;
}

export interface Resume {
  id: number;
  title: string;
  summary?: string;
  experience?: string;
  education?: string;
  skills?: string;
  languages?: string;
  portfolio_url?: string;
  desired_position?: string;
  desired_salary?: number;
  location?: string;
  is_public?: boolean;
  user_id: number;
  created_at: string;
  updated_at: string;
}

export interface Application {
  id: number;
  cover_letter?: string;
  status: 'pending' | 'reviewed' | 'accepted' | 'rejected';
  user_id: number;
  job_id: number;
  resume_id: number;
  created_at: string;
  updated_at: string;
  job_title?: string;
  company_name?: string;
  resume_title?: string;
  user_name?: string;
}

export interface ChatMessage {
  id: string;
  role: 'USER' | 'ASSISTANT';
  content: string;
  created_at: string;
}

export interface ChatSession {
  id: number;
  session_id: string;
  user_id?: number;
  created_at: string;
  updated_at: string;
  messages: ChatMessage[];
}

// Auth API
export const authAPI = {
  register: (data: {
    email: string;
    password: string;
    full_name: string;
    phone?: string;
    user_type: 'job_seeker' | 'employer';
  }) => api.post<User>('/auth/register', data),

  login: (data: { email: string; password: string }) =>
    api.post<{ access_token: string; token_type: string }>('/auth/login', data),

  getMe: () => api.get<User>('/auth/me'),
};

// Jobs API
export const jobsAPI = {
  getJobs: (params?: {
    page?: number;
    limit?: number;
    search?: string;
    location?: string;
  }) => api.get<{
    jobs: Job[];
    total: number;
    page: number;
    limit: number;
  }>('/jobs/', { params }),

  getJob: (id: number) => api.get<Job>(`/jobs/${id}`),

  createJob: (data: {
    title: string;
    description: string;
    requirements?: string;
    salary_min?: number;
    salary_max?: number;
    location?: string;
    company_name: string;
  }) => api.post<Job>('/jobs/', data),

  updateJob: (id: number, data: Partial<Job>) => api.put<Job>(`/jobs/${id}`, data),

  deleteJob: (id: number) => api.delete(`/jobs/${id}`),

  getMyJobs: () => api.get<Job[]>('/jobs/my/jobs'),
};

// Resumes API
export const resumesAPI = {
  getResumes: () => api.get<Resume[]>('/resumes/'),

  getResume: (id: number) => api.get<Resume>(`/resumes/${id}`),

  createResume: (data: {
    title: string;
    summary?: string;
    experience?: string;
    education?: string;
    skills?: string;
    languages?: string;
    portfolio_url?: string;
    desired_position?: string;
    desired_salary?: number;
    location?: string;
    is_public?: boolean;
  }) => api.post<Resume>('/resumes/', data),

  updateResume: (id: number, data: Partial<Resume>) =>
    api.put<Resume>(`/resumes/${id}`, data),

  deleteResume: (id: number) => api.delete(`/resumes/${id}`),
};

// Applications API
export const applicationsAPI = {
  getApplications: () => api.get<Application[]>('/applications/'),

  getApplication: (id: number) => api.get<Application>(`/applications/${id}`),

  createApplication: (data: {
    job_id: number;
    resume_id: number;
    cover_letter?: string;
  }) => api.post<Application>('/applications/', data),

  updateApplication: (id: number, data: {
    cover_letter?: string;
    status?: 'pending' | 'reviewed' | 'accepted' | 'rejected';
  }) => api.put<Application>(`/applications/${id}`, data),

  deleteApplication: (id: number) => api.delete(`/applications/${id}`),

  getApplicationResume: (applicationId: number) => api.get<Resume>(`/applications/${applicationId}/resume`),
};

// Chat API
// SmartBot interfaces
export interface SmartBotMessage {
  id: string;
  role: 'USER' | 'ASSISTANT' | 'SYSTEM';
  content: string;
  created_at: string;
}

export interface SmartBotSession {
  id: number;
  session_id: string;
  application_id: number;
  status: 'active' | 'completed' | 'paused';
  created_at: string;
  updated_at: string;
}

export interface CandidateAnalysis {
  id: number;
  application_id: number;
  overall_score: number;
  summary: string;
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  created_at: string;
}

export const chatAPI = {
  sendMessage: (data: { message: string; session_id?: string }) =>
    api.post<{ message: string; session_id: string }>('/chat/', data),

  getSession: (sessionId: string) => api.get<ChatSession>(`/chat/sessions/${sessionId}`),

  getSessions: () => api.get<ChatSession[]>('/chat/sessions'),
};

export const smartBotAPI = {
  startAnalysis: (data: { application_id: number }) =>
    api.post<{
      session_id: string;
      initial_message?: string;
      is_completed: boolean;
    }>('/smartbot/start-analysis', data),
  
  startEmployerAnalysis: (data: { application_id: number }) =>
    api.post<{
      session_id: string;
      initial_message?: string;
      is_completed: boolean;
    }>('/smartbot/employer/start-analysis', data),

  sendMessage: (data: { session_id: string; message: string }) =>
    api.post<{
      message: string;
      is_completed: boolean;
      analysis?: CandidateAnalysis;
    }>('/smartbot/chat', data),

  getSession: (sessionId: string) => api.get<SmartBotSession>(`/smartbot/sessions/${sessionId}`),

  getAnalysis: (applicationId: number) => api.get<CandidateAnalysis>(`/smartbot/analysis/${applicationId}`),

  getSessionMessages: (sessionId: string) => api.get<SmartBotMessage[]>(`/smartbot/sessions/${sessionId}/messages`),
};

export default api;