import React from 'react';
import type { Pipeline } from '../types';

interface StageStatusCirclesProps {
  pipeline: Pipeline;
}

export default function StageStatusCircles({ pipeline }: StageStatusCirclesProps) {
  const stages = pipeline.stages || [];

  const getStatusIcon = (status: string) => {
    const statusStr = String(status || '').toLowerCase();
    if (statusStr === 'complete' || statusStr === 'completed') return 'check_circle';
    if (statusStr === 'error' || statusStr === 'failed') return 'error';
    if (statusStr === 'running' || statusStr === 'in_progress') return 'pending';
    return 'radio_button_unchecked';
  };

  const getStatusColor = (status: string) => {
    const statusStr = String(status || '').toLowerCase();
    if (statusStr === 'complete' || statusStr === 'completed') return 'text-green-200';
    if (statusStr === 'error' || statusStr === 'failed') return 'text-red-200';
    if (statusStr === 'running' || statusStr === 'in_progress') return 'text-yellow-200';
    return 'text-gray-300';
  };

  return (
    <div className="flex items-center gap-3">
      <span className="text-sm font-medium opacity-90">{String(pipeline.name || 'Unknown')}</span>
      <div className="flex items-center gap-2">
        {stages.map((stage, index) => (
          <div key={index} className="group relative">
            <span className={`material-symbols-rounded text-xl ${getStatusColor(stage.status)}`}>
              {getStatusIcon(stage.status)}
            </span>
            <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
              <div className="font-semibold">{String(stage.name || 'Unknown').replace(/_/g, ' ')}</div>
              <div className="text-gray-300">Status: {String(stage.status || 'unknown').replace(/_/g, ' ')}</div>
              {stage.file_count !== undefined && (
                <div className="text-gray-300">{Number(stage.file_count || 0)} files</div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}