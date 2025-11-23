import React from 'react';
import type { Pipeline } from '../types.ts';

interface StageHealthCardProps {
  pipeline: Pipeline;
}

export default function StageHealthCard({ pipeline }: StageHealthCardProps) {
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

  const getStatusLabel = (status: string) => {
    const statusStr = String(status || 'unknown').toLowerCase();
    return statusStr.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div className="p-6">
        <div className="space-y-4">
          {pipeline.stages?.map((stage, index) => (
            <div key={index} className="flex items-center gap-4">
              <div className={`w-10 h-10 rounded-full ${getStatusColor(stage.status)} flex items-center justify-center flex-shrink-0`}>
                <span className="material-symbols-rounded text-white text-[20px]">
                  {getStatusIcon(stage.status)}
                </span>
              </div>
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900 capitalize">
                  {String(stage.name || 'unknown').replace(/_/g, ' ')}
                </h4>
                <p className="text-sm text-gray-600">
                  Status: {getStatusLabel(stage.status)}
                </p>
              </div>
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                String(stage.status || 'unknown').toLowerCase() === 'processed' || 
                String(stage.status || 'unknown').toLowerCase() === 'complete'
                  ? 'bg-green-100 text-green-800'
                  : String(stage.status || 'unknown').toLowerCase() === 'processing'
                  ? 'bg-blue-100 text-blue-800'
                  : 'bg-red-100 text-red-800'
              }`}>
                {getStatusLabel(stage.status)}
              </div>
            </div>
          )) ?? (
            <div className="text-center py-8 text-gray-500">
              <span className="material-symbols-rounded text-[48px] mb-2">info</span>
              <p>No stage information available</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}