import React, { useState, useEffect } from 'react';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { Loading } from '../components/common/Loading';
import { apiService } from '../services/api';

interface LaTeXTemplate {
  name: string;
  description: string;
  preview_image?: string;
  packages?: string[];
}

interface ColorScheme {
  name: string;
  description: string;
}

interface AnalystResumeData {
  personal_info: {
    full_name: string;
    phone: string;
    email: string;
    linkedin: string;
    github: string;
    leetcode?: string;
    portfolio?: string;
  };
  education: {
    university: string;
    graduation_date: string;
    degree: string;
    major: string;
  };
  technical_skills: {
    programming_languages: string;
    data_libraries: string;
    tools_platforms: string;
    core_skills: string;
    soft_skills: string;
  };
  projects: Array<{
    name: string;
    technologies: string;
    github_link?: string;
    date: string;
    description: string[];
  }>;
  internships: Array<{
    company: string;
    certificate_link?: string;
    location: string;
    position: string;
    dates: string;
    description: string[];
  }>;
  achievements: Array<{
    name: string;
    issuer: string;
    link?: string;
    date: string;
  }>;
}

interface LaTeXFormData {
  target_role: string;
  experience_level: 'entry' | 'mid' | 'senior';
  job_description: string;
  latex_template: string;
  color_scheme: string;
  personal_info?: {
    full_name: string;
    phone: string;
    email: string;
    linkedin: string;
    github: string;
    leetcode?: string;
    portfolio?: string;
  };
  education?: {
    university: string;
    graduation_date: string;
    degree: string;
    major: string;
  };
  technical_skills?: Array<{
    category: string;
    skills: string;
  }>;
  projects?: Array<{
    name: string;
    technologies: string;
    github_link?: string;
    date: string;
    description: string[];
  }>;
  internships?: Array<{
    company: string;
    location: string;
    position: string;
    dates: string;
    description: string[];
  }>;
  achievements?: Array<{
    name: string;
    issuer: string;
    link?: string;
    date: string;
  }>;
}

export const LaTeXGeneratorPage: React.FC = () => {
  const [formData, setFormData] = useState<LaTeXFormData>({
    target_role: 'Data Scientist',
    experience_level: 'mid',
    job_description: '',
    latex_template: 'analyst',
    color_scheme: 'blue',
    personal_info: {
      full_name: '',
      phone: '',
      email: '',
      linkedin: '',
      github: '',
      leetcode: '',
      portfolio: ''
    },
    education: {
      university: '',
      graduation_date: '',
      degree: '',
      major: ''
    },
    technical_skills: [
      { category: 'Programming Languages', skills: '' },
      { category: 'Tools & Platforms', skills: '' },
      { category: 'Core Data Skills', skills: '' },
      { category: 'Soft Skills', skills: '' }
    ],
    projects: [],
    internships: [],
    achievements: []
  });
  
  const [loading, setLoading] = useState(false);
  const [latexCode, setLatexCode] = useState<string>('');
  const [templates, setTemplates] = useState<Record<string, LaTeXTemplate>>({});
  const [colorSchemes, setColorSchemes] = useState<Record<string, ColorScheme>>({});
  const [resumeData, setResumeData] = useState<any>(null);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    setError(''); // Clear any previous errors
    loadTemplates();
    // Test backend connectivity
    testBackendConnection();
  }, []);

  const testBackendConnection = async () => {
    try {
      console.log('Testing backend connection...');
      const response = await apiService.healthCheck();
      console.log('Backend health check:', response.data);
    } catch (error) {
      console.error('Backend connection test failed:', error);
      setError('Cannot connect to backend server. Please check if the backend is running.');
    }
  };

  const loadTemplates = async () => {
    try {
      console.log('Loading LaTeX templates...');
      const response = await apiService.get('/api/v1/templates/latex');
      console.log('Templates response:', response.data);
      
      if (response.data.success) {
        setTemplates(response.data.data.templates || {});
        setColorSchemes(response.data.data.color_schemes || {});
        console.log('Templates loaded:', response.data.data.templates);
        console.log('Color schemes loaded:', response.data.data.color_schemes);
      } else {
        console.error('Failed to load templates:', response.data.message);
        setError('Failed to load LaTeX templates: ' + response.data.message);
      }
    } catch (error: any) {
      console.error('Failed to load templates:', error);
      setError('Failed to load LaTeX templates: ' + (error.response?.data?.detail || error.message));
      
      // Set default templates as fallback
      setTemplates({
        modern: {
          name: 'Modern Professional',
          description: 'Clean, modern design with color accents using moderncv package',
          packages: ['moderncv', 'geometry', 'inputenc']
        },
        academic: {
          name: 'Academic Research',
          description: 'Traditional academic format for research positions and academia',
          packages: ['geometry', 'enumitem', 'hyperref', 'xcolor', 'titlesec']
        },
        classic: {
          name: 'Classic Business',
          description: 'Traditional professional format for business and corporate roles',
          packages: ['geometry', 'enumitem', 'hyperref', 'titlesec']
        }
      });
      
      setColorSchemes({
        blue: { name: 'Professional Blue', description: 'Classic blue accent color' },
        green: { name: 'Forest Green', description: 'Natural green accent color' },
        red: { name: 'Crimson Red', description: 'Bold red accent color' },
        purple: { name: 'Royal Purple', description: 'Elegant purple accent color' },
        orange: { name: 'Warm Orange', description: 'Vibrant orange accent color' }
      });
    }
  };

  const testConnection = async () => {
    try {
      console.log('Testing backend connection...');
      const response = await apiService.get('/health');
      console.log('Health check response:', response);
      alert('Backend connection successful!');
    } catch (error: any) {
      console.error('Health check failed:', error);
      alert('Backend connection failed: ' + (error.message || 'Unknown error'));
    }
  };

  const generateLaTeXResume = async () => {
    if (!formData.target_role) {
      setError('Please enter a target role');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      console.log('Generating LaTeX resume with data:', formData);
      
      const requestData = {
        target_role: formData.target_role,
        experience_level: formData.experience_level,
        job_description: formData.job_description || undefined,
        preferences: {
          latex_template: 'analyst',
          color_scheme: formData.color_scheme
        },
        // Use actual form data for analyst resume
        personal_info: {
          full_name: formData.personal_info?.full_name || 'Your Name',
          phone: formData.personal_info?.phone || '+1-xxx-xxx-xxxx',
          email: formData.personal_info?.email || 'email@example.com',
          linkedin: formData.personal_info?.linkedin || 'https://linkedin.com/in/username',
          github: formData.personal_info?.github || 'https://github.com/username',
          leetcode: formData.personal_info?.leetcode || '',
          portfolio: formData.personal_info?.portfolio || ''
        },
        education: {
          university: formData.education?.university || 'University Name',
          graduation_date: formData.education?.graduation_date || 'Expected May 2026',
          degree: formData.education?.degree || 'Bachelor of Technology',
          major: formData.education?.major || 'Computer Science and Engineering'
        },
        technical_skills: (() => {
          const skillsObj: any = {};
          formData.technical_skills?.forEach((skill, index) => {
            if (skill.category && skill.skills) {
              // Convert category to snake_case key
              const key = skill.category.toLowerCase().replace(/[^a-z0-9]+/g, '_');
              skillsObj[key] = skill.skills;
            }
          });
          
          // Ensure we have at least some default structure
          return Object.keys(skillsObj).length > 0 ? skillsObj : {
            programming_languages: 'Python, JavaScript',
            tools_platforms: 'Excel, Power BI',
            core_skills: 'Data Analysis, Machine Learning',
            soft_skills: 'Analytical Reasoning, Communication'
          };
        })(),
        projects: formData.projects || [],
        internships: formData.internships || [],
        achievements: formData.achievements || []
      };
      
      console.log('Request payload:', requestData);
      console.log('API URL:', 'http://localhost:8000/api/v1/generate/resume/latex');
      
      const response = await apiService.post('/api/v1/generate/resume/latex', requestData);
      console.log('LaTeX generation response:', response);

      if (response.data && response.data.success) {
        setLatexCode(response.data.data.latex_source);
        setResumeData(response.data.data);
        console.log('LaTeX resume generated successfully:', response.data.data);
      } else {
        const errorMsg = response.data?.message || response.data?.detail || 'Unknown error occurred';
        console.error('LaTeX generation failed:', errorMsg);
        setError(errorMsg);
      }
    } catch (error: any) {
      console.error('Failed to generate LaTeX resume:', error);
      console.error('Error details:', {
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        config: error.config
      });
      
      let errorMessage = 'Failed to generate LaTeX resume';
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const downloadLatexSource = async () => {
    if (!latexCode) return;
    
    try {
      const blob = new Blob([latexCode], { type: 'application/x-tex' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `resume_${new Date().getTime()}.tex`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download LaTeX source:', error);
      setError('Failed to download LaTeX source');
    }
  };

  const compileToPdf = async () => {
    if (!latexCode) return;
    
    setLoading(true);
    try {
      const response = await apiService.post('/api/v1/generate/resume/latex/compile', {
        latex_code: latexCode
      }, {
        responseType: 'blob'
      });

      const blob = new Blob([response.data], { 
        type: response.headers['content-type'] || 'application/pdf' 
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // Get filename from header or use default
      const contentDisposition = response.headers['content-disposition'];
      let filename = `resume_${new Date().getTime()}.pdf`;
      if (contentDisposition) {
        const matches = /filename[^;=\\n]*=((['\"]).*?\\2|[^;\\n]*)/.exec(contentDisposition);
        if (matches != null && matches[1]) {
          filename = matches[1].replace(/['"]/g, '');
        }
      }
      
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error: any) {
      console.error('Failed to compile PDF:', error);
      setError('Failed to compile PDF. LaTeX compiler may not be installed on the server.');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: keyof LaTeXFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleNestedInputChange = (section: string, field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [section]: {
        ...prev[section as keyof LaTeXFormData],
        [field]: value
      }
    }));
  };

  const addArrayItem = (arrayName: 'projects' | 'internships' | 'achievements') => {
    setFormData(prev => {
      const currentArray = prev[arrayName] || [];
      let newItem: any = {};
      
      if (arrayName === 'projects') {
        newItem = { name: '', technologies: '', github_link: '', date: '', description: [] };
      } else if (arrayName === 'internships') {
        newItem = { company: '', location: '', position: '', dates: '', description: [] };
      } else if (arrayName === 'achievements') {
        newItem = { name: '', issuer: '', date: '', link: '' };
      }
      
      return {
        ...prev,
        [arrayName]: [...currentArray, newItem]
      };
    });
  };

  const removeArrayItem = (arrayName: 'projects' | 'internships' | 'achievements', index: number) => {
    setFormData(prev => {
      const currentArray = prev[arrayName] || [];
      return {
        ...prev,
        [arrayName]: currentArray.filter((_, i) => i !== index)
      };
    });
  };

  const handleArrayItemChange = (arrayName: 'projects' | 'internships' | 'achievements', index: number, field: string, value: any) => {
    setFormData(prev => {
      const currentArray = prev[arrayName] || [];
      const updatedArray = currentArray.map((item, i) => {
        if (i === index) {
          return { ...item, [field]: value };
        }
        return item;
      });
      
      return {
        ...prev,
        [arrayName]: updatedArray
      };
    });
  };

  const addSkillCategory = () => {
    setFormData(prev => ({
      ...prev,
      technical_skills: [...(prev.technical_skills || []), { category: '', skills: '' }]
    }));
  };

  const removeSkillCategory = (index: number) => {
    setFormData(prev => ({
      ...prev,
      technical_skills: (prev.technical_skills || []).filter((_, i) => i !== index)
    }));
  };

  const handleSkillCategoryChange = (index: number, field: string, value: string) => {
    setFormData(prev => {
      const updatedSkills = (prev.technical_skills || []).map((skill, i) => {
        if (i === index) {
          return { ...skill, [field]: value };
        }
        return skill;
      });
      
      return {
        ...prev,
        technical_skills: updatedSkills
      };
    });
  };

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-8">
      <div className="text-center">
        <h1 className="section-title">📄 LaTeX Resume Generator</h1>
        <p className="text-gray-600 mb-8">
          Generate professional LaTeX resumes with customizable templates. Download both source code and compiled PDF.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Input Form */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-6">Resume Configuration</h2>
          
          <div className="space-y-6">
            <Input
              label="Target Role"
              value={formData.target_role}
              onChange={(e) => handleInputChange('target_role', e.target.value)}
              placeholder="e.g., Software Engineer, Data Scientist, Product Manager"
              required
            />

            <div>
              <label className="label">Experience Level</label>
              <select
                value={formData.experience_level}
                onChange={(e) => handleInputChange('experience_level', e.target.value)}
                className="input-field"
              >
                <option value="entry">Entry Level (0-2 years)</option>
                <option value="mid">Mid Level (3-7 years)</option>
                <option value="senior">Senior Level (8+ years)</option>
              </select>
            </div>

            <div>
              <label className="label">LaTeX Template</label>
              {Object.keys(templates).length > 0 ? (
                <div className="grid grid-cols-1 gap-3">
                  {Object.entries(templates).map(([key, template]) => (
                    <label key={key} className={`flex items-start p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors ${
                      formData.latex_template === key ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
                    }`}>
                      <input
                        type="radio"
                        name="latex_template"
                        value={key}
                        checked={formData.latex_template === key}
                        onChange={(e) => handleInputChange('latex_template', e.target.value)}
                        className="mt-1 mr-3 text-blue-600"
                      />
                      <div className="flex-1">
                        <div className="font-medium text-gray-900">{template.name}</div>
                        <div className="text-sm text-gray-600 mb-2">{template.description}</div>
                        {template.packages && (
                          <div className="text-xs text-gray-500">
                            <strong>Packages:</strong> {template.packages.join(', ')}
                          </div>
                        )}
                      </div>
                    </label>
                  ))}
                </div>
              ) : (
                <div className="p-4 border border-gray-300 rounded-lg bg-gray-50">
                  <div className="text-sm text-gray-600">Loading templates...</div>
                </div>
              )}
            </div>

            <div>
              <label className="label">Color Scheme</label>
              {Object.keys(colorSchemes).length > 0 ? (
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(colorSchemes).map(([key, scheme]) => (
                    <label key={key} className={`flex items-center p-3 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors ${
                      formData.color_scheme === key ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
                    }`}>
                      <input
                        type="radio"
                        name="color_scheme"
                        value={key}
                        checked={formData.color_scheme === key}
                        onChange={(e) => handleInputChange('color_scheme', e.target.value)}
                        className="mr-3 text-blue-600"
                      />
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-sm truncate">{scheme.name}</div>
                        <div className="text-xs text-gray-500 truncate">{scheme.description}</div>
                      </div>
                    </label>
                  ))}
                </div>
              ) : (
                <div className="p-3 border border-gray-300 rounded-lg bg-gray-50">
                  <div className="text-sm text-gray-600">Loading color schemes...</div>
                </div>
              )}
            </div>

            {/* Personal Information Section */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-lg font-semibold mb-4 text-gray-800">Personal Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="Full Name"
                  value={formData.personal_info?.full_name || ''}
                  onChange={(e) => handleNestedInputChange('personal_info', 'full_name', e.target.value)}
                  placeholder="John Doe"
                  required
                />
                <Input
                  label="Phone"
                  value={formData.personal_info?.phone || ''}
                  onChange={(e) => handleNestedInputChange('personal_info', 'phone', e.target.value)}
                  placeholder="+1-xxx-xxx-xxxx"
                />
                <Input
                  label="Email"
                  type="email"
                  value={formData.personal_info?.email || ''}
                  onChange={(e) => handleNestedInputChange('personal_info', 'email', e.target.value)}
                  placeholder="email@example.com"
                  required
                />
                <Input
                  label="LinkedIn URL"
                  value={formData.personal_info?.linkedin || ''}
                  onChange={(e) => handleNestedInputChange('personal_info', 'linkedin', e.target.value)}
                  placeholder="https://linkedin.com/in/username"
                />
                <Input
                  label="GitHub URL"
                  value={formData.personal_info?.github || ''}
                  onChange={(e) => handleNestedInputChange('personal_info', 'github', e.target.value)}
                  placeholder="https://github.com/username"
                />
                <Input
                  label="LeetCode URL (Optional)"
                  value={formData.personal_info?.leetcode || ''}
                  onChange={(e) => handleNestedInputChange('personal_info', 'leetcode', e.target.value)}
                  placeholder="https://leetcode.com/username"
                />
                <Input
                  label="Portfolio URL (Optional)"
                  value={formData.personal_info?.portfolio || ''}
                  onChange={(e) => handleNestedInputChange('personal_info', 'portfolio', e.target.value)}
                  placeholder="https://portfolio.com"
                />
              </div>
            </div>

            {/* Education Section */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-lg font-semibold mb-4 text-gray-800">Education</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="University"
                  value={formData.education?.university || ''}
                  onChange={(e) => handleNestedInputChange('education', 'university', e.target.value)}
                  placeholder="University Name"
                  required
                />
                <Input
                  label="Graduation Date"
                  value={formData.education?.graduation_date || ''}
                  onChange={(e) => handleNestedInputChange('education', 'graduation_date', e.target.value)}
                  placeholder="Expected May 2026"
                />
                <Input
                  label="Degree"
                  value={formData.education?.degree || ''}
                  onChange={(e) => handleNestedInputChange('education', 'degree', e.target.value)}
                  placeholder="Bachelor of Technology"
                />
                <Input
                  label="Major"
                  value={formData.education?.major || ''}
                  onChange={(e) => handleNestedInputChange('education', 'major', e.target.value)}
                  placeholder="Computer Science and Engineering"
                />
              </div>
            </div>

            {/* Technical Skills Section */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-800">Technical Skills</h3>
                <button
                  type="button"
                  onClick={() => addSkillCategory()}
                  className="px-3 py-1 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700"
                >
                  + Add Skill Category
                </button>
              </div>
              <div className="space-y-3">
                {formData.technical_skills?.map((skill, index) => (
                  <div key={index} className="flex gap-3 items-end">
                    <div className="flex-1">
                      <Input
                        label="Category"
                        value={skill.category || ''}
                        onChange={(e) => handleSkillCategoryChange(index, 'category', e.target.value)}
                        placeholder="e.g., Programming Languages, Frameworks"
                      />
                    </div>
                    <div className="flex-2 min-w-0">
                      <Input
                        label="Skills"
                        value={skill.skills || ''}
                        onChange={(e) => handleSkillCategoryChange(index, 'skills', e.target.value)}
                        placeholder="Python, JavaScript, React, Node.js"
                      />
                    </div>
                    <button
                      type="button"
                      onClick={() => removeSkillCategory(index)}
                      className="mb-2 px-2 py-1 text-red-600 hover:text-red-800 text-sm border border-red-300 rounded-md hover:bg-red-50"
                    >
                      Remove
                    </button>
                  </div>
                ))}
                {(!formData.technical_skills || formData.technical_skills.length === 0) && (
                  <p className="text-gray-500 text-center py-4">No skill categories added yet. Click "Add Skill Category" to get started.</p>
                )}
              </div>
            </div>

            {/* Projects Section */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-800">Projects</h3>
                <button
                  type="button"
                  onClick={() => addArrayItem('projects')}
                  className="px-3 py-1 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700"
                >
                  + Add Project
                </button>
              </div>
              {formData.projects?.map((project, index) => (
                <div key={index} className="mb-4 p-4 bg-white rounded-lg border border-gray-200">
                  <div className="flex justify-between items-center mb-3">
                    <h4 className="font-medium text-gray-700">Project {index + 1}</h4>
                    <button
                      type="button"
                      onClick={() => removeArrayItem('projects', index)}
                      className="text-red-600 hover:text-red-800 text-sm"
                    >
                      Remove
                    </button>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                    <Input
                      label="Project Name"
                      value={project.name || ''}
                      onChange={(e) => handleArrayItemChange('projects', index, 'name', e.target.value)}
                      placeholder="My Awesome Project"
                    />
                    <Input
                      label="Technologies"
                      value={project.technologies || ''}
                      onChange={(e) => handleArrayItemChange('projects', index, 'technologies', e.target.value)}
                      placeholder="Python, React, Node.js"
                    />
                    <Input
                      label="GitHub Link (Optional)"
                      value={project.github_link || ''}
                      onChange={(e) => handleArrayItemChange('projects', index, 'github_link', e.target.value)}
                      placeholder="https://github.com/username/project"
                    />
                    <Input
                      label="Date"
                      value={project.date || ''}
                      onChange={(e) => handleArrayItemChange('projects', index, 'date', e.target.value)}
                      placeholder="January 2026"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Description (one point per line)
                    </label>
                    <textarea
                      value={project.description?.join('\n') || ''}
                      onChange={(e) => handleArrayItemChange('projects', index, 'description', e.target.value.split('\n'))}
                      placeholder="Built a web application using modern frameworks&#10;Implemented user authentication and authorization&#10;Deployed to cloud platform with CI/CD"
                      rows={3}
                      className="input-field"
                    />
                  </div>
                </div>
              ))}
              {(!formData.projects || formData.projects.length === 0) && (
                <p className="text-gray-500 text-center py-4">No projects added yet. Click "Add Project" to get started.</p>
              )}
            </div>

            {/* Internships Section */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-800">Internships</h3>
                <button
                  type="button"
                  onClick={() => addArrayItem('internships')}
                  className="px-3 py-1 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700"
                >
                  + Add Internship
                </button>
              </div>
              {formData.internships?.map((internship, index) => (
                <div key={index} className="mb-4 p-4 bg-white rounded-lg border border-gray-200">
                  <div className="flex justify-between items-center mb-3">
                    <h4 className="font-medium text-gray-700">Internship {index + 1}</h4>
                    <button
                      type="button"
                      onClick={() => removeArrayItem('internships', index)}
                      className="text-red-600 hover:text-red-800 text-sm"
                    >
                      Remove
                    </button>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                    <Input
                      label="Company"
                      value={internship.company || ''}
                      onChange={(e) => handleArrayItemChange('internships', index, 'company', e.target.value)}
                      placeholder="Tech Company Inc."
                    />
                    <Input
                      label="Location"
                      value={internship.location || ''}
                      onChange={(e) => handleArrayItemChange('internships', index, 'location', e.target.value)}
                      placeholder="San Francisco, CA"
                    />
                    <Input
                      label="Position"
                      value={internship.position || ''}
                      onChange={(e) => handleArrayItemChange('internships', index, 'position', e.target.value)}
                      placeholder="Software Engineering Intern"
                    />
                    <Input
                      label="Dates"
                      value={internship.dates || ''}
                      onChange={(e) => handleArrayItemChange('internships', index, 'dates', e.target.value)}
                      placeholder="June 2025 - August 2025"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Description (one point per line)
                    </label>
                    <textarea
                      value={internship.description?.join('\n') || ''}
                      onChange={(e) => handleArrayItemChange('internships', index, 'description', e.target.value.split('\n'))}
                      placeholder="Developed web applications using React and Node.js&#10;Collaborated with senior developers on code reviews&#10;Implemented automated testing procedures"
                      rows={3}
                      className="input-field"
                    />
                  </div>
                </div>
              ))}
              {(!formData.internships || formData.internships.length === 0) && (
                <p className="text-gray-500 text-center py-4">No internships added yet. Click "Add Internship" to get started.</p>
              )}
            </div>

            {/* Achievements Section */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-800">Achievements & Certifications</h3>
                <button
                  type="button"
                  onClick={() => addArrayItem('achievements')}
                  className="px-3 py-1 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700"
                >
                  + Add Achievement
                </button>
              </div>
              {formData.achievements?.map((achievement, index) => (
                <div key={index} className="mb-4 p-4 bg-white rounded-lg border border-gray-200">
                  <div className="flex justify-between items-center mb-3">
                    <h4 className="font-medium text-gray-700">Achievement {index + 1}</h4>
                    <button
                      type="button"
                      onClick={() => removeArrayItem('achievements', index)}
                      className="text-red-600 hover:text-red-800 text-sm"
                    >
                      Remove
                    </button>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <Input
                      label="Achievement/Certification Name"
                      value={achievement.name || ''}
                      onChange={(e) => handleArrayItemChange('achievements', index, 'name', e.target.value)}
                      placeholder="AWS Certified Solutions Architect"
                    />
                    <Input
                      label="Issuing Organization"
                      value={achievement.issuer || ''}
                      onChange={(e) => handleArrayItemChange('achievements', index, 'issuer', e.target.value)}
                      placeholder="Amazon Web Services"
                    />
                    <Input
                      label="Date"
                      value={achievement.date || ''}
                      onChange={(e) => handleArrayItemChange('achievements', index, 'date', e.target.value)}
                      placeholder="December 2025"
                    />
                    <Input
                      label="Certificate Link (Optional)"
                      value={achievement.link || ''}
                      onChange={(e) => handleArrayItemChange('achievements', index, 'link', e.target.value)}
                      placeholder="https://certificate-url.com"
                    />
                  </div>
                </div>
              ))}
              {(!formData.achievements || formData.achievements.length === 0) && (
                <p className="text-gray-500 text-center py-4">No achievements added yet. Click "Add Achievement" to get started.</p>
              )}
            </div>

            <div>
              <label className="label">Job Description (Optional)</label>
              <textarea
                value={formData.job_description}
                onChange={(e) => handleInputChange('job_description', e.target.value)}
                placeholder="Paste job description to tailor your resume for specific requirements..."
                rows={6}
                className="input-field"
              />
              <p className="text-sm text-gray-500 mt-1">
                Providing a job description will help optimize the resume content and keywords
              </p>
            </div>

            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-600 text-sm font-medium">Error:</p>
                <p className="text-red-600 text-sm">{error}</p>
                <button 
                  onClick={() => setError('')} 
                  className="mt-2 text-xs text-red-500 underline hover:text-red-700"
                >
                  Dismiss
                </button>
              </div>
            )}

            <div className="space-y-3">
              <Button
                onClick={testConnection}
                className="w-full bg-blue-600 hover:bg-blue-700"
              >
                Test Backend Connection
              </Button>
              <Button
                onClick={generateLaTeXResume}
                disabled={loading || !formData.target_role}
                loading={loading}
                className="w-full"
              >
                {loading ? 'Generating LaTeX Resume...' : '🚀 Generate LaTeX Resume'}
              </Button>
            </div>
          </div>
        </div>

        {/* Generated Output */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-6">Generated LaTeX Resume</h2>
          
          {latexCode ? (
            <div className="space-y-6">
              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-3">
                <Button
                  onClick={downloadLatexSource}
                  variant="secondary"
                  className="flex-1"
                >
                  📄 Download .tex Source
                </Button>
                <Button
                  onClick={compileToPdf}
                  disabled={loading}
                  loading={loading}
                  className="flex-1"
                >
                  📎 Compile to PDF
                </Button>
              </div>

              {/* Resume Data Preview */}
              {resumeData && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <h3 className="font-medium text-green-800 mb-2">✅ Resume Generated Successfully</h3>
                  <div className="text-sm text-green-700 space-y-1">
                    <p><strong>Template:</strong> {resumeData.template_info?.name || formData.latex_template}</p>
                    <p><strong>Color:</strong> {colorSchemes[formData.color_scheme]?.name || formData.color_scheme}</p>
                    <p><strong>ATS Score:</strong> {((resumeData.metadata?.ats_compliance_score || 0) * 100).toFixed(1)}%</p>
                    <p><strong>Processing Time:</strong> {resumeData.execution_time?.toFixed(2)}s</p>
                  </div>
                </div>
              )}

              {/* LaTeX Code Preview */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-medium text-gray-700">LaTeX Source Code</h3>
                  <span className="text-xs text-gray-500">{latexCode.length} characters</span>
                </div>
                <pre className="bg-gray-100 p-4 rounded-lg text-sm overflow-auto max-h-96 border font-mono">
                  <code>{latexCode}</code>
                </pre>
              </div>

            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <div className="text-4xl mb-4">📄</div>
              <p className="mb-2">Generate a LaTeX resume to see the source code</p>
              <p className="text-sm">Fill out the form and click "Generate LaTeX Resume"</p>
            </div>
          )}
        </div>
      </div>

      {/* Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="font-semibold text-blue-800 mb-4">🔧 How to Use LaTeX Files</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-blue-700">
          <div>
            <h4 className="font-medium mb-2">📱 Online Editors (Recommended)</h4>
            <ul className="space-y-1 text-sm">
              <li><strong>• Overleaf:</strong> overleaf.com - No setup required</li>
              <li><strong>• TeXstudio Online:</strong> Web-based LaTeX editor</li>
              <li><strong>• ShareLaTeX:</strong> Collaborative editing</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium mb-2">💻 Desktop Editors</h4>
            <ul className="space-y-1 text-sm">
              <li><strong>• TeXworks:</strong> Cross-platform LaTeX editor</li>
              <li><strong>• TeXstudio:</strong> Advanced LaTeX IDE</li>
              <li><strong>• VS Code:</strong> With LaTeX Workshop extension</li>
            </ul>
          </div>
        </div>
        <div className="mt-4 pt-4 border-t border-blue-200">
          <p className="text-blue-700 text-sm">
            <strong>💡 Pro Tip:</strong> Upload the .tex file to Overleaf for instant compilation and editing. 
            No LaTeX installation required!
          </p>
        </div>
      </div>
    </div>
  );
};

export default LaTeXGeneratorPage;