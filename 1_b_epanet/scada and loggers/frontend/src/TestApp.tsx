import React from 'react';

const TestApp: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          💧 Water Network Monitoring System
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          React app is working! 🚀
        </p>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">System Status</h2>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span>React:</span>
              <span className="text-green-600">✅ Working</span>
            </div>
            <div className="flex justify-between">
              <span>TypeScript:</span>
              <span className="text-green-600">✅ Working</span>
            </div>
            <div className="flex justify-between">
              <span>TailwindCSS:</span>
              <span className="text-green-600">✅ Working</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TestApp;

