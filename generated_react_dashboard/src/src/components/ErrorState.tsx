import React from 'react';

interface ErrorStateProps {
  error: string;
}

export default function ErrorState({ error }: ErrorStateProps) {
  return (
    <div className="min-h-screen bg-surface flex items-center justify-center">
      <div className="bg-error-container rounded-2xl p-8 max-w-md text-center">
        <span className="material-symbols-rounded text-error mb-4" style={{ fontSize: '48px' }}>
          error
        </span>
        <h2 className="text-2xl font-bold text-error mb-2">Error Loading Data</h2>
        <p className="text-on-surface-variant">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="mt-6 px-6 py-3 bg-primary text-on-primary rounded-full font-medium hover:shadow-lg transition-shadow"
        >
          Retry
        </button>
      </div>
    </div>
  );
}