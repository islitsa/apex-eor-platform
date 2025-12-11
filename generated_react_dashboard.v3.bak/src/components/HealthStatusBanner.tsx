import React from 'react';

interface HealthStatusBannerProps {
  status: 'healthy' | 'processing' | 'error';
  lastUpdated: string;
}

export default function HealthStatusBanner({ status, lastUpdated }: HealthStatusBannerProps) {
  const getStatusConfig = () => {
    switch (status) {
      case 'healthy':
        return {
          bg: 'bg-green-600',
          text: 'All pipelines operational',
          icon: 'check_circle',
        };
      case 'processing':
        return {
          bg: 'bg-amber-600',
          text: 'Pipelines processing',
          icon: 'pending',
        };
      case 'error':
        return {
          bg: 'bg-red-600',
          text: 'Pipeline errors detected',
          icon: 'error',
        };
      default:
        return {
          bg: 'bg-gray-600',
          text: 'Status unknown',
          icon: 'help',
        };
    }
  };

  const config = getStatusConfig();

  return (
    <div className={`${config.bg} text-white px-8 py-4 fixed top-0 left-0 right-0 z-50`}>
      <div className="max-w-[1600px] mx-auto flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="material-symbols-rounded">{config.icon}</span>
          <span className="font-semibold">{config.text}</span>
        </div>
        <div className="text-sm opacity-90">
          Last updated: {lastUpdated}
        </div>
      </div>
    </div>
  );
}