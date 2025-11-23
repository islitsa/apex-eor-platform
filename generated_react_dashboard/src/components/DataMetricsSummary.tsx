import React from 'react';
import type { Pipeline } from '../types';

interface DataMetricsSummaryProps {
  pipeline: Pipeline;
  selectedFile: string;
}

export default function DataMetricsSummary({ pipeline, selectedFile }: DataMetricsSummaryProps) {
  const recordCount = pipeline.metrics?.record_count || 0;
  const dataSize = pipeline.metrics?.data_size || '0 MB';
  const fileName = selectedFile.split('/').pop() || selectedFile;

  return (
    <div className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h2 className="text-xl font-bold text-gray-900">{pipeline.display_name || pipeline.name}</h2>
          <p className="text-sm text-gray-600 flex items-center gap-2 mt-1">
            <span className="material-symbols-rounded text-sm">description</span>
            {fileName}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-10">
        <div>
          <p className="text-3xl font-bold text-gray-900">{recordCount.toLocaleString()}</p>
          <p className="text-sm text-gray-600 mt-1">Total Records</p>
        </div>
        <div>
          <p className="text-3xl font-bold text-gray-900">{dataSize}</p>
          <p className="text-sm text-gray-600 mt-1">File Size</p>
        </div>
        <div>
          <p className="text-3xl font-bold text-gray-900">100</p>
          <p className="text-sm text-gray-600 mt-1">Rows Displayed</p>
        </div>
      </div>
    </div>
  );
}