import axios from 'axios';

// Use environment variable for API URL (falls back to localhost for development)
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`);
    console.log('Request config:', {
      method: config.method,
      baseURL: config.baseURL,
      url: config.url,
      fullURL: `${config.baseURL}${config.url}`,
      headers: config.headers,
      data: config.data
    });
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export interface GenerationRequest {
  target_role: string;
  experience_level: 'entry' | 'mid' | 'senior';
  job_description?: string;
  existing_resume?: any;
  preferences?: {
    format: string;
    style: string;
    length: 'short' | 'medium' | 'long';
  };
}

export interface ScreeningRequest {
  resume_data: any;
  job_data: any;
  explain?: boolean;
}

export interface ContentGenerationRequest {
  content_type: 'email' | 'cover_letter' | 'linkedin_prompt';
  target_role: string;
  company_name: string;
  tone?: 'professional' | 'friendly' | 'formal';
  additional_context?: string;
}

// API Functions
export const apiService = {
  // Basic HTTP methods
  get: (url: string, config = {}) => api.get(url, config),
  post: (url: string, data = {}, config = {}) => api.post(url, data, config),
  put: (url: string, data = {}, config = {}) => api.put(url, data, config),
  delete: (url: string, config = {}) => api.delete(url, config),

  // Health check
  healthCheck: () => api.get('/health'),

  // Resume generation
  generateResume: (request: GenerationRequest) => 
    api.post('/api/v1/generate/resume', request),

  // Resume download
  downloadResume: (resumeData: any) => 
    api.post('/api/v1/generate/resume/pdf', resumeData, {
      responseType: 'blob'
    }),

  // LaTeX-specific endpoints
  generateLatexResume: (data: any) => 
    api.post('/api/v1/generate/resume/latex', data),
  
  getLatexTemplates: () => 
    api.get('/api/v1/templates/latex'),
  
  compileLatexToPdf: (latexCode: string) => 
    api.post('/api/v1/generate/resume/latex/compile', { latex_code: latexCode }, {
      responseType: 'blob'
    }),
  
  parseLatexResume: (latexContent: string) => 
    api.post('/api/v1/parse/latex', { latex_content: latexContent }),

  // Resume screening
  screenResume: (request: ScreeningRequest) => 
    api.post('/api/v1/screen/resume', request),

  // Batch screening
  batchScreenResumes: (resumes: any[], jobData: any, explain = false) => 
    api.post('/api/v1/screen/batch', {
      resumes_data: resumes,
      job_data: jobData,
      explain
    }),

  // Content generation
  generateContent: (request: ContentGenerationRequest) => 
    api.post('/api/v1/generate/content', request),

  // Data generation
  generateSyntheticData: (numResumes = 100, numJobs = 50) => 
    api.post('/api/v1/data/generate', {
      num_resumes: numResumes,
      num_jobs: numJobs
    }),

  // Analytics
  getDataStats: () => api.get('/api/v1/data/stats'),
  evaluateModels: () => api.get('/api/v1/evaluate/models'),
};

export default api;