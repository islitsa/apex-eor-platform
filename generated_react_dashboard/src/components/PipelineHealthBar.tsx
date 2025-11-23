import React from 'react';
import type { Pipeline } from '../types.ts';

interface Props {
  pipeline: Pipeline;
}

export default function PipelineHealthBar({ pipeline }: Props) {
  const stages = pipeline.stages || [];

  const getStageIcon = (status: string): string => {
    const statusStr = String(status || '').toLowerCase();
    if (statusStr === 'complete' || statusStr === 'completed') return 'check_circle';
    if (statusStr === 'running' || statusStr === 'in_progress') return 'pending';
    if (statusStr === 'failed' || statusStr === 'error') return 'error';
    return 'pending';
  };

  const getStageColor = (status: string): string => {
    const statusStr = String(status || '').toLowerCase();
    if (statusStr === 'complete' || statusStr === 'completed') return 'text-green-600';
    if (statusStr === 'running' || statusStr === 'in_progress') return 'text-amber-600';
    if (statusStr === 'failed' || statusStr === 'error') return 'text-red-600';
    return 'text-gray-400';
  };

  return (
    <div className="flex items-center gap-8">
      {stages.map((stage, index) => (
        <React.Fragment key={index}>
          <div className="flex items-center gap-3">
            <div
              className="flex items-center justify-center rounded-full bg-gray-50"
              style={{ width: '48px', height: '48px' }}
            >
              <span className={`material-symbols-rounded text-3xl ${getStageColor(stage.status)}`}>
                {getStageIcon(stage.status)}
              </span>
            </div>
            <div>
              <div className="text-sm font-semibold text-gray-900" style={{ fontWeight: 600 }}>
                {String(stage.name || 'unknown').replace(/_/g, ' ')}
              </div>
              <div className="text-xs text-gray-500 capitalize">
                {String(stage.status || 'unknown').replace(/_/g, ' ')}
              </div>
            </div>
          </div>
          {index < stages.length - 1 && (
            <div className="w-8 h-0.5 bg-gray-300"></div>
          )}
        </React.Fragment>
      ))}
    </div>
  );
}