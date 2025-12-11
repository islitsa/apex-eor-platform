import React from 'react';

interface Stage {
  name: string;
  status: string;
}

interface PipelineStageIndicatorsProps {
  stages: Stage[];
}

export default function PipelineStageIndicators({ stages }: PipelineStageIndicatorsProps) {
  const getStageIcon = (status: string) => {
    const statusLower = String(status || '').toLowerCase();
    if (statusLower === 'complete' || statusLower === 'completed') return 'check_circle';
    if (statusLower === 'processing' || statusLower === 'running') return 'pending';
    if (statusLower === 'error' || statusLower === 'failed') return 'error';
    return 'radio_button_unchecked';
  };

  const getStageColor = (status: string) => {
    const statusLower = String(status || '').toLowerCase();
    if (statusLower === 'complete' || statusLower === 'completed') return 'text-green-600';
    if (statusLower === 'processing' || statusLower === 'running') return 'text-amber-600';
    if (statusLower === 'error' || statusLower === 'failed') return 'text-red-600';
    return 'text-gray-400';
  };

  if (!stages || stages.length === 0) {
    return null;
  }

  return (
    <div className="pt-4 border-t border-gray-200">
      <p className="text-xs text-gray-500 mb-3">Pipeline Health</p>
      <div className="flex items-center gap-2">
        {stages.map((stage, index) => (
          <React.Fragment key={index}>
            <div className="group relative">
              <span className={`material-symbols-rounded text-xl ${getStageColor(stage.status)} transition-colors duration-200`}>
                {getStageIcon(stage.status)}
              </span>
              <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap pointer-events-none z-10">
                {String(stage.name || '').replace(/_/g, ' ')}: {String(stage.status || '').replace(/_/g, ' ')}
              </div>
            </div>
            {index < stages.length - 1 && (
              <div className="flex-1 h-0.5 bg-gray-200 max-w-[20px]"></div>
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}