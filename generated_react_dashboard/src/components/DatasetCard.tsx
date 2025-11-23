import React, { useState } from 'react';
import type { Pipeline } from '../types';
import FileExplorerTree from './FileExplorerTree.tsx';
import DataTable from './DataTable.tsx';
import ExpandButton from './ExpandButton.tsx';

interface DatasetCardProps {
  pipeline: Pipeline;
}

export default function DatasetCard({ pipeline }: DatasetCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const recordCount = pipeline.metrics?.record_count || 0;
  const fileCount = pipeline.metrics?.file_count || 0;
  const dataSize = String(pipeline.metrics?.data_size || '0 GB');

  return (
    <div 
      className="bg-white rounded-2xl shadow-md hover:shadow-lg transition-shadow duration-200"
      style={{ width: '480px' }}
    >
      {/* Card Header */}
      <div 
        className="px-6 py-5 border-b border-gray-100 cursor-pointer"
        style={{ height: '64px' }}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <span className="material-symbols-rounded text-blue-600 mr-3" style={{ fontSize: '20px' }}>
              science
            </span>
            <h3 className="text-2xl font-bold text-gray-900">
              {String(pipeline.display_name || pipeline.name || 'Unknown')}
            </h3>
          </div>
          <span className="material-symbols-rounded text-gray-400">
            {isExpanded ? 'expand_less' : 'expand_more'}
          </span>
        </div>
      </div>

      {/* Summary Stats (Collapsed State) */}
      {!isExpanded && (
        <div className="px-6 py-5">
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-gray-500 mb-1">Records</p>
              <p className="text-lg font-semibold text-gray-900">
                {Number(recordCount || 0).toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500 mb-1">Files</p>
              <p className="text-lg font-semibold text-gray-900">
                {Number(fileCount || 0).toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500 mb-1">Size</p>
              <p className="text-lg font-semibold text-gray-900">{dataSize}</p>
            </div>
          </div>
        </div>
      )}

      {/* Expanded Content */}
      {isExpanded && (
        <div className="px-6 py-5">
          {/* Summary Stats in Expanded State */}
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div>
              <p className="text-sm text-gray-500 mb-1">Records</p>
              <p className="text-lg font-semibold text-gray-900">
                {Number(recordCount || 0).toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500 mb-1">Files</p>
              <p className="text-lg font-semibold text-gray-900">
                {Number(fileCount || 0).toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500 mb-1">Size</p>
              <p className="text-lg font-semibold text-gray-900">{dataSize}</p>
            </div>
          </div>

          {/* File Explorer */}
          <div className="mb-6">
            <h4 className="text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wide">
              Files
            </h4>
            <FileExplorerTree files={pipeline.files} pipelineId={pipeline.id} />
          </div>

          {/* Data Table */}
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wide">
              Data Preview
            </h4>
            <DataTable pipelineId={pipeline.id} />
          </div>
        </div>
      )}

      {/* Expand Button */}
      {!isExpanded && (
        <div className="px-6 pb-5">
          <ExpandButton 
            isExpanded={isExpanded}
            onClick={() => setIsExpanded(true)}
          />
        </div>
      )}
    </div>
  );
}