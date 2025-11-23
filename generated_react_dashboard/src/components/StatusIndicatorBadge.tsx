import React from 'react';

interface StatusIndicatorBadgeProps {
  status: string;
}

export default function StatusIndicatorBadge({ status }: StatusIndicatorBadgeProps) {
  const statusStr = String(status || 'unknown').toLowerCase();

  const getStatusConfig = () => {
    switch (statusStr) {
      case 'complete':
      case 'completed':
        return {
          bg: 'bg-green-100',
          text: 'text-green-800',
          icon: 'check_circle',
          label: 'Complete'
        };
      case 'running':
      case 'in_progress':
        return {
          bg: 'bg-blue-100',
          text: 'text-blue-800',
          icon: 'sync',
          label: 'Running'
        };
      case 'failed':
      case 'error':
        return {
          bg: 'bg-red-100',
          text: 'text-red-800',
          icon: 'error',
          label: 'Failed'
        };
      default:
        return {
          bg: 'bg-[#FF6B35] bg-opacity-20',
          text: 'text-[#FF6B35]',
          icon: 'warning',
          label: 'Unknown Status'
        };
    }
  };

  const config = getStatusConfig();

  return (
    <div className={`${config.bg} ${config.text} rounded-full px-4 py-2 flex items-center gap-2 animate-pulse`}>
      <span className="material-symbols-rounded text-xl">{config.icon}</span>
      <span className="font-medium text-sm">{config.label}</span>
    </div>
  );
}