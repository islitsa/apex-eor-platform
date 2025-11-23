import React from 'react';

interface ErrorDisplayProps {
  error: string;
}

export function ErrorDisplay({ error }: ErrorDisplayProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center p-6">
      <div className="bg-white rounded-xl shadow-lg border border-red-200 p-8 max-w-md w-full">
        <div className="flex items-center gap-3 mb-4">
          <span className="material-symbols-rounded text-4xl text-red-600">
            error
          </span>
          <h2 className="text-2xl font-bold text-slate-900">Error Loading Data</h2>
        </div>
        <p className="text-slate-700 mb-4">
          Failed to fetch pipeline data from the API.
        </p>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
          <p className="text-sm text-red-800 font-mono">
            {error}
          </p>
        </div>
        <button
          onClick={() => window.location.reload()}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          <span className="material-symbols-rounded text-sm">
            refresh
          </span>
          Retry
        </button>
      </div>
    </div>
  );
}