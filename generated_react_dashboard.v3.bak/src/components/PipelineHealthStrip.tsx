import React from 'react';
import type { Pipeline } from '../types';

interface Props {
  pipeline: Pipeline;
}

const STAGE_ICONS: Record<string, string> = {
  download: 'download',
  downloads: 'download',
  extract: 'transform',
  extracted: 'transform',
  parsing: 'code',
  parsed: 'code',
  complete: 'check_circle',
};

export default function PipelineHealthStrip({ pipeline }: Props) {
  const stages = pipeline.stages || [];

  const getStageIcon = (stageName: string): string => {
    const lowerName = String(stageName || '').toLowerCase();
    return STAGE_ICONS[lowerName] || 'circle';
  };

  const getStageColor = (status: string): string => {
    const lowerStatus = String(status || '').toLowerCase();
    if (lowerStatus === 'complete' || lowerStatus === 'completed') return 'bg-green-500';
    if (lowerStatus === 'processing' || lowerStatus === 'in_progress') return 'bg-amber-500';
    if (lowerStatus === 'error' || lowerStatus === 'failed') return 'bg-red-500';
    return 'bg-gray-300';
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <h3 className="text-sm font-medium text-gray-700 mb-4">Pipeline Health</h3>
      <div className="flex items-center gap-3">
        {stages.map((stage, index) => (
          <React.Fragment key={index}>
            <div className="flex flex-col items-center gap-2 group relative">
              <div
                className={`w-12 h-12 rounded-full ${getStageColor(
                  stage.status
                )} flex items-center justify-center transition-all duration-150`}
              >
                <span className="material-symbols-rounded text-white text-xl">
                  {getStageIcon(stage.name)}
                </span>
              </div>
              <span className="text-xs text-gray-600 text-center max-w-[60px]">
                {String(stage.name || '').replace(/_/g, ' ')}
              </span>
              
              {/* Tooltip */}
              <div className="absolute bottom-full mb-2 hidden group-hover:block bg-gray-900 text-white text-xs rounded px-2 py-1 whitespace-nowrap z-10">
                {String(stage.status || 'unknown').replace(/_/g, ' ')}
              </div>
            </div>
            {index < stages.length - 1 && (
              <div className="w-8 h-0.5 bg-gray-300 mb-6"></div>
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}