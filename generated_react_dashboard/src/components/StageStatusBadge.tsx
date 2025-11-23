import React from 'react';

interface StageStatusBadgeProps {
  status: string;
}

export default function StageStatusBadge({ status }: StageStatusBadgeProps) {
  const normalizedStatus = String(status || 'unknown').toLowerCase();

  const getStatusConfig = (status: string) => {
    if (status.includes('complete') || status.includes('success')) {
      return {
        bg: 'bg-green-500',
        icon: 'check_circle',
        text: 'Complete'
      };
    }
    if (status.includes('running') || status.includes('progress')) {
      return {
        bg: 'bg-blue-500',
        icon: 'pending',
        text: 'Running'
      };
    }
    if (status.includes('error') || status.includes('failed')) {
      return {
        bg: 'bg-red-500',
        icon: 'error',
        text: 'Error'
      };
    }
    if (status.includes('warning')) {
      return {
        bg: 'bg-amber-500',
        icon: 'warning',
        text: 'Warning'
      };
    }
    return {
      bg: 'bg-gray-400',
      icon: 'help',
      text: 'Unknown'
    };
  };

  const config = getStatusConfig(normalizedStatus);

  return (
    <div className={`inline-flex items-center gap-1 px-3 py-1 rounded-full ${config.bg}`}>
      <span className="material-symbols-rounded text-white text-base">{config.icon}</span>
      <span className="text-xs font-bold text-white">{config.text}</span>
    </div>
  );
}