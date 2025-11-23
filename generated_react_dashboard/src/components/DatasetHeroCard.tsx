import React from 'react';
import type { Pipeline } from '../types.ts';
import FileNavigationTree from './FileNavigationTree.tsx';

interface Props {
  pipeline: Pipeline;
  isExpanded: boolean;
  onToggleExpand: () => void;
  onFileSelect: (filePath: string) => void;
}

export default function DatasetHeroCard({ pipeline, isExpanded, onToggleExpand, onFileSelect }: Props) {
  const fileCount = pipeline.metrics?.file_count || 0;
  const recordCount = pipeline.metrics?.record_count || 0;
  const dataSize = pipeline.metrics?.data_size || '0 B';

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden" style={{ width: '320px' }}>
      {/* Card Header */}
      <div
        className="p-6 cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={onToggleExpand}
      >
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0">
            <span className="material-symbols-rounded text-blue-600 text-5xl">
              science
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              {String(pipeline.display_name || pipeline.name || 'Unknown')}
            </h2>
            <div className="flex flex-wrap gap-2 mb-3">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold bg-blue-100 text-blue-800">
                {Number(recordCount || 0).toLocaleString()} records
              </span>
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold bg-green-100 text-green-800">
                {Number(fileCount || 0).toLocaleString()} files
              </span>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <span className="material-symbols-rounded text-lg">storage</span>
              <span>{String(dataSize)}</span>
            </div>
          </div>
          <div className="flex-shrink-0">
            <span className={`material-symbols-rounded text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}>
              expand_more
            </span>
          </div>
        </div>
      </div>

      {/* Expandable File Browser */}
      {isExpanded && (
        <div className="border-t border-gray-200 bg-gray-50">
          <FileNavigationTree
            pipeline={pipeline}
            onFileSelect={onFileSelect}
          />
        </div>
      )}
    </div>
  );
}