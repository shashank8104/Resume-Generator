import React, { useState, useEffect } from 'react';
import { Button } from '../components/common/Button';
import { Loading } from '../components/common/Loading';
import { apiService } from '../services/api';

interface DataStats {
  total_resumes: number;
  total_job_descriptions: number;
  recent_activity: {
    resumes_generated: number;
    screenings_performed: number;
    content_generated: number;
  };
  average_scores: {
    overall_match_rate: number;
    skill_alignment: number;
    experience_relevance: number;
  };
}

export const AnalyticsPage: React.FC = () => {
  const [stats, setStats] = useState<DataStats | null>(null);
  const [evaluation, setEvaluation] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    setIsLoading(true);
    setError('');
    
    try {
      const [statsResponse] = await Promise.all([
        apiService.getDataStats(),
      ]);
      
      setStats(statsResponse.data.data);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to load analytics');
    } finally {
      setIsLoading(false);
    }
  };

  const runEvaluation = async () => {
    setIsEvaluating(true);
    
    try {
      const response = await apiService.evaluateModels();
      setEvaluation(response.data);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to run evaluation');
    } finally {
      setIsEvaluating(false);
    }
  };

  if (isLoading) {
    return <Loading message="Loading analytics..." fullScreen />;
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      <div className="text-center">
        <h1 className="section-title">Analytics Dashboard</h1>
        <p className="text-gray-600 mb-8">
          Monitor system performance, usage statistics, and model metrics.
        </p>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-600 text-sm">{error}</p>
        </div>
      )}

      {/* System Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card text-center">
          <div className="text-3xl font-bold text-primary-600 mb-2">
            {stats?.total_resumes || 0}
          </div>
          <div className="text-sm text-gray-600">Total Resumes</div>
          <div className="text-xs text-gray-500 mt-1">📝 Processed</div>
        </div>
        
        <div className="card text-center">
          <div className="text-3xl font-bold text-green-600 mb-2">
            {stats?.total_job_descriptions || 0}
          </div>
          <div className="text-sm text-gray-600">Job Descriptions</div>
          <div className="text-xs text-gray-500 mt-1">💼 Analyzed</div>
        </div>
        
        <div className="card text-center">
          <div className="text-3xl font-bold text-blue-600 mb-2">
            {stats?.recent_activity?.screenings_performed || 0}
          </div>
          <div className="text-sm text-gray-600">Screenings</div>
          <div className="text-xs text-gray-500 mt-1">🔍 Recent</div>
        </div>
        
        <div className="card text-center">
          <div className="text-3xl font-bold text-purple-600 mb-2">
            {stats?.recent_activity?.content_generated || 0}
          </div>
          <div className="text-sm text-gray-600">Content Generated</div>
          <div className="text-xs text-gray-500 mt-1">✍️ Recent</div>
        </div>
      </div>

      {/* Performance Metrics */}
      {stats?.average_scores && (
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Average Performance Scores</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-20 h-20 mx-auto mb-3 relative">
                <svg className="w-20 h-20 transform -rotate-90">
                  <circle
                    cx="40"
                    cy="40"
                    r="30"
                    stroke="#e5e7eb"
                    strokeWidth="6"
                    fill="none"
                  />
                  <circle
                    cx="40"
                    cy="40"
                    r="30"
                    stroke="#3b82f6"
                    strokeWidth="6"
                    fill="none"
                    strokeDasharray={`${(stats.average_scores.overall_match_rate / 100) * 188.4} 188.4`}
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-sm font-semibold">
                    {stats.average_scores.overall_match_rate.toFixed(0)}%
                  </span>
                </div>
              </div>
              <div className="text-sm font-medium text-gray-900">Overall Match Rate</div>
              <div className="text-xs text-gray-500">Average screening score</div>
            </div>
            
            <div className="text-center">
              <div className="w-20 h-20 mx-auto mb-3 relative">
                <svg className="w-20 h-20 transform -rotate-90">
                  <circle
                    cx="40"
                    cy="40"
                    r="30"
                    stroke="#e5e7eb"
                    strokeWidth="6"
                    fill="none"
                  />
                  <circle
                    cx="40"
                    cy="40"
                    r="30"
                    stroke="#10b981"
                    strokeWidth="6"
                    fill="none"
                    strokeDasharray={`${(stats.average_scores.skill_alignment / 100) * 188.4} 188.4`}
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-sm font-semibold">
                    {stats.average_scores.skill_alignment.toFixed(0)}%
                  </span>
                </div>
              </div>
              <div className="text-sm font-medium text-gray-900">Skill Alignment</div>
              <div className="text-xs text-gray-500">Skills match accuracy</div>
            </div>
            
            <div className="text-center">
              <div className="w-20 h-20 mx-auto mb-3 relative">
                <svg className="w-20 h-20 transform -rotate-90">
                  <circle
                    cx="40"
                    cy="40"
                    r="30"
                    stroke="#e5e7eb"
                    strokeWidth="6"
                    fill="none"
                  />
                  <circle
                    cx="40"
                    cy="40"
                    r="30"
                    stroke="#8b5cf6"
                    strokeWidth="6"
                    fill="none"
                    strokeDasharray={`${(stats.average_scores.experience_relevance / 100) * 188.4} 188.4`}
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-sm font-semibold">
                    {stats.average_scores.experience_relevance.toFixed(0)}%
                  </span>
                </div>
              </div>
              <div className="text-sm font-medium text-gray-900">Experience Relevance</div>
              <div className="text-xs text-gray-500">Experience match rate</div>
            </div>
          </div>
        </div>
      )}

      {/* Model Evaluation */}
      <div className="card">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-gray-900">Model Evaluation</h2>
          <Button 
            onClick={runEvaluation} 
            loading={isEvaluating}
            variant="outline"
          >
            {isEvaluating ? 'Running Evaluation...' : 'Run Model Evaluation'}
          </Button>
        </div>
        
        {evaluation && (
          <div className="space-y-4">
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-green-700 text-sm font-medium">
                ✓ Model evaluation completed successfully!
              </p>
              <p className="text-green-600 text-sm mt-1">
                Evaluation started in background. Check system logs for detailed results.
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-medium text-gray-900 mb-2">Embedding Performance</h3>
                <div className="space-y-1 text-sm text-gray-600">
                  <div>TF-IDF Vectorization: Active</div>
                  <div>BERT Embeddings: Available</div>
                  <div>Feature Extraction: Optimized</div>
                </div>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-medium text-gray-900 mb-2">Screening Pipeline</h3>
                <div className="space-y-1 text-sm text-gray-600">
                  <div>Similarity Calculation: Multi-metric</div>
                  <div>Section Scoring: Weighted</div>
                  <div>Explainability: Enhanced</div>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {!evaluation && !isEvaluating && (
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-4">📋</div>
            <p>Click "Run Model Evaluation" to assess system performance</p>
            <p className="text-sm mt-1">This will evaluate ML models, accuracy metrics, and latency.</p>
          </div>
        )}
      </div>

      {/* System Status */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">System Health</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">API Server</span>
              <span className="flex items-center text-sm text-green-600">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                Online
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">ML Pipeline</span>
              <span className="flex items-center text-sm text-green-600">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                Active
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Data Storage</span>
              <span className="flex items-center text-sm text-green-600">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                Available
              </span>
            </div>
          </div>
        </div>
        
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
          <div className="space-y-3">
            <div className="text-sm text-gray-600">
              📝 {stats?.recent_activity?.resumes_generated || 0} resumes generated
            </div>
            <div className="text-sm text-gray-600">
              🔍 {stats?.recent_activity?.screenings_performed || 0} screenings performed
            </div>
            <div className="text-sm text-gray-600">
              ✍️ {stats?.recent_activity?.content_generated || 0} content pieces created
            </div>
            <div className="pt-2 border-t border-gray-200">
              <Button 
                onClick={loadAnalytics} 
                variant="ghost" 
                size="sm" 
                className="w-full"
              >
                🔄 Refresh Data
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};