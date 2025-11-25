import React from 'react';

interface Props {
  totalFiles: number;
  totalRecords: number;
  totalSize: number;
}

export default function QuickStatsBar({ totalFiles, totalRecords, totalSize }: Props) {
  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 border-b border-gray-200">
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-gray-600 uppercase">Total Files</span>
          <span className="text-lg font-bold text-gray-900">
            {Number(totalFiles || 0).toLocaleString()}
          </span>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-gray-600 uppercase">Total Records</span>
          <span className="text-lg font-bold text-gray-900">
            {Number(totalRecords || 0).toLocaleString()}
          </span>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-gray-600 uppercase">Total Size</span>
          <span className="text-lg font-bold text-gray-900">
            {Number(totalSize || 0).toFixed(2)} MB
          </span>
        </div>
      </div>
    </div>
  );
}