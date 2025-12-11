import React from 'react';
import type { Pipeline } from '../types';

interface Props {
  pipeline: Pipeline;
}

export default function MetricsSummaryBar({ pipeline }: Props) {
  const formatSize = (sizeStr: string): string => {
    return sizeStr || '0 B';
  };

  return (
    <div className="flex items-center gap-4">
      {/* File Count */}
      <div className="flex-1">
        <p className="text-xs text-gray-500 mb-1">Files</p>
        <p className="text-base font-bold text-gray-900">
          {(pipeline.metrics?.file_count || 0).toLocaleString()}
        </p>
      </div>

      {/* Data Size */}
      <div className="flex-1">
        <p className="text-xs text-gray-500 mb-1">Size</p>
        <p className="text-base font-bold text-gray-900">
          {formatSize(pipeline.metrics?.data_size || '0 B')}
        </p>
      </div>

      {/* Record Count */}
      <div className="flex-1">
        <p className="text-xs text-gray-500 mb-1">Records</p>
        <p className="text-base font-bold text-gray-900">
          {(pipeline.metrics?.record_count || 0).toLocaleString()}
        </p>
      </div>
    </div>
  );
}