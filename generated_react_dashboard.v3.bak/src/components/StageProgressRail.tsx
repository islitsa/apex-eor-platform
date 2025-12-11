import React from 'react';
import { Stage } from '../types.ts';

interface StageProgressRailProps {
  stages: Stage[];
}

export default function StageProgressRail({ stages }: StageProgressRailProps) {
  const getStageIcon = (stageName: string) => {
    const name = String(stageName || '').toLowerCase();
    if (name.includes('download') || name.includes('fetch')) return 'download';
    if (name.includes('transform') || name.includes('process')) return 'transform';
    if (name.includes('load') || name.includes('store')) return 'code';
    return 'settings';
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return 'check_circle';
      case 'failed':
        return 'error';
      case 'running':
        return 'pending';
      default:
        return 'pending';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600';
      case 'failed':
        return 'text-red-600';
      case 'running':
        return 'text-blue-600';
      default:
        return 'text-gray-400';
    }
  };

  if (!stages || stages.length === 0) {
    return null;
  }

  return (
    <div className="flex items-center gap-4 py-4">
      {stages.map((stage, index) => (
        <React.Fragment key={index}>
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-12 h-12 rounded-full bg-gray-100">
              <span className="material-symbols-rounded text-gray-600 text-2xl">
                {getStageIcon(stage.name)}
              </span>
            </div>
            <div className="flex flex-col">
              <div className="flex items-center gap-2">
                <span className={`material-symbols-rounded text-xl ${getStatusColor(stage.status)}`}>
                  {getStatusIcon(stage.status)}
                </span>
                <span className="font-semibold text-gray-800">{stage.name}</span>
              </div>
              <span className="text-sm text-gray-500 capitalize">{stage.status}</span>
            </div>
          </div>
          {index < stages.length - 1 && (
            <div className="flex-1 h-0.5 bg-gray-300 min-w-[40px]" />
          )}
        </React.Fragment>
      ))}
    </div>
  );
}