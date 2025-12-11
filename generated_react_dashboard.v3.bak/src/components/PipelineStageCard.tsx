import React from 'react';
import { PipelineStage } from '../types.ts';

interface PipelineStageCardProps {
  stage: PipelineStage;
}

export function PipelineStageCard({ stage }: PipelineStageCardProps) {
  const normalizedStatus = String(stage.status || '').toLowerCase();
  
  let statusColor = 'text-gray-400';
  let icon = 'pending';
  let progressWidth = '0%';
  
  if (normalizedStatus === 'completed' || normalizedStatus === 'processed') {
    statusColor = 'text-green-500';
    icon = 'check_circle';
    progressWidth = '100%';
  } else if (normalizedStatus === 'running' || normalizedStatus === 'processing') {
    statusColor = 'text-yellow-500';
    icon = 'pending';
    progressWidth = '50%';
  } else if (normalizedStatus === 'failed' || normalizedStatus === 'error') {
    statusColor = 'text-red-500';
    icon = 'error';
    progressWidth = '100%';
  }

  return (
    <div className="w-80 bg-white rounded-lg shadow-sm p-6">
      <div className="flex items-center gap-3 mb-4">
        <span className={`material-symbols-rounded text-2xl ${statusColor}`}>
          {icon}
        </span>
        <h3 className="text-base font-semibold text-gray-900">{stage.name}</h3>
      </div>
      <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full transition-all duration-300 ${
            normalizedStatus === 'failed' || normalizedStatus === 'error'
              ? 'bg-red-500'
              : normalizedStatus === 'completed' || normalizedStatus === 'processed'
              ? 'bg-green-500'
              : 'bg-yellow-500'
          }`}
          style={{ width: progressWidth }}
        />
      </div>
    </div>
  );
}