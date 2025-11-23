import React from 'react';

interface DataVolumeVisualizationProps {
  sizeInBytes: number;
  fileCount: number;
}

export default function DataVolumeVisualization({
  sizeInBytes,
  fileCount
}: DataVolumeVisualizationProps) {
  const sizeInGB = sizeInBytes / (1024 * 1024 * 1024);
  const maxGB = 100; // Reference scale
  const percentage = Math.min((sizeInGB / maxGB) * 100, 100);

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <span className="material-symbols-rounded text-gray-600 text-xl">storage</span>
        <span className="text-lg font-semibold text-gray-900">
          {Number(sizeInGB || 0).toFixed(2)} GB
        </span>
        <span className="text-sm text-gray-500">
          ({Number(fileCount || 0).toLocaleString()} files)
        </span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
        <div
          className="bg-gradient-to-r from-[#FF6B35] to-[#FF8C42] h-full rounded-full transition-all duration-500"
          style={{ width: `${percentage}%` }}
        />
      </div>
      <div className="flex justify-between text-xs text-gray-500">
        <span>0 GB</span>
        <span>{maxGB} GB</span>
      </div>
    </div>
  );
}