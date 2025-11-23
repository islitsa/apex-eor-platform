import React from 'react';

interface FileSizeIndicatorProps {
  sizeBytes: number;
  utilizationPercent: number;
}

export default function FileSizeIndicator({ sizeBytes, utilizationPercent }: FileSizeIndicatorProps) {
  const formatSize = (bytes: number): string => {
    const num = Number(bytes || 0);
    const gb = num / (1024 * 1024 * 1024);
    if (gb >= 1) {
      return `${gb.toFixed(2)} GB`;
    }
    const mb = num / (1024 * 1024);
    return `${mb.toFixed(2)} MB`;
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="material-symbols-rounded text-gray-600 text-sm">storage</span>
          <span className="text-sm text-gray-700 font-medium">Storage</span>
        </div>
        <span className="text-sm font-bold text-gray-900">{formatSize(sizeBytes)}</span>
      </div>
      
      {/* Progress Bar */}
      <div className="w-[280px] h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className="h-full bg-green-500 rounded-full transition-all duration-300"
          style={{ width: `${Math.min(utilizationPercent, 100)}%` }}
        />
      </div>
    </div>
  );
}