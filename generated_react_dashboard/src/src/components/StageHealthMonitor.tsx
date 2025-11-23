import React from 'react';
import type { Pipeline, PipelineStage } from '../types.ts';

interface StageHealthMonitorProps {
  pipeline: Pipeline;
}

export default function StageHealthMonitor({ pipeline }: StageHealthMonitorProps) {
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
        return 'bg-gray-300';
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

  const stages = pipeline.stages || [];

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Pipeline Health by Stage</h2>
      
      {stages.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <span className="material-symbols-rounded text-4xl mb-2">info</span>
          <p>No stage information available</p>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Progress Bar */}
          <div className="flex items-center gap-2">
            {stages.map((stage, idx) => (
              <React.Fragment key={idx}>
                <div className="flex-1">
                  <div className={`h-2 rounded-full ${getStatusColor(stage.status)}`}></div>
                </div>
                {idx < stages.length - 1 && (
                  <span className="material-symbols-rounded text-gray-300">chevron_right</span>
                )}
              </React.Fragment>
            ))}
          </div>

          {/* Stage Details */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
            {stages.map((stage, idx) => (
              <div key={idx} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-gray-900 capitalize">
                    {String(stage.name || 'unknown').replace(/_/g, ' ')}
                  </h3>
                  <span className={`material-symbols-rounded ${getStatusColor(stage.status).replace('bg-', 'text-')}`}>
                    {getStatusIcon(stage.status)}
                  </span>
                </div>
                
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Status:</span>
                    <span className="font-medium capitalize">
                      {String(stage.status || 'unknown').replace(/_/g, ' ')}
                    </span>
                  </div>
                  
                  {stage.file_count !== undefined && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Files:</span>
                      <span className="font-medium">{Number(stage.file_count || 0).toLocaleString()}</span>
                    </div>
                  )}
                  
                  {stage.last_updated && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Updated:</span>
                      <span className="font-medium text-xs">
                        {new Date(String(stage.last_updated)).toLocaleDateString()}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}