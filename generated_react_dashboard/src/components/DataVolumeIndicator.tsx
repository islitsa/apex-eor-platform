import React from 'react';

interface DataVolumeIndicatorProps {
  pipelineName: string;
  sizeBytes: number;
}

export default function DataVolumeIndicator({ 
  pipelineName, 
  sizeBytes 
}: DataVolumeIndicatorProps) {
  // Calculate percentage based on max observed size (RRC is largest)
  const maxSize = 80 * 1024 * 1024 * 1024; // 80GB approximate max
  const percentage = Math.min((Number(sizeBytes) / maxSize) * 100, 100);

  const getColor = (): string => {
    const name = String(pipelineName).toLowerCase();
    if (name.includes('rrc')) return 'blue';
    if (name.includes('production')) return 'green';
    return 'gray';
  };

  const color = getColor();

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-xs text-gray-600">
        <span>Data Volume</span>
        <span>{Number(percentage).toFixed(0)}% of capacity</span>
      </div>
      <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
        <div 
          className={`h-full bg-${color}-500 transition-all duration-300`}
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    </div>
  );
}