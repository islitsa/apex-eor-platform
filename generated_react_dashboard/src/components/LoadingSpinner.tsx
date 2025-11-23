import React from 'react';

export function LoadingSpinner() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-slate-300 border-t-blue-600 mb-4"></div>
        <p className="text-slate-600 text-lg font-medium">Loading pipeline data...</p>
      </div>
    </div>
  );
}