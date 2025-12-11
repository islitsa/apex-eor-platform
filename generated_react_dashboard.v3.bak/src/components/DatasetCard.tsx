import React, { useState } from 'react';
import StatusBadge from './StatusBadge';
import FileExplorerTree from './FileExplorerTree';
import DataPreviewTable from './DataPreviewTable';
import type { Pipeline } from '../types';

interface Props {
  pipeline: Pipeline;
  isSelected: boolean;
  onSelect: () => void;
}

export default function DatasetCard({ pipeline, isSelected, onSelect }: Props) {
  const [showPreview, setShowPreview] = useState(false);

  const handleCardClick = (e: React.MouseEvent) => {
    if ((e.target as HTMLElement).closest('.preview-button')) {
      return;
    }
    onSelect();
  };

  return (
    <div
      className={`bg-white rounded-2xl transition-all cursor-pointer ${
        isSelected 
          ? 'shadow-lg w-[400px] h-auto' 
          : 'shadow-md hover:shadow-lg w-[400px] h-[180px]'
      }`}
      onClick={handleCardClick}
    >
      {/* Card Header */}
      <div className="p-6">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            <span className="material-symbols-rounded text-blue-600 text-2xl">science</span>
            <h3 className="text-2xl font-bold text-gray-900">
              {String(pipeline.display_name || pipeline.name)}
            </h3>
          </div>
          <StatusBadge status={String(pipeline.status || 'unknown')} />
        </div>

        <div className="space-y-1 text-sm text-gray-600">
          <div className="flex items-center gap-2">
            <span className="material-symbols-rounded text-base">folder</span>
            <span>{Number(pipeline.metrics?.file_count || 0).toLocaleString()} files</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="material-symbols-rounded text-base">table_chart</span>
            <span>{Number(pipeline.metrics?.record_count || 0).toLocaleString()} records</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="material-symbols-rounded text-base">storage</span>
            <span>{String(pipeline.metrics?.data_size || '0 B')}</span>
          </div>
        </div>

        {isSelected && (
          <button
            className="preview-button mt-4 flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
            onClick={(e) => {
              e.stopPropagation();
              setShowPreview(!showPreview);
            }}
          >
            <span className="material-symbols-rounded text-base">
              {showPreview ? 'folder' : 'table_chart'}
            </span>
            {showPreview ? 'Show Files' : 'Preview Data'}
          </button>
        )}
      </div>

      {/* Expanded Content */}
      {isSelected && (
        <div className="border-t border-gray-200">
          {showPreview ? (
            <DataPreviewTable pipeline={pipeline} />
          ) : (
            <FileExplorerTree pipeline={pipeline} />
          )}
        </div>
      )}
    </div>
  );
}