import React, { useState } from 'react';
import FileExplorerTree from './FileExplorerTree.tsx';
import type { Pipeline } from '../types';

interface Props {
  pipeline: Pipeline;
  onFileSelect: (pipeline: Pipeline, filePath: string) => void;
  selectedFile: string | null;
}

export default function ExpandableDatasetCard({ pipeline, onFileSelect, selectedFile }: Props) {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleToggle = () => {
    setIsExpanded(!isExpanded);
  };

  const formatSize = (sizeStr: string): string => {
    try {
      const match = String(sizeStr || '0').match(/^([\d.]+)\s*([A-Za-z]+)$/);
      if (match) {
        const value = Number(match[1]);
        const unit = match[2].toUpperCase();
        return `${value.toFixed(2)} ${unit}`;
      }
      return sizeStr;
    } catch {
      return sizeStr;
    }
  };

  return (
    <div
      className={`bg-white rounded-xl shadow-md overflow-hidden transition-all duration-300 ease-out ${
        isExpanded ? 'h-auto' : 'h-[120px]'
      }`}
    >
      {/* Header - Always visible */}
      <div
        className="p-6 cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={handleToggle}
      >
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3 flex-1">
            <span className="material-symbols-rounded text-blue-600 text-3xl">oil_barrel</span>
            <div>
              <h3 className="text-2xl font-semibold text-gray-900">
                {pipeline.display_name || pipeline.name}
              </h3>
              <p className="text-gray-600 text-sm mt-1">Pipeline ID: {pipeline.id}</p>
            </div>
          </div>
          <button
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            onClick={handleToggle}
          >
            <span
              className={`material-symbols-rounded text-gray-600 transition-transform duration-300 ${
                isExpanded ? 'rotate-180' : ''
              }`}
            >
              expand_more
            </span>
          </button>
        </div>

        {/* Stats Row */}
        <div className="flex items-center gap-8 mt-4 ml-11">
          <div className="flex items-center gap-2">
            <span className="material-symbols-rounded text-gray-500 text-xl">folder</span>
            <span className="text-lg text-gray-700">
              <span className="font-semibold">{(pipeline.metrics?.file_count || 0).toLocaleString()}</span> files
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="material-symbols-rounded text-gray-500 text-xl">table_rows</span>
            <span className="text-lg text-gray-700">
              <span className="font-semibold">{(pipeline.metrics?.record_count || 0).toLocaleString()}</span> records
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="material-symbols-rounded text-gray-500 text-xl">storage</span>
            <span className="text-lg text-gray-700">
              <span className="font-semibold">{formatSize(pipeline.metrics?.data_size || '0 B')}</span>
            </span>
          </div>
        </div>
      </div>

      {/* Expandable Content */}
      {isExpanded && (
        <div className="border-t border-gray-200 bg-gray-50">
          <div className="p-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <span className="material-symbols-rounded">folder_open</span>
              File Structure
            </h4>
            <div className="bg-white rounded-lg border border-gray-200 max-h-[480px] overflow-y-auto">
              <FileExplorerTree
                pipeline={pipeline}
                onFileSelect={onFileSelect}
                selectedFile={selectedFile}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}