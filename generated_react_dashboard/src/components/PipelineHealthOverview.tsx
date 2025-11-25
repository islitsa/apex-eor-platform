import React from 'react';
import type { Pipeline } from '../types';

interface Props {
  pipelines: Pipeline[];
}

export default function PipelineHealthOverview({ pipelines }: Props) {
  const getStatusIcon = (status: string) => {
    const statusStr = String(status || 'unknown').toLowerCase();
    if (statusStr === 'complete' || statusStr === 'success') {
      return { icon: 'check_circle', color: 'text-green-600', bg: 'bg-green-50' };
    }
    if (statusStr === 'running' || statusStr === 'in_progress') {
      return { icon: 'pending', color: 'text-blue-600', bg: 'bg-blue-50' };
    }
    if (statusStr === 'error' || statusStr === 'failed') {
      return { icon: 'error', color: 'text-red-600', bg: 'bg-red-50' };
    }
    return { icon: 'help', color: 'text-gray-600', bg: 'bg-gray-50' };
  };

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold text-gray-900 mb-4">Pipeline Health</h2>
      
      {pipelines.map(pipeline => (
        <div key={pipeline.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-3">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-bold text-gray-900">{pipeline.display_name || pipeline.name}</h3>
            {(() => {
              const statusInfo = getStatusIcon(pipeline.status);
              return (
                <div className={`flex items-center gap-1 px-2 py-1 rounded-full ${statusInfo.bg}`}>
                  <span className={`material-symbols-rounded text-sm ${statusInfo.color}`}>
                    {statusInfo.icon}
                  </span>
                  <span className={`text-xs font-medium ${statusInfo.color}`}>
                    {String(pipeline.status || 'unknown').replace(/_/g, ' ')}
                  </span>
                </div>
              );
            })()}
          </div>

          <div className="space-y-2">
            {pipeline.stages && Array.isArray(pipeline.stages) && pipeline.stages.map((stage, idx) => {
              const stageName = stage.name || `Stage ${idx + 1}`;
              const stageStatus = stage.status || 'unknown';
              const statusInfo = getStatusIcon(stageStatus);
              
              return (
                <div key={idx} className="flex items-center justify-between py-2 border-t border-gray-100">
                  <div className="flex items-center gap-2">
                    <span className={`material-symbols-rounded text-sm ${statusInfo.color}`}>
                      {statusInfo.icon}
                    </span>
                    <span className="text-sm text-gray-700">
                      {String(stageName || '').replace(/_/g, ' ')}
                    </span>
                  </div>
                  <span className="text-xs text-gray-500">
                    {String(stageStatus || 'unknown').replace(/_/g, ' ')}
                  </span>
                </div>
              );
            })}
          </div>

          <div className="mt-3 pt-3 border-t border-gray-100 grid grid-cols-2 gap-2 text-xs">
            <div>
              <span className="text-gray-500">Files:</span>
              <span className="ml-1 font-medium text-gray-900">
                {(pipeline.metrics?.file_count || 0).toLocaleString()}
              </span>
            </div>
            <div>
              <span className="text-gray-500">Records:</span>
              <span className="ml-1 font-medium text-gray-900">
                {(pipeline.metrics?.record_count || 0).toLocaleString()}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}