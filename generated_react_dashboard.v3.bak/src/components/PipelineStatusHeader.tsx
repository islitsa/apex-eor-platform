import React from 'react';
import StageProgressIndicator from './StageProgressIndicator';

interface Props {
  metrics: {
    total: number;
    processed: number;
    downloaded: number;
    failed: number;
    totalFiles: number;
    totalRecords: number;
  };
}

export default function PipelineStatusHeader({ metrics }: Props) {
  const getHealthStatus = () => {
    const healthScore = (metrics.processed / metrics.total) * 100;
    if (healthScore >= 80) return { color: 'bg-green-500', label: 'Healthy' };
    if (healthScore >= 50) return { color: 'bg-amber-500', label: 'Warning' };
    return { color: 'bg-red-500', label: 'Critical' };
  };

  const health = getHealthStatus();

  return (
    <div className="h-16 bg-gray-900 text-white px-8 flex items-center justify-between shadow-lg">
      <div className="flex items-center gap-6">
        <h1 className="text-2xl font-bold">Data Pipeline Dashboard</h1>
        <div className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${health.color}`}></div>
          <span className="text-base">{health.label}</span>
        </div>
      </div>

      <div className="flex items-center gap-8">
        <div className="text-center">
          <div className="text-base text-gray-400">Pipelines</div>
          <div className="text-base font-semibold">{metrics.total}</div>
        </div>
        <div className="text-center">
          <div className="text-base text-gray-400">Total Files</div>
          <div className="text-base font-semibold">{Number(metrics.totalFiles || 0).toLocaleString()}</div>
        </div>
        <div className="text-center">
          <div className="text-base text-gray-400">Total Records</div>
          <div className="text-base font-semibold">{Number(metrics.totalRecords || 0).toLocaleString()}</div>
        </div>
        <div className="text-center">
          <div className="text-base text-gray-400">Processed</div>
          <div className="text-base font-semibold text-green-400">{metrics.processed}</div>
        </div>
        <div className="text-center">
          <div className="text-base text-gray-400">Downloaded</div>
          <div className="text-base font-semibold text-amber-400">{metrics.downloaded}</div>
        </div>
        {metrics.failed > 0 && (
          <div className="text-center">
            <div className="text-base text-gray-400">Failed</div>
            <div className="text-base font-semibold text-red-400">{metrics.failed}</div>
          </div>
        )}
      </div>
    </div>
  );
}