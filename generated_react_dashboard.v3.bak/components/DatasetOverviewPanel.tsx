import { useState, useMemo } from 'react';
import { Pipeline } from '../types.ts';

interface DatasetOverviewPanelProps {
  pipeline: Pipeline;
  isExpanded: boolean;
  onToggle: () => void;
}

function DatasetOverviewPanel({ pipeline, isExpanded, onToggle }: DatasetOverviewPanelProps) {
  const fileCount = useMemo(() => {
    return Number(pipeline?.metrics?.file_count || 0);
  }, [pipeline]);

  const dataSize = useMemo(() => {
    const bytes = Number(pipeline?.metrics?.data_size || 0);
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
  }, [pipeline]);

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6">
      <div
        className="flex items-center justify-between cursor-pointer"
        onClick={onToggle}
      >
        <div className="flex items-center gap-3">
          <span className="material-symbols-rounded text-3xl text-purple-600">science</span>
          <div>
            <h2 className="text-xl font-bold text-gray-900">{pipeline.display_name}</h2>
            <p className="text-sm text-gray-500">
              {fileCount} {fileCount === 1 ? 'file' : 'files'} • {dataSize}
            </p>
          </div>
        </div>
        <span className="material-symbols-rounded text-gray-600">
          {isExpanded ? 'expand_less' : 'expand_more'}
        </span>
      </div>
    </div>
  );
}

export { DatasetOverviewPanel };
export default DatasetOverviewPanel;