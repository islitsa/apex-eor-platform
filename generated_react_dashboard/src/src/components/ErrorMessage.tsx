import React from 'react';
import Icon from './Icon.tsx';

interface ErrorMessageProps {
  message: string;
}

export default function ErrorMessage({ message }: ErrorMessageProps) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-6">
      <div className="flex items-start gap-3">
        <Icon name="error" className="text-red-600 flex-shrink-0" />
        <div>
          <h3 className="font-semibold text-red-900 mb-1">Error Loading Data</h3>
          <p className="text-sm text-red-800">{message}</p>
          <p className="text-xs text-red-700 mt-2">
            Make sure the backend API is running at http://localhost:8000
          </p>
        </div>
      </div>
    </div>
  );
}