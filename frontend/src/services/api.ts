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
  location?: string;
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
  getResumes: () => api.get<Resume[]>('/resumes'),

  getResume: (id: number) => api.get<Resume>(`/resumes/${id}`),

  createResume: (data: {
    title: string;
    summary?: string;
    experience?: string;
    education?: string;
    skills?: string;
  }) => api.post<Resume>('/resumes', data),

  updateResume: (id: number, data: Partial<Resume>) =>
    api.put<Resume>(`/resumes/${id}`, data),

  deleteResume: (id: number) => api.delete(`/resumes/${id}`),
};

// Applications API
export const applicationsAPI = {
  getApplications: () => api.get<Application[]>('/applications'),

  getApplication: (id: number) => api.get<Application>(`/applications/${id}`),

  createApplication: (data: {
    job_id: number;
    resume_id: number;
    cover_letter?: string;
  }) => api.post<Application>('/applications', data),

  updateApplication: (id: number, data: {
    cover_letter?: string;
    status?: 'pending' | 'reviewed' | 'accepted' | 'rejected';
  }) => api.put<Application>(`/applications/${id}`, data),

  deleteApplication: (id: number) => api.delete(`/applications/${id}`),
};

// Chat API
export const chatAPI = {
  sendMessage: (data: { message: string; session_id?: string }) =>
    api.post<{ response: string; session_id: string }>('/chat/', data),

  getSession: (sessionId: string) => api.get<ChatSession>(`/chat/sessions/${sessionId}`),

  getSessions: () => api.get<ChatSession[]>('/chat/sessions'),
};

export default api;