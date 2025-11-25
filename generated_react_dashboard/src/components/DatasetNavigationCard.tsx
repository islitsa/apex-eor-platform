import React, { useState } from 'react';
import type { Pipeline } from '../types';
import FileExplorerTree from './FileExplorerTree.tsx';

interface Props {
  pipeline: Pipeline;
  isSelected: boolean;
  onSelect: () => void;
  onFileSelect: (filePath: string) => void;
}

export default function DatasetNavigationCard({
  pipeline,
  isSelected,
  onSelect,
  onFileSelect
}: Props) {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleToggle = () => {
    setIsExpanded(!isExpanded);
    if (!isExpanded) {
      onSelect();
    }
  };

  return (
    <div
      className={`bg-white rounded-lg border transition-all duration-300 ${
        isSelected ? 'border-blue-500 shadow-md' : 'border-gray-200 shadow-sm'
      } ${isExpanded ? 'h-auto' : 'h-[120px]'}`}
    >
      <div
        className="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={handleToggle}
      >
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <span className="material-symbols-rounded text-blue-600">folder</span>
            <h3 className="font-bold text-gray-900">{pipeline.display_name || pipeline.name}</h3>
          </div>
          <span className="material-symbols-rounded text-gray-600">
            {isExpanded ? 'expand_less' : 'expand_more'}
          </span>
        </div>

        <div className="grid grid-cols-3 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Files:</span>
            <span className="ml-1 font-medium text-gray-900">
              {(pipeline.metrics?.file_count || 0).toLocaleString()}
            </span>
          </div>
          <div>
            <span className="text-gray-500">Records:</span>
            <span className="ml-1 font-medium text-gray-900">
              {(pipeline.metrics?.record_count || 0).toLocaleString()}
            </span>
          </div>
          <div>
            <span className="text-gray-500">Size:</span>
            <span className="ml-1 font-medium text-gray-900">
              {pipeline.metrics?.data_size || '0 GB'}
            </span>
          </div>
        </div>
      </div>

      {isExpanded && (
        <div className="border-t border-gray-200 p-4 max-h-[600px] overflow-y-auto">
          <FileExplorerTree pipeline={pipeline} onFileSelect={onFileSelect} />
        </div>
      )}
    </div>
  );
}