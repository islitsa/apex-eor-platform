import React from 'react';

export default function LoadingSpinner() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-gray-300 border-t-primary-600 mb-4"></div>
        <p className="text-gray-600 text-lg">Loading production data...</p>
      </div>
    </div>
  );
}