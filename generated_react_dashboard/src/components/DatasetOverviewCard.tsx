import React, { useState } from 'react';
import type { Pipeline } from '../types';

interface Props {
  pipeline: Pipeline;
  isSelected: boolean;
  onClick: () => void;
}

export default function DatasetOverviewCard({ pipeline, isSelected, onClick }: Props) {
  const [isExpanded, setIsExpanded] = useState(false);

  const getStatusColor = (status: string) => {
    const statusStr = String(status || '').toLowerCase();
    if (statusStr.includes('complete') || statusStr.includes('success')) return 'text-green-600 bg-green-50';
    if (statusStr.includes('running') || statusStr.includes('progress')) return 'text-yellow-600 bg-yellow-50';
    if (statusStr.includes('error') || statusStr.includes('failed')) return 'text-red-600 bg-red-50';
    return 'text-gray-600 bg-gray-50';
  };

  return (
    <div
      className={`rounded-lg border-2 transition-all cursor-pointer ${
        isSelected
          ? 'border-blue-500 bg-blue-50 shadow-md'
          : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm'
      }`}
      onClick={onClick}
    >
      <div className="p-6">
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1">
            <h3 className="text-xl font-bold text-gray-900 mb-1">
              {String(pipeline.display_name || pipeline.name || 'Unknown')}
            </h3>
            <div className="flex items-center gap-2">
              <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(pipeline.status)}`}>
                {String(pipeline.status || 'unknown').replace(/_/g, ' ')}
              </span>
            </div>
          </div>
          <button
            onClick={(e) => {
              e.stopPropagation();
              setIsExpanded(!isExpanded);
            }}
            className="text-gray-400 hover:text-gray-600"
          >
            <span className="material-symbols-rounded">
              {isExpanded ? 'expand_less' : 'expand_more'}
            </span>
          </button>
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Records</span>
            <span className="font-semibold text-gray-900">
              {Number(pipeline.metrics?.record_count || 0).toLocaleString()}
            </span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Files</span>
            <span className="font-semibold text-gray-900">
              {Number(pipeline.metrics?.file_count || 0).toLocaleString()}
            </span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Size</span>
            <span className="font-semibold text-gray-900">
              {String(pipeline.metrics?.data_size || '0 MB')}
            </span>
          </div>
        </div>

        {isExpanded && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <h4 className="text-xs font-semibold text-gray-700 mb-2 uppercase">Pipeline Health</h4>
            <div className="space-y-2">
              {pipeline.stages?.map((stage, idx) => {
                const stageName = String(stage.name || 'unknown');
                const stageStatus = String(stage.status || 'unknown');
                
                return (
                  <div key={idx} className="flex items-center justify-between text-sm">
                    <span className="text-gray-600 capitalize">
                      {stageName.replace(/_/g, ' ')}
                    </span>
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${getStatusColor(stageStatus)}`}>
                      {stageStatus.replace(/_/g, ' ')}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}