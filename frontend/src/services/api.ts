import axios from 'axios';
import { API_BASE_URL, getAuthHeaders } from '../utils/auth';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth headers
api.interceptors.request.use((config) => {
  const authHeaders = getAuthHeaders();
  Object.assign(config.headers, authHeaders);
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Only redirect if it's not a login attempt
      if (!error.config?.url?.includes('/auth/login')) {
        // Token expired or invalid - only redirect for authenticated routes
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
