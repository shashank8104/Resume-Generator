export interface ContactInfo {
  full_name: string;
  email: string;
  phone?: string;
  location: string;
  linkedin?: string;
  github?: string;
  website?: string;
}

export interface WorkExperience {
  job_title: string;
  company: string;
  location: string;
  start_date: string;
  end_date?: string;
  description: string;
  achievements: string[];
  technologies?: string[];
}

export interface Education {
  degree: string;
  institution: string;
  location: string;
  graduation_date: string;
  gpa?: number;
  relevant_coursework?: string[];
}

export interface Project {
  name: string;
  description: string;
  technologies: string[];
  start_date: string;
  end_date?: string;
  repository_url?: string;
  live_url?: string;
  achievements: string[];
}

export interface Resume {
  contact_info: ContactInfo;
  summary?: string;
  skills: Record<string, string[]>;
  work_experience: WorkExperience[];
  education: Education[];
  projects: Project[];
  certifications?: string[];
  languages?: string[];
}

export interface JobDescription {
  title: string;
  company: string;
  location: string;
  job_type: 'full_time' | 'part_time' | 'contract' | 'remote';
  experience_level: 'entry' | 'mid' | 'senior' | 'executive';
  description: string;
  requirements: string[];
  preferred_qualifications?: string[];
  salary_range?: {
    min: number;
    max: number;
    currency: string;
  };
  benefits?: string[];
  skills_required: string[];
  industry: string;
}

export interface SectionScore {
  section_name: string;
  score: number;
  max_score: number;
  feedback: string;
  missing_keywords: string[];
  suggestions: string[];
}

export interface ScreeningResult {
  overall_score: number;
  overall_rating: 'excellent' | 'good' | 'fair' | 'poor';
  section_scores: SectionScore[];
  key_strengths: string[];
  improvement_areas: string[];
  recommendation: string;
  detailed_analysis: {
    keyword_match_rate: number;
    experience_relevance: number;
    skill_alignment: number;
    education_match: number;
  };
}

export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  message: string;
  execution_time: number;
  session_id: string;
}

export interface LoadingState {
  isLoading: boolean;
  message?: string;
}

export interface ErrorState {
  hasError: boolean;
  message?: string;
  code?: string;
}