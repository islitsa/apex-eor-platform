import React from 'react';
import { Stage } from '../types.ts';

interface PipelineHealthOverviewProps {
  stages: Stage[];
}

export function PipelineHealthOverview({ stages }: PipelineHealthOverviewProps) {
  const getStageIcon = (status: string): string => {
    const statusLower = String(status || '').toLowerCase();
    if (statusLower === 'completed' || statusLower === 'processed') return 'download';
    if (statusLower === 'in_progress' || statusLower === 'processing') return 'transform';
    return 'code';
  };

  const getStageColor = (status: string): string => {
    const statusLower = String(status || '').toLowerCase();
    if (statusLower === 'completed' || statusLower === 'processed') return 'text-green-600';
    if (statusLower === 'in_progress' || statusLower === 'processing') return 'text-orange-500';
    return 'text-gray-400';
  };

  const getProgressColor = (status: string): string => {
    const statusLower = String(status || '').toLowerCase();
    if (statusLower === 'completed' || statusLower === 'processed') return 'bg-green-100 border-green-600';
    if (statusLower === 'in_progress' || statusLower === 'processing') return 'bg-orange-100 border-orange-500';
    return 'bg-gray-100 border-gray-400';
  };

  return (
    <div className="w-[300px] flex-shrink-0">
      <div className="flex items-center gap-2 mb-6">
        <span className="material-symbols-rounded text-2xl text-gray-700">database</span>
        <h2 className="text-lg font-bold text-gray-900">Pipeline Health</h2>
      </div>
      <div className="w-[280px] flex flex-col gap-6">
        {stages.map((stage, index) => (
          <div key={index} className="flex flex-col items-center">
            <div
              className={`w-12 h-12 rounded-full border-2 flex items-center justify-center ${getProgressColor(
                stage.status
              )}`}
            >
              <span className={`material-symbols-rounded text-2xl ${getStageColor(stage.status)}`}>
                {getStageIcon(stage.status)}
              </span>
            </div>
            <div className="mt-2 text-center font-bold text-sm text-gray-900">
              {stage.name}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}