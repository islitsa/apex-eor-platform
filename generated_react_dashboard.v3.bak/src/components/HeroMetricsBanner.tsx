import React from 'react';

interface Props {
  totalSources: number;
  totalFiles: number;
  totalRecords: number;
  totalSizeGB: number;
}

export default function HeroMetricsBanner({ totalSources, totalFiles, totalRecords, totalSizeGB }: Props) {
  const metrics = [
    { label: 'Data Sources', value: totalSources, icon: 'database' },
    { label: 'Total Files', value: totalFiles.toLocaleString(), icon: 'description' },
    { label: 'Total Records', value: totalRecords.toLocaleString(), icon: 'table_chart' },
    { label: 'Total Size', value: `${Number(totalSizeGB || 0).toFixed(2)} GB`, icon: 'storage' },
  ];

  return (
    <div className="flex gap-12">
      {metrics.map((metric, index) => (
        <div key={index} className="flex flex-col">
          <div className="flex items-center gap-2 mb-2">
            <span className="material-symbols-rounded text-gray-600 text-xl">{metric.icon}</span>
            <span className="text-sm font-medium text-gray-600 uppercase tracking-wide">
              {metric.label}
            </span>
          </div>
          <div className="text-[80px] font-bold leading-none text-gray-900">
            {metric.value}
          </div>
        </div>
      ))}
    </div>
  );
}