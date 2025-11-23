import React from 'react';

interface StatusIndicatorsProps {
  status: string;
  size?: 'small' | 'medium' | 'large';
}

export default function StatusIndicators({ status, size = 'medium' }: StatusIndicatorsProps) {
  const normalizedStatus = String(status || 'unknown').toLowerCase();

  const getStatusConfig = () => {
    if (normalizedStatus === 'complete' || normalizedStatus === 'completed') {
      return {
        icon: 'check_circle',
        color: 'text-green-600',
        bg: 'bg-green-100',
        label: 'Complete'
      };
    } else if (normalizedStatus === 'failed' || normalizedStatus === 'error') {
      return {
        icon: 'error',
        color: 'text-red-600',
        bg: 'bg-red-100',
        label: 'Failed'
      };
    } else if (normalizedStatus === 'processing' || normalizedStatus === 'running') {
      return {
        icon: 'pending',
        color: 'text-yellow-600',
        bg: 'bg-yellow-100',
        label: 'Processing'
      };
    } else {
      return {
        icon: 'help',
        color: 'text-gray-600',
        bg: 'bg-gray-100',
        label: 'Unknown'
      };
    }
  };

  const config = getStatusConfig();
  const sizeClasses = {
    small: 'w-5 h-5 text-sm',
    medium: 'w-6 h-6 text-base',
    large: 'w-8 h-8 text-2xl'
  };

  return (
    <div className={`${config.bg} ${sizeClasses[size]} rounded-full flex items-center justify-center`}>
      <span className={`material-symbols-rounded ${config.color} ${
        size === 'small' ? 'text-sm' : size === 'large' ? 'text-2xl' : 'text-base'
      }`}>
        {config.icon}
      </span>
    </div>
  );
}