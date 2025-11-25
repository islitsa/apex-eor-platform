import React from 'react';
import type { Stage } from '../types';

interface Props {
  stages: Stage[];
}

export default function PipelineStageIndicators({ stages }: Props) {
  const getStageIcon = (status: string) => {
    const statusStr = String(status || '').toLowerCase();
    if (statusStr.includes('complete') || statusStr.includes('success')) return 'check_circle';
    if (statusStr.includes('running') || statusStr.includes('progress')) return 'pending';
    if (statusStr.includes('error') || statusStr.includes('failed')) return 'error';
    return 'radio_button_unchecked';
  };

  const getStageColor = (status: string) => {
    const statusStr = String(status || '').toLowerCase();
    if (statusStr.includes('complete') || statusStr.includes('success')) return 'text-green-600';
    if (statusStr.includes('running') || statusStr.includes('progress')) return 'text-yellow-600';
    if (statusStr.includes('error') || statusStr.includes('failed')) return 'text-red-600';
    return 'text-gray-400';
  };

  if (!stages || stages.length === 0) {
    return (
      <div className="text-sm text-gray-500">
        No pipeline stages available
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 overflow-x-auto pb-2">
      {stages.map((stage, idx) => {
        const stageName = String(stage.name || 'unknown');
        const stageStatus = String(stage.status || 'unknown');
        
        return (
          <React.Fragment key={idx}>
            <div className="flex items-center gap-2 group relative">
              <span className={`material-symbols-rounded ${getStageColor(stageStatus)}`}>
                {getStageIcon(stageStatus)}
              </span>
              <span className="text-sm font-medium text-gray-700 whitespace-nowrap capitalize">
                {stageName.replace(/_/g, ' ')}
              </span>
              
              {/* Tooltip */}
              <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded shadow-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-10">
                <div className="font-semibold capitalize">{stageName.replace(/_/g, ' ')}</div>
                <div className="text-gray-300 capitalize">{stageStatus.replace(/_/g, ' ')}</div>
                {stage.file_count !== undefined && (
                  <div className="text-gray-300">{Number(stage.file_count || 0).toLocaleString()} files</div>
                )}
              </div>
            </div>
            
            {idx < stages.length - 1 && (
              <span className="material-symbols-rounded text-gray-300 text-sm">
                arrow_forward
              </span>
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
}