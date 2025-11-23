import React, { useState } from 'react';
import { Pipeline } from '../types.ts';
import StageIndicator from './StageIndicator.tsx';
import FileExplorer from './FileExplorer.tsx';

interface DatasetCardProps {
  pipeline: Pipeline;
}

export default function DatasetCard({ pipeline }: DatasetCardProps) {
  const [expanded, setExpanded] = useState(false);

  const stageOrder = ['download', 'extraction', 'parsing', 'validation', 'loading'];
  const orderedStages = stageOrder
    .filter(stage => pipeline.stages[stage])
    .map(stage => ({
      name: stage,
      ...pipeline.stages[stage]
    }));

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'processed':
      case 'complete':
        return 'bg-green-100 text-success';
      case 'processing':
        return 'bg-blue-100 text-primary';
      case 'not_started':
        return 'bg-gray-100 text-gray-600';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  const totalFiles = pipeline.files.file_count || 0;

  return (
    <div
      className={`bg-white rounded-2xl transition-all duration-300 ${
        expanded ? 'shadow-lg' : 'shadow-md hover:shadow-lg'
      }`}
    >
      {/* Card Header */}
      <div className="p-6">
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="bg-blue-50 p-3 rounded-xl">
              <span className="material-symbols-rounded text-primary text-2xl">science</span>
            </div>
            <div>
              <h3 className="text-2xl font-bold text-gray-900">{pipeline.name}</h3>
              <p className="text-sm text-gray-600 mt-1 font-mono">{pipeline.id}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className={`px-4 py-2 rounded-full text-sm font-medium ${getStatusColor(pipeline.status)}`}>
              {pipeline.status}
            </span>
          </div>
        </div>

        {/* Pipeline Stages */}
        <div className="flex items-center gap-4 mb-6">
          {orderedStages.map((stage, index) => (
            <React.Fragment key={stage.name}>
              <StageIndicator
                name={stage.name}
                status={stage.status}
                date={stage.date}
                note={stage.note}
              />
              {index < orderedStages.length - 1 && (
                <div className="flex-1 h-0.5 bg-gray-200"></div>
              )}
            </React.Fragment>
          ))}
        </div>

        {/* Metadata */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-gray-50 rounded-xl p-4">
            <p className="text-sm text-gray-600 mb-1">Total Files</p>
            <p className="text-2xl font-bold text-gray-900 font-mono">{totalFiles}</p>
          </div>
          <div className="bg-gray-50 rounded-xl p-4">
            <p className="text-sm text-gray-600 mb-1">Data Size</p>
            <p className="text-2xl font-bold text-gray-900 font-mono">{pipeline.data_size}</p>
          </div>
          {pipeline.parsed_files !== undefined && (
            <div className="bg-gray-50 rounded-xl p-4">
              <p className="text-sm text-gray-600 mb-1">Parsed Files</p>
              <p className="text-2xl font-bold text-gray-900 font-mono">{pipeline.parsed_files}</p>
            </div>
          )}
        </div>

        {/* Expand/Collapse Button */}
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full flex items-center justify-center gap-2 py-3 px-4 bg-gray-50 hover:bg-gray-100 rounded-xl transition-colors text-gray-700 font-medium"
        >
          <span>{expanded ? 'Hide Files' : 'Show Files'}</span>
          <span
            className={`material-symbols-rounded transition-transform duration-300 ${
              expanded ? 'rotate-180' : ''
            }`}
          >
            expand_more
          </span>
        </button>
      </div>

      {/* File Explorer (Expanded) */}
      {expanded && (
        <div className="border-t border-gray-200 p-6 bg-gray-50">
          <FileExplorer files={pipeline.files} />
        </div>
      )}
    </div>
  );
}