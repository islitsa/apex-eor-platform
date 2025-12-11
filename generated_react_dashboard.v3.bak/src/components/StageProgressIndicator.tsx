import React from 'react';

interface Stage {
  name: string;
  status: string;
}

interface Props {
  stages: Stage[];
}

export default function StageProgressIndicator({ stages }: Props) {
  const getStageIcon = (stageName: string) => {
    const name = String(stageName || '').toLowerCase();
    if (name.includes('download')) return 'download';
    if (name.includes('extract')) return 'folder_zip';
    if (name.includes('pars')) return 'code';
    if (name.includes('transform')) return 'transform';
    return 'circle';
  };

  const getStatusColor = (status: string) => {
    const statusStr = String(status || '').toLowerCase();
    if (statusStr === 'complete' || statusStr === 'processed') return 'bg-green-500';
    if (statusStr === 'running' || statusStr === 'processing') return 'bg-blue-500 animate-pulse';
    if (statusStr === 'failed' || statusStr === 'error') return 'bg-red-500';
    return 'bg-gray-300';
  };

  return (
    <div className="flex items-center gap-2">
      {stages.map((stage, idx) => (
        <React.Fragment key={idx}>
          <div className="flex flex-col items-center">
            <div className={`w-8 h-8 rounded-full ${getStatusColor(stage.status)} flex items-center justify-center text-white shadow-sm`}>
              <span className="material-symbols-rounded text-sm">{getStageIcon(stage.name)}</span>
            </div>
            <span className="text-xs text-gray-600 mt-1 capitalize">
              {String(stage.name || '').replace(/_/g, ' ').substring(0, 8)}
            </span>
          </div>
          {idx < stages.length - 1 && (
            <div className="w-4 h-0.5 bg-gray-300 mb-4"></div>
          )}
        </React.Fragment>
      ))}
    </div>
  );
}