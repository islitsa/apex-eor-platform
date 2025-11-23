import React from 'react';

interface QuickStatsGridProps {
  fileCount: number;
  totalSize: number;
  recordCount: number;
}

export default function QuickStatsGrid({ fileCount, totalSize, recordCount }: QuickStatsGridProps) {
  const formatSize = (bytes: number): string => {
    const gb = bytes / (1024 ** 3);
    return Number(gb || 0).toFixed(2);
  };

  const formatRecords = (count: number): string => {
    const millions = count / 1_000_000;
    return Number(millions || 0).toFixed(1);
  };

  return (
    <div className="grid grid-cols-3 gap-6">
      <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
        <div className="flex items-center gap-3 mb-3">
          <span className="material-symbols-rounded text-blue-600 text-3xl">description</span>
          <span className="text-sm font-medium text-gray-500 uppercase tracking-wide">Total Files</span>
        </div>
        <div className="text-4xl font-bold text-gray-900">{Number(fileCount || 0).toLocaleString()}</div>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
        <div className="flex items-center gap-3 mb-3">
          <span className="material-symbols-rounded text-purple-600 text-3xl">storage</span>
          <span className="text-sm font-medium text-gray-500 uppercase tracking-wide">Total Size</span>
        </div>
        <div className="text-4xl font-bold text-gray-900">{formatSize(totalSize)} GB</div>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
        <div className="flex items-center gap-3 mb-3">
          <span className="material-symbols-rounded text-green-600 text-3xl">table_rows</span>
          <span className="text-sm font-medium text-gray-500 uppercase tracking-wide">Total Records</span>
        </div>
        <div className="text-4xl font-bold text-gray-900">{formatRecords(recordCount)}M+</div>
      </div>
    </div>
  );
}