import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="flex items-center space-x-2 mb-4 md:mb-0">
            <div className="flex items-center justify-center w-6 h-6 bg-primary-600 rounded">
              <span className="text-white font-bold text-sm">R</span>
            </div>
            <span className="font-semibold text-gray-900">
              Resume Intelligence System
            </span>
          </div>
          
          <div className="text-sm text-gray-500 text-center md:text-right">
            <p>Powered by ML-driven resume optimization</p>
            <p className="mt-1">© 2026 Resume Intelligence. All rights reserved.</p>
          </div>
        </div>
        
        <div className="mt-6 pt-6 border-t border-gray-200">
          <div className="flex flex-wrap justify-center space-x-6 text-sm text-gray-500">
            <span>✨ AI-Powered Generation</span>
            <span>🎯 Smart Screening</span>
            <span>📊 Analytics Dashboard</span>
            <span>🔒 Secure & Private</span>
          </div>
        </div>
      </div>
    </footer>
  );
};