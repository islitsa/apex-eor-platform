import React from 'react';
import type { Pipeline } from '../types';

interface PipelineHealthProps {
  pipelines: Pipeline[];
}

export default function PipelineHealth({ pipelines }: PipelineHealthProps) {
  const getStatusColor = (status: string): string => {
    const statusStr = String(status || 'unknown').toLowerCase();
    switch (statusStr) {
      case 'processed':
      case 'complete':
      case 'success':
        return 'bg-green-500';
      case 'processing':
      case 'running':
        return 'bg-blue-500';
      case 'error':
      case 'failed':
        return 'bg-red-500';
      default:
        return 'bg-gray-400';
    }
  };

  const getStatusIcon = (status: string): string => {
    const statusStr = String(status || 'unknown').toLowerCase();
    switch (statusStr) {
      case 'processed':
      case 'complete':
      case 'success':
        return 'check_circle';
      case 'processing':
      case 'running':
        return 'sync';
      case 'error':
      case 'failed':
        return 'error';
      default:
        return 'help';
    }
  };

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
        <span className="material-symbols-rounded">monitor_heart</span>
        Pipeline Health
      </h2>

      <div className="space-y-6">
        {pipelines.map((pipeline) => (
          <div key={pipeline.id} className="border-b border-gray-200 pb-6 last:border-b-0">
            <h3 className="font-bold text-gray-900 mb-4 text-sm">
              {pipeline.display_name || pipeline.name}
            </h3>

            <div className="space-y-3">
              {pipeline.stages?.map((stage, index) => {
                const stageStatus = String(stage.status || 'unknown');
                const stageName = String(stage.name || 'unknown');
                
                return (
                  <div key={index} className="flex items-center gap-3">
                    <div
                      className={`w-12 h-12 rounded-full flex items-center justify-center ${getStatusColor(stageStatus)} text-white flex-shrink-0`}
                    >
                      <span className="material-symbols-rounded text-xl">
                        {getStatusIcon(stageStatus)}
                      </span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-bold text-sm text-gray-900 capitalize">
                        {stageName.replace(/_/g, ' ')}
                      </div>
                      <div className="text-xs text-gray-600 capitalize">
                        {stageStatus.replace(/_/g, ' ')}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Overall Status */}
            <div className="mt-4 pt-4 border-t border-gray-100">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-gray-600">Overall Status</span>
                <div className={`px-3 py-1 rounded-full text-xs font-bold ${
                  pipeline.status === 'processed' || pipeline.status === 'complete'
                    ? 'bg-green-100 text-green-800'
                    : pipeline.status === 'processing'
                    ? 'bg-blue-100 text-blue-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {String(pipeline.status || 'unknown').toUpperCase()}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {pipelines.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <span className="material-symbols-rounded text-4xl mb-2">info</span>
          <p className="text-sm">No pipelines to monitor</p>
        </div>
      )}
    </div>
  );
}