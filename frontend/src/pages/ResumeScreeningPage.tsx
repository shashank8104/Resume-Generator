import React, { useState } from 'react';
import { Button } from '../components/common/Button';
import { Textarea } from '../components/common/Textarea';
import { Loading } from '../components/common/Loading';
import { apiService } from '../services/api';
import type { ScreeningResult } from '../types';

export const ResumeScreeningPage: React.FC = () => {
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [resumeText, setResumeText] = useState('');
  const [useTextInput, setUseTextInput] = useState(false);
  const [jobDescription, setJobDescription] = useState('');
  const [explainResults, setExplainResults] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ScreeningResult | null>(null);
  const [error, setError] = useState<string>('');
  const [isDragOver, setIsDragOver] = useState(false);

  const handleFileSelect = (file: File) => {
    if (file && file.type === 'application/pdf') {
      setResumeFile(file);
      setError('');
    } else {
      setError('Please select a valid PDF file');
      setResumeFile(null);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFileSelect(file);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if ((!resumeFile && !resumeText) || !jobDescription) {
      setError('Please provide both a resume (PDF or text) and job description');
      return;
    }

    setIsLoading(true);
    setError('');
    
    try {
      console.log('Starting screening...');
      
      if (useTextInput || !resumeFile) {
        // Use text-based screening
        console.log('Using text-based screening');
        
        const response = await fetch('http://localhost:8000/api/v1/screen/resume', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            resume_data: {
              content: resumeText,
              parsed: true
            },
            job_data: {
              description: jobDescription,
              title: 'Target Position'
            },
            explain: explainResults
          }),
        });

        console.log('Text screening response status:', response.status);
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error('Text screening error:', errorText);
          throw new Error(`Server error: ${response.status} - ${errorText}`);
        }

        const data = await response.json();
        console.log('Text screening data:', data);
        
        if (data.success) {
          // Add ATS score calculation
          const atsScore = Math.min(100, Math.max(0, data.data.overall_score * 10));
          data.data.ats_score = Math.round(atsScore * 10) / 10;
          setResult(data.data);
          console.log('Text screening results set successfully');
        } else {
          throw new Error(data.message || 'Unknown API error');
        }
      } else {
        // Try PDF-based screening first, fallback to text if it fails
        console.log('Using PDF-based screening');
        console.log('PDF file:', resumeFile);
        
        const formData = new FormData();
        formData.append('resume_pdf', resumeFile);
        formData.append('job_description', jobDescription);
        formData.append('explain', explainResults.toString());

        console.log('Making PDF API call to:', 'http://localhost:8000/api/v1/screen/pdf');
        
        const response = await fetch('http://localhost:8000/api/v1/screen/pdf', {
          method: 'POST',
          body: formData,
        });

        console.log('PDF response status:', response.status);

        if (!response.ok) {
          const errorText = await response.text();
          console.error('PDF API Error:', errorText);
          throw new Error(`PDF processing failed. Please switch to text input mode.`);
        }

        const data = await response.json();
        console.log('PDF response data:', data);
        
        if (data.success) {
          setResult(data.data);
          console.log('PDF results set successfully');
        } else {
          throw new Error(data.message || 'PDF processing failed');
        }
      }
    } catch (error: any) {
      console.error('Screening error:', error);
      if (error.message.includes('PDF processing failed') && resumeFile && !useTextInput) {
        setError(error.message + ' Click "Use Text Input Instead" below to try manual text entry.');
      } else {
        setError(error.message || 'Failed to screen resume');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const getScoreColor = (score: number, maxScore: number) => {
    const percentage = (score / maxScore) * 100;
    if (percentage >= 80) return 'text-green-600 bg-green-100';
    if (percentage >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getRatingColor = (rating: string) => {
    switch (rating) {
      case 'excellent': return 'text-green-600 bg-green-100';
      case 'good': return 'text-blue-600 bg-blue-100';
      case 'fair': return 'text-yellow-600 bg-yellow-100';
      case 'poor': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div className="text-center">
        <h1 className="section-title">Resume Screening</h1>
        <p className="text-gray-600 mb-8">
          Get AI-powered analysis of how well a resume matches a job description.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Input Form */}
        <div className="space-y-6">
          <div className="card">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Resume Input Section - PDF or Text */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <label className="block text-sm font-medium text-gray-700">
                    Resume Input
                  </label>
                  <button
                    type="button"
                    onClick={() => {
                      setUseTextInput(!useTextInput);
                      setResumeFile(null);
                      setResumeText('');
                      setError('');
                    }}
                    className="text-sm text-blue-600 hover:text-blue-700 underline"
                  >
                    {useTextInput ? 'Upload PDF Instead' : 'Use Text Input Instead'}
                  </button>
                </div>

                {useTextInput ? (
                  // Text Input
                  <div>
                    <textarea
                      value={resumeText}
                      onChange={(e) => setResumeText(e.target.value)}
                      placeholder="Paste your resume text here..."
                      rows={10}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      required
                    />
                    <p className="text-xs text-gray-500 mt-2">
                      Copy and paste your resume text here for analysis.
                    </p>
                  </div>
                ) : (
                  // PDF Upload
                  <div
                    className={`relative border-2 border-dashed rounded-lg p-6 transition-colors ${
                      isDragOver
                        ? 'border-blue-400 bg-blue-50'
                        : resumeFile
                        ? 'border-green-400 bg-green-50'
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                    onDrop={handleDrop}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                  >
                    <div className="text-center">
                      {resumeFile ? (
                        <>
                          <div className="text-4xl mb-4">📄</div>
                          <p className="text-sm font-medium text-green-700 mb-2">
                            {resumeFile.name}
                          </p>
                          <p className="text-xs text-green-600 mb-4">
                            {(resumeFile.size / 1024 / 1024).toFixed(2)} MB
                          </p>
                          <button
                            type="button"
                            onClick={() => setResumeFile(null)}
                            className="text-sm text-red-600 hover:text-red-700 underline"
                          >
                            Remove file
                          </button>
                        </>
                      ) : (
                        <>
                          <div className="text-4xl mb-4">📤</div>
                          <p className="text-sm text-gray-600 mb-2">
                            Drag and drop your resume PDF here, or
                          </p>
                          <input
                            type="file"
                            accept=".pdf"
                            onChange={(e) => {
                              const file = e.target.files?.[0];
                              if (file) handleFileSelect(file);
                            }}
                            className="hidden"
                            id="resume-upload"
                          />
                          <label
                            htmlFor="resume-upload"
                            className="cursor-pointer text-blue-600 hover:text-blue-700 underline"
                          >
                            click to browse
                          </label>
                          <p className="text-xs text-gray-400 mt-2">
                            PDF files up to 10MB
                          </p>
                        </>
                      )}
                    </div>
                  </div>
                )}

                <p className="text-xs text-gray-500 mt-2">
                  {useTextInput 
                    ? 'Paste your resume text for direct analysis.' 
                    : 'Upload your resume in PDF format for automatic text extraction and ATS analysis.'
                  }
                </p>
              </div>

              <Textarea
                label="Job Description"
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste the job description here..."
                rows={8}
                required
                helpText="Provide the complete job description including requirements and qualifications."
              />

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="explain"
                  checked={explainResults}
                  onChange={(e) => setExplainResults(e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="explain" className="ml-2 text-sm text-gray-700">
                  Generate detailed explanations and improvement suggestions
                </label>
              </div>

              {error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-red-600 text-sm">{error}</p>
                </div>
              )}

              <Button type="submit" loading={isLoading} className="w-full">
                {isLoading ? 'Analyzing Resume...' : 'Screen Resume'}
              </Button>
            </form>
          </div>
        </div>

        {/* Results */}
        <div className="space-y-6">
          {isLoading && (
            <div className="card">
              <Loading message="Analyzing resume against job requirements..." />
            </div>
          )}

          {result && (
            <div className="space-y-6">
              {/* ATS Score */}
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">ATS Compatibility Score</h3>
                <div className="text-center">
                  <div className={`inline-flex items-center px-6 py-3 rounded-full text-2xl font-bold ${getScoreColor(result.ats_score || result.overall_score * 10, 100)}`}>
                    {Math.round(result.ats_score || result.overall_score * 10)}/100
                  </div>
                  <p className="text-sm text-gray-600 mt-2">
                    Your resume's compatibility with this job posting
                  </p>
                </div>
              </div>

              {/* Overall Rating */}
              {result.overall_rating && (
                <div className="card">
                  <h3 className="text-lg font-semibold mb-4">Overall Rating</h3>
                  <div className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium ${getRatingColor(result.overall_rating)}`}>
                    {result.overall_rating.toUpperCase()}
                  </div>
                  {result.summary && (
                    <p className="text-gray-600 mt-3">{result.summary}</p>
                  )}
                </div>
              )}

              {/* Skills Analysis */}
              {result.skills_analysis && (
                <div className="card">
                  <h3 className="text-lg font-semibold mb-4">Skills Analysis</h3>
                  
                  {result.skills_analysis.matched_skills && result.skills_analysis.matched_skills.length > 0 && (
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-green-700 mb-2">✅ Matched Skills</h4>
                      <div className="flex flex-wrap gap-2">
                        {result.skills_analysis.matched_skills.map((skill, index) => (
                          <span key={index} className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {result.skills_analysis.missing_skills && result.skills_analysis.missing_skills.length > 0 && (
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-red-700 mb-2">❌ Missing Skills</h4>
                      <div className="flex flex-wrap gap-2">
                        {result.skills_analysis.missing_skills.map((skill, index) => (
                          <span key={index} className="px-2 py-1 bg-red-100 text-red-700 text-xs rounded-full">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {result.skills_analysis.additional_skills && result.skills_analysis.additional_skills.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-blue-700 mb-2">💡 Additional Skills</h4>
                      <div className="flex flex-wrap gap-2">
                        {result.skills_analysis.additional_skills.map((skill, index) => (
                          <span key={index} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Recommendations */}
              {result.recommendations && result.recommendations.length > 0 && (
                <div className="card">
                  <h3 className="text-lg font-semibold mb-4">💡 Recommendations</h3>
                  <ul className="space-y-2">
                    {result.recommendations.map((rec, index) => (
                      <li key={index} className="flex items-start space-x-2">
                        <span className="text-blue-500 mt-1">•</span>
                        <span className="text-gray-700">{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Detailed Explanation */}
              {result.explanation && (
                <div className="card">
                  <h3 className="text-lg font-semibold mb-4">📋 Detailed Analysis</h3>
                  <div className="prose prose-sm max-w-none">
                    <p className="text-gray-700 whitespace-pre-wrap">{result.explanation}</p>
                  </div>
                </div>
              )}
            </div>
          )}

          {!result && !isLoading && (
            <div className="card text-center py-12">
              <div className="text-6xl mb-4">🎯</div>
              <h3 className="text-lg font-semibold mb-2">Upload Resume PDF for ATS Analysis</h3>
              <p className="text-sm text-gray-600">Upload your resume PDF and job description to get your ATS compatibility score</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};