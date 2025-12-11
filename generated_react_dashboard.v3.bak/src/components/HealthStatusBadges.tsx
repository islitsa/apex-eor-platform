import React from 'react';

interface Stage {
  name: string;
  status: string;
}

interface HealthStatusBadgesProps {
  stages: Stage[];
}

export default function HealthStatusBadges({ stages }: HealthStatusBadgesProps) {
  const getStatusColor = (status: string) => {
    const statusLower = String(status || '').toLowerCase();
    if (statusLower === 'complete' || statusLower === 'completed') {
      return 'bg-green-500 text-white';
    } else if (statusLower === 'processing' || statusLower === 'in_progress') {
      return 'bg-amber-500 text-white';
    } else if (statusLower === 'failed' || statusLower === 'error') {
      return 'bg-red-500 text-white';
    }
    return 'bg-gray-400 text-white';
  };

  const getStatusIcon = (status: string) => {
    const statusLower = String(status || '').toLowerCase();
    if (statusLower === 'complete' || statusLower === 'completed') {
      return 'check_circle';
    } else if (statusLower === 'processing' || statusLower === 'in_progress') {
      return 'pending';
    } else if (statusLower === 'failed' || statusLower === 'error') {
      return 'error';
    }
    return 'help';
  };

  return (
    <div className="flex flex-wrap gap-3">
      {stages.map((stage, index) => (
        <div
          key={index}
          className={`flex items-center gap-2 px-4 py-2 rounded-full ${getStatusColor(stage.status)} shadow-sm`}
        >
          <span className="material-symbols-rounded text-lg">
            {getStatusIcon(stage.status)}
          </span>
          <span className="font-bold text-sm">
            {String(stage.name || 'unknown').replace(/_/g, ' ').toUpperCase()}
          </span>
        </div>
      ))}
    </div>
  );
}