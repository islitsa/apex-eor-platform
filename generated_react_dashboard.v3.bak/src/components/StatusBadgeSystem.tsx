import React from 'react';

interface Props {
  status: string;
}

export default function StatusBadgeSystem({ status }: Props) {
  const getStatusConfig = (status: string) => {
    const statusLower = String(status || '').toLowerCase();
    
    if (statusLower === 'complete' || statusLower === 'completed' || statusLower === 'processed') {
      return {
        icon: 'check_circle',
        bgColor: 'bg-green-100',
        textColor: 'text-green-800',
        iconColor: 'text-green-600',
        label: 'Complete'
      };
    }
    
    if (statusLower === 'pending' || statusLower === 'processing' || statusLower === 'in_progress') {
      return {
        icon: 'pending',
        bgColor: 'bg-yellow-100',
        textColor: 'text-yellow-800',
        iconColor: 'text-yellow-600',
        label: 'Pending'
      };
    }
    
    if (statusLower === 'error' || statusLower === 'failed') {
      return {
        icon: 'error',
        bgColor: 'bg-red-100',
        textColor: 'text-red-800',
        iconColor: 'text-red-600',
        label: 'Error'
      };
    }
    
    return {
      icon: 'help',
      bgColor: 'bg-gray-100',
      textColor: 'text-gray-800',
      iconColor: 'text-gray-600',
      label: String(status || 'Unknown').replace(/_/g, ' ')
    };
  };

  const config = getStatusConfig(status);

  return (
    <div className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full ${config.bgColor}`}>
      <span className={`material-symbols-rounded text-base ${config.iconColor}`}>
        {config.icon}
      </span>
      <span className={`text-sm font-medium ${config.textColor} capitalize`}>
        {config.label}
      </span>
    </div>
  );
}