import React from 'react';
import { Button } from '../components/ui/Button';

export function ResumeGeneratorPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-8 text-center">
      <div className="text-center">
        <h1 className="section-title">Resume Generator</h1>
        <p className="text-gray-600 mb-8">
          This feature has been replaced with our enhanced LaTeX Resume Generator.
        </p>
      </div>

      <div className="card max-w-2xl mx-auto">
        <div className="text-center py-12">
          <div className="text-6xl mb-6">📄</div>
          <h3 className="text-xl font-semibold text-gray-800 mb-4">
            Feature Moved to LaTeX Generator
          </h3>
          <p className="text-gray-600 mb-6">
            We've enhanced our resume generation capabilities with a more powerful LaTeX-based system 
            that creates professional, customizable resumes in your preferred format.
          </p>
          <Button 
            onClick={() => window.location.href = '/latex'}
            className="bg-blue-600 hover:bg-blue-700"
          >
            Go to LaTeX Generator
          </Button>
        </div>
      </div>
    </div>
  );
}