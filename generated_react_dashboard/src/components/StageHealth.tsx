import React from 'react';
import type { Pipeline } from '../types.ts';

interface StageHealthProps {
  pipeline: Pipeline;
}

export default function StageHealth({ pipeline }: StageHealthProps) {
  const getStatusColor = (status: string) => {
    const statusStr = String(status || 'unknown').toLowerCase();
    switch (statusStr) {
      case 'processed':
      case 'complete':
        return 'bg-green-500';
      case 'processing':
        return 'bg-blue-500';
      case 'error':
      case 'failed':
        return 'bg-red-500';
      default:
        return 'bg-gray-400';
    }
  };

  const getStatusIcon = (status: string) => {
    const statusStr = String(status || 'unknown').toLowerCase();
    switch (statusStr) {
      case 'processed':
      case 'complete':
        return 'check_circle';
      case 'processing':
        return 'sync';
      case 'error':
      case 'failed':
        return 'error';
      default:
        return 'help';
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center gap-3 mb-4">
        <span className="material-symbols-rounded text-gray-700">monitoring</span>
        <h2 className="text-lg font-semibold text-gray-900">Pipeline Health</h2>
      </div>

      <div className="space-y-4">
        {pipeline.stages?.map((stage, index) => (
          <div key={index} className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${getStatusColor(stage.status)}`}></div>
                <span className="font-medium text-gray-900">
                  {String(stage.name || 'unknown').replace(/_/g, ' ')}
                </span>
              </div>
              <span className={`material-symbols-rounded text-[20px] ${
                String(stage.status || '').toLowerCase() === 'complete' || String(stage.status || '').toLowerCase() === 'processed'
                  ? 'text-green-600'
                  : String(stage.status || '').toLowerCase() === 'processing'
                  ? 'text-blue-600'
                  : 'text-gray-400'
              }`}>
                {getStatusIcon(stage.status)}
              </span>
            </div>
            <div className="text-sm text-gray-600">
              <p>Status: <span className="font-medium">{String(stage.status || 'unknown').replace(/_/g, ' ')}</span></p>
              {stage.file_count !== undefined && (
                <p>Files: <span className="font-medium">{Number(stage.file_count || 0).toLocaleString()}</span></p>
              )}
              {stage.last_updated && (
                <p>Updated: <span className="font-medium">{String(stage.last_updated)}</span></p>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Overall Status</span>
          <span className={`flex items-center gap-1 px-3 py-1 rounded-full font-medium ${
            String(pipeline.status || '').toLowerCase() === 'processed'
              ? 'bg-green-100 text-green-800'
              : String(pipeline.status || '').toLowerCase() === 'processing'
              ? 'bg-blue-100 text-blue-800'
              : 'bg-gray-100 text-gray-800'
          }`}>
            <span className="material-symbols-rounded text-[16px]">{getStatusIcon(pipeline.status)}</span>
            {String(pipeline.status || 'unknown').replace(/_/g, ' ')}
          </span>
        </div>
      </div>
    </div>
  );
}