import React from 'react';

interface HeroMetricsPanelProps {
  totalRecords: number;
  totalFiles: number;
  totalSize: number;
}

export default function HeroMetricsPanel({ totalRecords, totalFiles, totalSize }: HeroMetricsPanelProps) {
  const formatNumber = (num: number): string => {
    return Number(num || 0).toLocaleString();
  };

  const formatSize = (bytes: number): string => {
    const gb = Number(bytes || 0) / (1024 * 1024 * 1024);
    if (gb >= 1) {
      return `${gb.toFixed(2)} GB`;
    }
    const mb = Number(bytes || 0) / (1024 * 1024);
    return `${mb.toFixed(2)} MB`;
  };

  return (
    <div className="grid grid-cols-3 gap-8">
      {/* Total Records Card */}
      <div className="bg-white rounded-2xl shadow-lg p-6 h-[180px] flex flex-col justify-center">
        <div className="flex items-center gap-3 mb-4">
          <span className="material-symbols-rounded text-blue-600 text-3xl">storage</span>
          <p className="text-gray-600 text-base font-normal">Total Records</p>
        </div>
        <p className="text-5xl font-bold text-gray-900">{formatNumber(totalRecords)}</p>
      </div>

      {/* Total Files Card */}
      <div className="bg-white rounded-2xl shadow-lg p-6 h-[180px] flex flex-col justify-center">
        <div className="flex items-center gap-3 mb-4">
          <span className="material-symbols-rounded text-green-600 text-3xl">description</span>
          <p className="text-gray-600 text-base font-normal">Total Files</p>
        </div>
        <p className="text-5xl font-bold text-gray-900">{formatNumber(totalFiles)}</p>
      </div>

      {/* Storage Size Card */}
      <div className="bg-white rounded-2xl shadow-lg p-6 h-[180px] flex flex-col justify-center">
        <div className="flex items-center gap-3 mb-4">
          <span className="material-symbols-rounded text-purple-600 text-3xl">hard_drive</span>
          <p className="text-gray-600 text-base font-normal">Storage Used</p>
        </div>
        <p className="text-5xl font-bold text-gray-900">{formatSize(totalSize)}</p>
      </div>
    </div>
  );
}