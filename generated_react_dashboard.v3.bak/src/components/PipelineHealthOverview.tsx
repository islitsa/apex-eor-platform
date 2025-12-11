import React, { useMemo } from 'react';
import { Pipeline } from '../types.ts';

interface PipelineHealthOverviewProps {
  pipelines: Pipeline[];
}

interface HealthMetric {
  label: string;
  value: string;
  icon: string;
  color: string;
}

function PipelineHealthOverview({ pipelines }: PipelineHealthOverviewProps) {
  const metrics = useMemo((): HealthMetric[] => {
    const totalRecords = pipelines.reduce((sum, p) => sum + (p.metrics?.record_count || 0), 0);
    const totalFiles = pipelines.reduce((sum, p) => sum + (p.metrics?.file_count || 0), 0);
    const activePipelines = pipelines.filter(p => p.status === 'active').length;

    return [
      {
        label: 'Total Records',
        value: totalRecords.toLocaleString(),
        icon: 'science',
        color: 'text-blue-600',
      },
      {
        label: 'Data Files',
        value: totalFiles.toLocaleString(),
        icon: 'description',
        color: 'text-green-600',
      },
      {
        label: 'Active Pipelines',
        value: String(activePipelines),
        icon: 'check_circle',
        color: 'text-purple-600',
      },
    ];
  }, [pipelines]);

  return (
    <div className="grid grid-cols-3 gap-8">
      {metrics.map((metric, index) => (
        <div
          key={index}
          className="bg-white rounded-2xl shadow-lg p-6 hover:shadow-xl transition-shadow"
        >
          <div className="flex items-start justify-between mb-4">
            <span className={`material-symbols-rounded ${metric.color} text-4xl`}>
              {metric.icon}
            </span>
          </div>
          <div className="text-5xl font-bold text-gray-900 mb-2">
            {metric.value}
          </div>
          <div className="text-base text-gray-600">
            {metric.label}
          </div>
        </div>
      ))}
    </div>
  );
}

export default PipelineHealthOverview;