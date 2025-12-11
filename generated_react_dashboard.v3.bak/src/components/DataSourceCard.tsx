import React from 'react';
import type { Pipeline } from '../types';

interface Props {
  pipeline: Pipeline;
  isExpanded: boolean;
  isSelected: boolean;
  onToggleExpand: () => void;
  onSelect: () => void;
}

export default function DataSourceCard({ pipeline, isExpanded, isSelected, onToggleExpand, onSelect }: Props) {
  const fileCount = pipeline.metrics?.file_count || 0;
  const recordCount = pipeline.metrics?.record_count || 0;
  const dataSize = pipeline.metrics?.data_size || '0 B';

  return (
    <div
      className={`w-72 rounded-xl shadow-md border transition-all cursor-pointer ${
        isSelected ? 'border-blue-500 bg-blue-50' : 'border-gray-200 bg-white hover:shadow-lg'
      }`}
      onClick={onSelect}
    >
      <div className="p-4">
        <div className="flex items-start justify-between mb-2">
          <h3 className="text-lg font-bold text-gray-900 flex-1">{pipeline.display_name}</h3>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onToggleExpand();
            }}
            className="text-gray-500 hover:text-gray-700 transition-transform"
            style={{ transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)' }}
          >
            <span className="material-symbols-rounded">expand_more</span>
          </button>
        </div>

        <div className="space-y-1 text-sm text-gray-600">
          <div className="flex items-center gap-2">
            <span className="material-symbols-rounded text-base">folder</span>
            <span>{fileCount.toLocaleString()} files</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="material-symbols-rounded text-base">database</span>
            <span>{recordCount.toLocaleString()} records</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="material-symbols-rounded text-base">storage</span>
            <span>{dataSize}</span>
          </div>
        </div>

        {/* Pipeline Status */}
        <div className="mt-3 flex items-center gap-2">
          <div className={`px-2 py-1 rounded text-xs font-semibold ${
            pipeline.status === 'processed' ? 'bg-green-100 text-green-800' :
            pipeline.status === 'processing' ? 'bg-blue-100 text-blue-800' :
            'bg-gray-100 text-gray-800'
          }`}>
            {String(pipeline.status || 'unknown').toUpperCase()}
          </div>
        </div>

        {/* Expanded File Tree */}
        {isExpanded && pipeline.files && pipeline.files.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="text-xs font-semibold text-gray-700 mb-2">Files:</div>
            <div className="space-y-1 max-h-48 overflow-y-auto">
              {pipeline.files.slice(0, 10).map((file: any, idx: number) => (
                <div key={idx} className="flex items-center gap-2 text-xs text-gray-600 pl-2">
                  <span className="material-symbols-rounded text-sm">
                    {file.type === 'directory' || file.type === 'folder' ? 'folder' : 'description'}
                  </span>
                  <span className="truncate">{file.name}</span>
                </div>
              ))}
              {pipeline.files.length > 10 && (
                <div className="text-xs text-gray-500 pl-2">
                  +{pipeline.files.length - 10} more files
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}