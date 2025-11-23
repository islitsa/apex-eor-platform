import React from 'react';

interface Stage {
  name: string;
  status: string;
}

interface Props {
  stages: Stage[];
}

export default function PipelineHealthIndicator({ stages }: Props) {
  if (!stages || stages.length === 0) {
    return (
      <div className="text-sm text-gray-500 italic">No pipeline stages available</div>
    );
  }

  const getStatusIcon = (status: string) => {
    const statusStr = String(status || 'unknown').toLowerCase();
    if (statusStr === 'complete' || statusStr === 'success') {
      return { icon: 'check_circle', color: 'text-green-600', bg: 'bg-green-50' };
    } else if (statusStr === 'pending' || statusStr === 'in_progress') {
      return { icon: 'pending', color: 'text-amber-600', bg: 'bg-amber-50' };
    } else if (statusStr === 'failed' || statusStr === 'error') {
      return { icon: 'error', color: 'text-red-600', bg: 'bg-red-50' };
    }
    return { icon: 'help', color: 'text-gray-600', bg: 'bg-gray-50' };
  };

  return (
    <div className="space-y-2">
      {stages.map((stage, index) => {
        const { icon, color, bg } = getStatusIcon(stage.status);
        const stageName = String(stage.name || 'Unknown');
        
        return (
          <div
            key={index}
            className={`flex items-center gap-3 p-2 rounded-lg ${bg} group relative`}
            title={`${stageName}: ${String(stage.status || 'unknown')}`}
          >
            <span className={`material-symbols-rounded text-lg ${color}`}>{icon}</span>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-gray-900 truncate">
                {String(stageName).replace(/_/g, ' ')}
              </div>
              <div className="text-xs text-gray-600 capitalize">
                {String(stage.status || 'unknown').replace(/_/g, ' ')}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}