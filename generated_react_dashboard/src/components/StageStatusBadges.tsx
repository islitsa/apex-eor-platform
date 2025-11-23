import React from 'react';

interface Props {
  status: string;
}

export default function StageStatusBadges({ status }: Props) {
  const normalizedStatus = String(status || 'unknown').toLowerCase();

  const getStatusConfig = () => {
    switch (normalizedStatus) {
      case 'complete':
      case 'completed':
      case 'success':
        return {
          icon: 'check_circle',
          bgColor: 'bg-green-100',
          textColor: 'text-green-700',
          iconColor: 'text-green-600',
          label: 'Complete'
        };
      case 'pending':
      case 'in_progress':
      case 'running':
        return {
          icon: 'pending',
          bgColor: 'bg-yellow-100',
          textColor: 'text-yellow-700',
          iconColor: 'text-yellow-600',
          label: 'Pending'
        };
      case 'error':
      case 'failed':
        return {
          icon: 'error',
          bgColor: 'bg-red-100',
          textColor: 'text-red-700',
          iconColor: 'text-red-600',
          label: 'Error'
        };
      default:
        return {
          icon: 'help',
          bgColor: 'bg-gray-100',
          textColor: 'text-gray-700',
          iconColor: 'text-gray-600',
          label: 'Unknown'
        };
    }
  };

  const config = getStatusConfig();

  return (
    <div
      className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full ${config.bgColor} ${config.textColor} group relative`}
      title={`Status: ${config.label}`}
    >
      <span className={`material-symbols-rounded text-lg ${config.iconColor}`}>
        {config.icon}
      </span>
      <span className="text-sm font-medium">{config.label}</span>
      
      {/* Tooltip */}
      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-10">
        Stage status: {config.label}
        <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1 border-4 border-transparent border-t-gray-900"></div>
      </div>
    </div>
  );
}