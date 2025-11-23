import React, { useState } from 'react';
import FileExplorerTree from './FileExplorerTree.tsx';
import type { Pipeline } from '../types';

interface DatasetMasterCardProps {
  pipeline: Pipeline;
  isSelected: boolean;
  onSelect: (pipeline: Pipeline) => void;
}

export default function DatasetMasterCard({ pipeline, isSelected, onSelect }: DatasetMasterCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleToggle = () => {
    setIsExpanded(!isExpanded);
    if (!isExpanded) {
      onSelect(pipeline);
    }
  };

  const dataSizeGB = pipeline.metrics?.data_size 
    ? parseFloat(String(pipeline.metrics.data_size).replace(/[^0-9.]/g, '')) / 1024
    : 0;

  return (
    <div 
      className={`w-full max-w-4xl bg-white rounded-3xl shadow-md transition-all duration-300 cursor-pointer ${
        isExpanded ? 'shadow-xl' : 'hover:shadow-lg hover:scale-[1.02]'
      }`}
      onClick={handleToggle}
    >
      {/* Card Header */}
      <div className="p-8">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-blue-100 rounded-xl flex items-center justify-center">
              <span className="material-symbols-rounded text-blue-600 text-3xl">science</span>
            </div>
            <div>
              <h3 className="text-2xl font-bold text-gray-900">
                {pipeline.display_name || pipeline.name}
              </h3>
              <p className="text-gray-600 mt-1">Chemical Data Repository</p>
            </div>
          </div>
          
          <span className={`material-symbols-rounded text-gray-400 text-3xl transition-transform ${
            isExpanded ? 'rotate-180' : ''
          }`}>
            expand_more
          </span>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-3 gap-6 mt-6">
          <div className="bg-gray-50 rounded-xl p-4">
            <p className="text-gray-600 text-sm font-medium">Total Records</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">
              {(pipeline.metrics?.record_count || 0).toLocaleString()}
            </p>
          </div>
          <div className="bg-gray-50 rounded-xl p-4">
            <p className="text-gray-600 text-sm font-medium">Files</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">
              {(pipeline.metrics?.file_count || 0).toLocaleString()}
            </p>
          </div>
          <div className="bg-gray-50 rounded-xl p-4">
            <p className="text-gray-600 text-sm font-medium">Data Size</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">
              {Number(dataSizeGB || 0).toFixed(2)} GB
            </p>
          </div>
        </div>

        {/* Pipeline Stages */}
        <div className="flex items-center gap-4 mt-6">
          {pipeline.stages?.map((stage, index) => (
            <React.Fragment key={stage.name}>
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${
                  String(stage.status || '').toLowerCase() === 'complete'
                    ? 'bg-green-500'
                    : 'bg-gray-300'
                }`} />
                <span className="text-sm font-medium text-gray-700 capitalize">
                  {String(stage.name || '').replace(/_/g, ' ')}
                </span>
              </div>
              {index < (pipeline.stages?.length || 0) - 1 && (
                <span className="material-symbols-rounded text-gray-300 text-sm">arrow_forward</span>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Expanded File Explorer */}
      {isExpanded && (
        <div className="border-t border-gray-200 p-8 bg-gray-50" onClick={(e) => e.stopPropagation()}>
          <FileExplorerTree pipeline={pipeline} />
        </div>
      )}
    </div>
  );
}