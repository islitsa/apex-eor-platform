import React, { useState } from 'react';
import type { Pipeline } from '../types.ts';
import FileExplorer from './FileExplorer.tsx';

interface DatasetHeroCardProps {
  pipeline: Pipeline;
  isSelected: boolean;
  onSelect: () => void;
}

export default function DatasetHeroCard({ pipeline, isSelected, onSelect }: DatasetHeroCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleToggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'complete':
      case 'processed':
        return 'text-green-600 bg-green-50';
      case 'in_progress':
      case 'processing':
        return 'text-blue-600 bg-blue-50';
      case 'pending':
      case 'not_started':
        return 'text-gray-600 bg-gray-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div
      className={`bg-white rounded-lg shadow-md transition-all duration-400 overflow-hidden ${
        isSelected ? 'ring-2 ring-primary-500' : ''
      }`}
      style={{ minHeight: isExpanded ? '400px' : '240px' }}
    >
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <span className="material-symbols-rounded text-4xl text-primary-600">folder_open</span>
            <div>
              <h3 className="text-xl font-bold text-gray-900">{pipeline.name}</h3>
              <p className="text-sm text-gray-500">{pipeline.id}</p>
            </div>
          </div>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(pipeline.status)}`}>
            {pipeline.status}
          </span>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-sm text-gray-500">Files</div>
            <div className="text-2xl font-semibold text-gray-900">{pipeline.file_count}</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-sm text-gray-500">Data Size</div>
            <div className="text-2xl font-semibold text-gray-900">{pipeline.data_size_human}</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-sm text-gray-500">Stages</div>
            <div className="text-2xl font-semibold text-gray-900">{Object.keys(pipeline.stages).length}</div>
          </div>
        </div>

        {/* Pipeline Stages */}
        <div className="flex items-center gap-2 mb-4 overflow-x-auto pb-2">
          {Object.entries(pipeline.stages).map(([stageName, stage], index) => {
            const isComplete = stage.status === 'complete';
            const isInProgress = stage.status === 'in_progress';
            const isPending = stage.status === 'not_started' || stage.status === 'pending';

            return (
              <React.Fragment key={stageName}>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      isComplete
                        ? 'bg-green-500 text-white'
                        : isInProgress
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-300 text-gray-600'
                    }`}
                  >
                    <span className="material-symbols-rounded text-sm">
                      {isComplete ? 'check_circle' : isInProgress ? 'sync' : 'circle'}
                    </span>
                  </div>
                  <span className="text-sm font-medium text-gray-700">{stageName}</span>
                </div>
                {index < Object.keys(pipeline.stages).length - 1 && (
                  <div className="w-8 h-0.5 bg-gray-300 flex-shrink-0"></div>
                )}
              </React.Fragment>
            );
          })}
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3">
          <button
            onClick={handleToggleExpand}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            <span className="material-symbols-rounded text-sm">
              {isExpanded ? 'expand_less' : 'expand_more'}
            </span>
            <span>{isExpanded ? 'Hide Files' : 'View Files'}</span>
          </button>
          <button
            onClick={onSelect}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              isSelected
                ? 'bg-primary-100 text-primary-700 border border-primary-300'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <span className="material-symbols-rounded text-sm">
              {isSelected ? 'visibility' : 'visibility_off'}
            </span>
            <span>{isSelected ? 'Hide Data' : 'Show Data'}</span>
          </button>
        </div>

        {/* File Explorer */}
        {isExpanded && (
          <div className="mt-6 border-t border-gray-200 pt-4">
            <FileExplorer files={pipeline.files} />
          </div>
        )}
      </div>
    </div>
  );
}