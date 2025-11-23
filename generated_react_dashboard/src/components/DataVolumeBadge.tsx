import React from 'react';

interface DataVolumeBadgeProps {
  recordCount: number;
}

export default function DataVolumeBadge({ recordCount }: DataVolumeBadgeProps) {
  const formatCount = (count: number): string => {
    const num = Number(count || 0);
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(1)}M`;
    }
    if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`;
    }
    return String(num);
  };

  return (
    <div className="flex items-center gap-2 bg-green-600 text-white rounded-full px-3 py-1 shadow-md hover:scale-105 transition-transform duration-200">
      <span className="material-symbols-rounded text-sm">check_circle</span>
      <span className="text-sm font-bold">{formatCount(recordCount)}</span>
    </div>
  );
}