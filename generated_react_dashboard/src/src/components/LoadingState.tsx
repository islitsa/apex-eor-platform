import React from 'react';

export default function LoadingState() {
  return (
    <div className="min-h-screen bg-surface flex items-center justify-center">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-primary border-t-transparent mb-4"></div>
        <div className="text-xl font-medium text-on-surface">Loading pipeline data...</div>
      </div>
    </div>
  );
}