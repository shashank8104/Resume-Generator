import React, { useState } from 'react';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { Textarea } from '../components/common/Textarea';
import { Loading } from '../components/common/Loading';
import { apiService } from '../services/api';
import type { ContentGenerationRequest } from '../services/api';

const contentTypes = [
  { value: 'email', label: 'Professional Email', icon: '📧', description: 'Reach out to recruiters and hiring managers' },
  { value: 'cover_letter', label: 'Cover Letter', icon: '📝', description: 'Compelling cover letter for job applications' },
  { value: 'linkedin_prompt', label: 'LinkedIn Message', icon: '💼', description: 'Professional LinkedIn connection request' },
];

const tones = [
  { value: 'professional', label: 'Professional', description: 'Formal and business-appropriate' },
  { value: 'friendly', label: 'Friendly', description: 'Warm and approachable' },
  { value: 'formal', label: 'Formal', description: 'Very formal and conservative' },
];

export const ContentGeneratorPage: React.FC = () => {
  const [formData, setFormData] = useState<ContentGenerationRequest>({
    content_type: 'email',
    target_role: '',
    company_name: '',
    tone: 'professional',
    additional_context: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string>('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.target_role || !formData.company_name) {
      setError('Please provide job title and company name');
      return;
    }

    setIsLoading(true);
    setError('');
    
    try {
      const response = await apiService.generateContent(formData);
      setResult(response.data);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to generate content');
    } finally {
      setIsLoading(false);
    }
  };

  const selectedContentType = contentTypes.find(t => t.value === formData.content_type);

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div className="text-center">
        <h1 className="section-title">Content Generator</h1>
        <p className="text-gray-600 mb-8">
          Generate professional emails, cover letters, and LinkedIn messages with AI.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Form */}
        <div className="space-y-6">
          {/* Content Type Selection */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Content Type</h3>
            <div className="grid grid-cols-1 gap-3">
              {contentTypes.map((type) => (
                <button
                  key={type.value}
                  type="button"
                  onClick={() => setFormData(prev => ({ ...prev, content_type: type.value as any }))}
                  className={`p-4 text-left border rounded-lg transition-colors ${
                    formData.content_type === type.value
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    <span className="text-xl">{type.icon}</span>
                    <div>
                      <div className="font-medium text-gray-900">{type.label}</div>
                      <div className="text-sm text-gray-600">{type.description}</div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Job Information */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Job Information</h3>
            <div className="space-y-4">
              <Input
                label="Job Title"
                value={formData.target_role}
                onChange={(e) => setFormData(prev => ({
                  ...prev,
                  target_role: e.target.value
                }))}
                placeholder="e.g., Senior Software Engineer"
                required
              />
              
              <Input
                label="Company Name"
                value={formData.company_name}
                onChange={(e) => setFormData(prev => ({
                  ...prev,
                  company_name: e.target.value
                }))}
                placeholder="e.g., TechCorp Inc."
                required
              />
            </div>
          </div>

          {/* Tone & Context */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Style & Context</h3>
            <div className="space-y-4">
              <div>
                <label className="label">Tone</label>
                <div className="grid grid-cols-1 gap-2">
                  {tones.map((tone) => (
                    <button
                      key={tone.value}
                      type="button"
                      onClick={() => setFormData(prev => ({ ...prev, tone: tone.value as any }))}
                      className={`p-3 text-left border rounded-lg text-sm transition-colors ${
                        formData.tone === tone.value
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-gray-200 hover:bg-gray-50'
                      }`}
                    >
                      <div className="font-medium">{tone.label}</div>
                      <div className="text-gray-600">{tone.description}</div>
                    </button>
                  ))}
                </div>
              </div>
              
              <Textarea
                label="Additional Context (Optional)"
                value={formData.additional_context || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, additional_context: e.target.value }))}
                placeholder="Any specific details, achievements, or context to include..."
                rows={3}
                helpText="Mention specific skills, experiences, or reasons for interest."
              />
            </div>
          </div>

          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          )}

          <Button onClick={handleSubmit} loading={isLoading} className="w-full">
            {isLoading ? 'Generating Content...' : `Generate ${selectedContentType?.label}`}
          </Button>
        </div>

        {/* Results */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Generated {selectedContentType?.label}
          </h3>
          
          {isLoading && (
            <Loading message={`Generating your ${selectedContentType?.label.toLowerCase()}...`} />
          )}

          {result && (
            <div className="space-y-4">
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-green-700 text-sm font-medium">
                  ✓ Content generated successfully!
                </p>
                <p className="text-green-600 text-sm mt-1">
                  Processing time: {result.execution_time?.toFixed(2)}s
                </p>
              </div>

              {result.data?.content && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex justify-between items-center mb-3">
                    <h4 className="font-medium text-gray-900">Generated Content</h4>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => navigator.clipboard.writeText(result.data.content)}
                    >
                      📋 Copy
                    </Button>
                  </div>
                  
                  <div className="whitespace-pre-wrap text-sm text-gray-700 leading-relaxed border border-gray-200 rounded p-3 bg-white">
                    {result.data.content}
                  </div>
                  
                  {result.data.subject && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <span className="text-sm font-medium text-gray-700">Subject: </span>
                      <span className="text-sm text-gray-600">{result.data.subject}</span>
                    </div>
                  )}
                </div>
              )}

              {result.data?.tips && result.data.tips.length > 0 && (
                <div className="bg-blue-50 rounded-lg p-4">
                  <h4 className="font-medium text-blue-900 mb-2">💡 Tips for Success</h4>
                  <ul className="space-y-1">
                    {result.data.tips.map((tip: string, idx: number) => (
                      <li key={idx} className="text-sm text-blue-800">• {tip}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {!isLoading && !result && (
            <div className="text-center py-12 text-gray-500">
              <div className="text-4xl mb-4">{selectedContentType?.icon}</div>
              <p>Configure the settings to generate {selectedContentType?.label.toLowerCase()}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};