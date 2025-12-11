import React from 'react';
import { formatBytes, formatNumber } from '../utils.ts';

interface PipelineHealthHeaderProps {
  fileCount: number;
  dataSize: number;
  status: string;
}

export default function PipelineHealthHeader({ fileCount, dataSize, status }: PipelineHealthHeaderProps) {
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
      case 'active':
        return 'from-green-600 to-green-700';
      case 'pending':
      case 'running':
        return 'from-yellow-600 to-yellow-700';
      case 'failed':
        return 'from-red-600 to-red-700';
      default:
        return 'from-gray-600 to-gray-700';
    }
  };

  return (
    <div className="w-full h-[180px] bg-gradient-to-r from-gray-800 to-gray-900 flex items-center justify-center px-8">
      <div className="flex gap-8 max-w-[1200px] w-full">
        <div className="flex-1 max-w-[320px] bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg p-6 shadow-lg">
          <div className="flex items-center gap-3 mb-2">
            <span className="material-symbols-rounded text-white text-3xl">folder</span>
            <h3 className="text-white text-lg font-semibold">Files</h3>
          </div>
          <p className="text-white text-4xl font-bold">{formatNumber(fileCount)}</p>
        </div>

        <div className="flex-1 max-w-[320px] bg-gradient-to-br from-purple-600 to-purple-700 rounded-lg p-6 shadow-lg">
          <div className="flex items-center gap-3 mb-2">
            <span className="material-symbols-rounded text-white text-3xl">storage</span>
            <h3 className="text-white text-lg font-semibold">Data Size</h3>
          </div>
          <p className="text-white text-4xl font-bold">{formatBytes(dataSize)}</p>
        </div>

        <div className={`flex-1 max-w-[320px] bg-gradient-to-br ${getStatusColor(status)} rounded-lg p-6 shadow-lg`}>
          <div className="flex items-center gap-3 mb-2">
            <span className="material-symbols-rounded text-white text-3xl">
              {status === 'completed' || status === 'active' ? 'check_circle' : status === 'failed' ? 'error' : 'pending'}
            </span>
            <h3 className="text-white text-lg font-semibold">Status</h3>
          </div>
          <p className="text-white text-4xl font-bold capitalize">{status}</p>
        </div>
      </div>
    </div>
  );
}