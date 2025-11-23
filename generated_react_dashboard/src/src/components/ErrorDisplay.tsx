import React from 'react';

interface ErrorDisplayProps {
  error: string;
}

export default function ErrorDisplay({ error }: ErrorDisplayProps) {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
        <div className="flex items-center gap-3 mb-4">
          <span className="material-symbols-rounded text-4xl text-red-600">
            error
          </span>
          <h2 className="text-2xl font-bold text-gray-900">Error Loading Data</h2>
        </div>
        <p className="text-gray-700 mb-4">{error}</p>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-900">
            <strong>Troubleshooting:</strong>
          </p>
          <ul className="text-sm text-red-800 mt-2 space-y-1 list-disc list-inside">
            <li>Ensure the backend API is running at http://localhost:8000</li>
            <li>Check that the /api/pipelines endpoint is accessible</li>
            <li>Verify CORS settings allow requests from this origin</li>
          </ul>
        </div>
        <button
          onClick={() => window.location.reload()}
          className="mt-6 w-full bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200"
        >
          Retry
        </button>
      </div>
    </div>
  );
}