import React, { useState } from 'react';
import type { Pipeline } from '../types';
import PipelineHealthIndicator from './PipelineHealthIndicator.tsx';

interface Props {
  pipeline: Pipeline;
  isSelected: boolean;
  onSelect: (pipeline: Pipeline) => void;
}

export default function DatasetOverviewCards({ pipeline, isSelected, onSelect }: Props) {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleClick = () => {
    setIsExpanded(!isExpanded);
    onSelect(pipeline);
  };

  const fileCount = pipeline.metrics?.file_count || 0;
  const recordCount = pipeline.metrics?.record_count || 0;
  const dataSize = pipeline.metrics?.data_size || '0 B';

  return (
    <div
      className={`w-80 bg-white rounded-lg shadow-lg p-4 cursor-pointer transition-all duration-300 ${
        isSelected ? 'ring-2 ring-blue-500' : 'hover:shadow-xl'
      }`}
      onClick={handleClick}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h3 className="text-lg font-bold text-gray-900 mb-1">
            {pipeline.display_name || pipeline.name}
          </h3>
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <span className="material-symbols-rounded text-base">description</span>
              <span>{fileCount.toLocaleString()} files</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <span className="material-symbols-rounded text-base">storage</span>
              <span>{recordCount.toLocaleString()} records</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <span className="material-symbols-rounded text-base">hard_drive</span>
              <span>{dataSize}</span>
            </div>
          </div>
        </div>
        <span
          className={`material-symbols-rounded text-gray-400 transition-transform duration-300 ${
            isExpanded ? 'rotate-180' : ''
          }`}
        >
          expand_more
        </span>
      </div>

      {/* Expandable section */}
      <div
        className={`overflow-hidden transition-all duration-300 ${
          isExpanded ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'
        }`}
      >
        <div className="pt-3 border-t border-gray-200 mt-3">
          <h4 className="text-sm font-semibold text-gray-700 mb-2">Pipeline Health</h4>
          <PipelineHealthIndicator stages={pipeline.stages || []} />
        </div>
      </div>
    </div>
  );
}