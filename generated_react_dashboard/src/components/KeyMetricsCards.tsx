import React from 'react';

interface KeyMetricsCardsProps {
  totalRows: number;
  totalStorage: number;
  totalFiles: number;
}

export default function KeyMetricsCards({ 
  totalRows, 
  totalStorage, 
  totalFiles 
}: KeyMetricsCardsProps) {
  const formatNumber = (num: number): string => {
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(1)}M`;
    }
    if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`;
    }
    return String(num);
  };

  const formatBytes = (bytes: number): string => {
    const gb = bytes / (1024 * 1024 * 1024);
    return `${gb.toFixed(1)} GB`;
  };

  const metrics = [
    {
      label: 'Total Rows',
      value: formatNumber(totalRows),
      icon: 'table_rows',
      color: 'blue'
    },
    {
      label: 'Storage Used',
      value: formatBytes(totalStorage),
      icon: 'storage',
      color: 'green'
    },
    {
      label: 'Active Files',
      value: String(totalFiles),
      icon: 'description',
      color: 'purple'
    }
  ];

  return (
    <div className="flex gap-6">
      {metrics.map((metric, index) => (
        <div 
          key={index}
          className="bg-white rounded-2xl shadow-lg p-6 flex-1"
          style={{ width: '280px', height: '120px' }}
        >
          <div className="flex items-start justify-between">
            <div>
              <div className="text-5xl font-bold text-gray-900 mb-2">
                {metric.value}
              </div>
              <div className="text-gray-600 text-base">
                {metric.label}
              </div>
            </div>
            <span 
              className={`material-symbols-rounded text-4xl text-${metric.color}-500`}
            >
              {metric.icon}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}