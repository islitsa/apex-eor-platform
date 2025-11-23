import React from 'react';

interface Props {
  status: string;
}

export default function HealthStatusIndicators({ status }: Props) {
  const normalizedStatus = String(status || 'unknown').toLowerCase();

  const getStatusConfig = () => {
    if (normalizedStatus.includes('complete') || normalizedStatus.includes('success') || normalizedStatus === 'done') {
      return {
        icon: 'check_circle',
        color: 'text-green-600',
        bgColor: 'bg-green-50',
        label: 'Complete',
      };
    }
    if (normalizedStatus.includes('error') || normalizedStatus.includes('failed')) {
      return {
        icon: 'error',
        color: 'text-red-600',
        bgColor: 'bg-red-50',
        label: 'Error',
      };
    }
    if (normalizedStatus.includes('warning') || normalizedStatus.includes('partial')) {
      return {
        icon: 'warning',
        color: 'text-amber-600',
        bgColor: 'bg-amber-50',
        label: 'Warning',
      };
    }
    if (normalizedStatus.includes('running') || normalizedStatus.includes('processing')) {
      return {
        icon: 'pending',
        color: 'text-blue-600',
        bgColor: 'bg-blue-50',
        label: 'Running',
      };
    }
    return {
      icon: 'help',
      color: 'text-gray-600',
      bgColor: 'bg-gray-50',
      label: 'Unknown',
    };
  };

  const config = getStatusConfig();

  return (
    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${config.bgColor} ${config.color}`}>
      <span className="material-symbols-rounded" style={{ fontSize: '14px' }}>
        {config.icon}
      </span>
      {config.label}
    </span>
  );
}