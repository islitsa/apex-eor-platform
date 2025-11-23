import React from 'react';

interface MetricsSummaryGridProps {
  totalRecords: number;
  totalFiles: number;
  totalSize: number;
}

export default function MetricsSummaryGrid({ totalRecords, totalFiles, totalSize }: MetricsSummaryGridProps) {
  const metrics = [
    {
      label: 'Total Records',
      value: Number(totalRecords || 0).toLocaleString(),
      icon: 'dataset',
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      label: 'Total Files',
      value: Number(totalFiles || 0).toLocaleString(),
      icon: 'description',
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    },
    {
      label: 'Storage Size',
      value: `${Number(totalSize || 0).toFixed(2)} GB`,
      icon: 'storage',
      color: 'text-purple-600',
      bgColor: 'bg-purple-50'
    }
  ];

  return (
    <div className="grid grid-cols-3 gap-6">
      {metrics.map((metric, index) => (
        <div
          key={index}
          className={`${metric.bgColor} rounded-xl p-6 shadow-sm`}
          style={{ width: '120px', height: '120px' }}
        >
          <span className={`material-symbols-rounded ${metric.color} text-3xl mb-2 block`}>
            {metric.icon}
          </span>
          <p className="text-2xl font-bold text-gray-900 mb-1">{metric.value}</p>
          <p className="text-sm text-gray-600">{metric.label}</p>
        </div>
      ))}
    </div>
  );
}