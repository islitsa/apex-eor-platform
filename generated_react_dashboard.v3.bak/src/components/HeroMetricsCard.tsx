import React from 'react';
import { Pipeline } from '../types';

interface Props {
  pipelines: Pipeline[];
}

export default function HeroMetricsCard({ pipelines }: Props) {
  const totalFiles = pipelines.reduce((sum, p) => sum + (p.metrics?.file_count || 0), 0);
  const totalSize = pipelines.reduce((sum, p) => {
    const sizeStr = p.metrics?.data_size || '0 B';
    const match = sizeStr.match(/([\d.]+)\s*([KMGT]?B)/i);
    if (!match) return sum;
    const value = parseFloat(match[1]);
    const unit = match[2].toUpperCase();
    const multipliers: Record<string, number> = { 'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 'TB': 1024**4 };
    return sum + (value * (multipliers[unit] || 1));
  }, 0);

  const sizeInGB = totalSize / (1024 ** 3);
  const domain = pipelines[0]?.name?.split('_')[0] || 'petroleum_energy';

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
      <div className="flex items-center gap-3 mb-6">
        <span className="material-symbols-rounded text-blue-600 text-4xl">science</span>
        <h1 className="text-3xl font-bold text-gray-900">FracFocus Chemical Data</h1>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="text-center">
          <div className="text-4xl font-bold text-gray-900">{totalFiles}</div>
          <div className="text-sm text-gray-600 mt-1">Files</div>
        </div>
        <div className="text-center">
          <div className="text-4xl font-bold text-gray-900">{Number(sizeInGB || 0).toFixed(1)} GB</div>
          <div className="text-sm text-gray-600 mt-1">Total Size</div>
        </div>
        <div className="text-center">
          <div className="text-4xl font-bold text-gray-900">{String(domain).toLowerCase()}</div>
          <div className="text-sm text-gray-600 mt-1">Domain</div>
        </div>
      </div>
    </div>
  );
}