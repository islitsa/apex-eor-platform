import React from 'react';
import type { Pipeline } from '../types';

interface PipelineHealthPanelProps {
  pipeline: Pipeline;
}

export default function PipelineHealthPanel({ pipeline }: PipelineHealthPanelProps) {
  const getStageIcon = (stageName: string): string => {
    const name = String(stageName || '').toLowerCase();
    if (name.includes('download')) return 'download';
    if (name.includes('extract') || name.includes('transform')) return 'transform';
    if (name.includes('parse') || name.includes('code')) return 'code';
    return 'check_circle';
  };

  const getStatusColor = (status: string): string => {
    const statusStr = String(status || '').toLowerCase();
    if (statusStr === 'complete' || statusStr === 'success') return 'text-green-600';
    if (statusStr === 'running' || statusStr === 'in_progress') return 'text-blue-600';
    if (statusStr === 'failed' || statusStr === 'error') return 'text-red-600';
    return 'text-gray-400';
  };

  const stages = pipeline.stages || [];

  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <div className="flex items-center gap-2 mb-3">
        <h3 className="font-semibold text-gray-900 text-sm">
          {pipeline.display_name || pipeline.name}
        </h3>
      </div>

      <div className="space-y-2">
        {stages.map((stage, index) => (
          <div
            key={index}
            className="group relative flex items-center gap-3 p-2 rounded hover:bg-gray-50 transition-colors"
          >
            <span className={`material-symbols-rounded text-lg ${getStatusColor(stage.status)}`}>
              {getStageIcon(stage.name)}
            </span>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-700 truncate">
                {String(stage.name || '').replace(/_/g, ' ')}
              </p>
              <p className={`text-xs ${getStatusColor(stage.status)}`}>
                {String(stage.status || 'unknown').replace(/_/g, ' ')}
              </p>
            </div>
            <span className={`material-symbols-rounded text-lg ${getStatusColor(stage.status)}`}>
              {String(stage.status || '').toLowerCase() === 'complete' ? 'check_circle' : 'pending'}
            </span>

            {/* Tooltip */}
            <div className="absolute left-0 bottom-full mb-2 hidden group-hover:block z-10 bg-gray-900 text-white text-xs rounded px-2 py-1 whitespace-nowrap">
              Stage: {String(stage.name || '').replace(/_/g, ' ')}
            </div>
          </div>
        ))}

        {stages.length === 0 && (
          <p className="text-sm text-gray-500 text-center py-4">No stages available</p>
        )}
      </div>
    </div>
  );
}