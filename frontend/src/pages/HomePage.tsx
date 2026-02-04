import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/common/Button';
import { Loading } from '../components/common/Loading';
import { apiService } from '../services/api';

const features = [
  {
    icon: '🧠',
    title: 'AI-Powered Resume Generation',
    description: 'Generate tailored resumes using advanced ML algorithms that match job requirements perfectly.',
    href: '/generate'
  },
  {
    icon: '�',
    title: 'LaTeX Resume Generator',
    description: 'Create professional LaTeX resumes with customizable templates and downloadable source code.',
    href: '/latex'
  },
  {
    icon: '�🔍',
    title: 'Smart Resume Screening',
    description: 'Screen resumes against job descriptions with explainable AI feedback and improvement suggestions.',
    href: '/screen'
  },
  {
    icon: '✍️',
    title: 'Content Generator',
    description: 'Create professional emails, cover letters, and LinkedIn prompts with role-specific optimization.',
    href: '/content'
  },
  {
    icon: '📊',
    title: 'Analytics Dashboard',
    description: 'Track performance metrics, model accuracy, and system analytics in real-time.',
    href: '/analytics'
  }
];

export const HomePage: React.FC = () => {
  const [systemStatus, setSystemStatus] = useState<'loading' | 'online' | 'offline'>('loading');
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    checkSystemHealth();
    loadStats();
  }, []);

  const checkSystemHealth = async () => {
    try {
      await apiService.healthCheck();
      setSystemStatus('online');
    } catch (error) {
      setSystemStatus('offline');
    }
  };

  const loadStats = async () => {
    try {
      const response = await apiService.getDataStats();
      setStats(response.data.data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center py-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Welcome to{' '}
          <span className="text-gradient">Resume Intelligence System</span>
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
          Production-grade ML-driven platform for resume optimization, intelligent screening, 
          and professional content generation. Built with explainable AI and enterprise-ready architecture.
        </p>
        
        {/* System Status */}
        <div className="flex items-center justify-center space-x-4 mb-8">
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${
              systemStatus === 'online' ? 'bg-green-500' :
              systemStatus === 'offline' ? 'bg-red-500' : 'bg-yellow-500'
            }`}></div>
            <span className="text-sm font-medium">
              System Status: {systemStatus === 'loading' ? 'Checking...' : systemStatus}
            </span>
          </div>
          
          {stats && (
            <div className="text-sm text-gray-500">
              {stats.total_resumes} resumes • {stats.total_job_descriptions} jobs processed
            </div>
          )}
        </div>


      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {features.map((feature) => (
          <Link key={feature.title} to={feature.href} className="group">
            <div className="card hover:shadow-lg transition-all duration-200 group-hover:shadow-glow">
              <div className="text-center">
                <div className="text-3xl mb-4">{feature.icon}</div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600 text-sm leading-relaxed">
                  {feature.description}
                </p>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* Technical Overview */}
      <div className="bg-gradient-to-br from-primary-50 to-purple-50 rounded-2xl p-8">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            🚀 Production-Ready ML Architecture
          </h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Built with enterprise-grade components, explainable AI, and comprehensive evaluation metrics.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="bg-white rounded-lg p-4 mb-3">
              <span className="text-2xl">🧠</span>
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Hybrid ML Pipeline</h3>
            <p className="text-sm text-gray-600">
              TF-IDF + BERT embeddings with rule-based optimization
            </p>
          </div>
          
          <div className="text-center">
            <div className="bg-white rounded-lg p-4 mb-3">
              <span className="text-2xl">📊</span>
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Explainable AI</h3>
            <p className="text-sm text-gray-600">
              Section-wise scoring with detailed feedback and suggestions
            </p>
          </div>
          
          <div className="text-center">
            <div className="bg-white rounded-lg p-4 mb-3">
              <span className="text-2xl">⚙️</span>
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Enterprise Ready</h3>
            <p className="text-sm text-gray-600">
              FastAPI backend with comprehensive logging and monitoring
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};