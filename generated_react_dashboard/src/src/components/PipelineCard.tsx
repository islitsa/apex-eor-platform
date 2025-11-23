import React, { useState } from 'react';
import { Pipeline } from '../types.ts';

interface PipelineCardProps {
  pipeline: Pipeline;
}

export default function PipelineCard({ pipeline }: PipelineCardProps) {
  const [expanded, setExpanded] = useState(false);

  const getStatusColor = (status: string): string => {
    const statusStr = String(status || '').toLowerCase();
    switch (statusStr) {
      case 'processed':
      case 'complete':
        return 'text-green-700 bg-green-100';
      case 'processing':
        return 'text-blue-700 bg-blue-100';
      case 'error':
      case 'failed':
        return 'text-red-700 bg-red-100';
      default:
        return 'text-gray-700 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string): string => {
    const statusStr = String(status || '').toLowerCase();
    switch (statusStr) {
      case 'processed':
      case 'complete':
        return 'check_circle';
      case 'processing':
        return 'pending';
      case 'error':
      case 'failed':
        return 'error';
      default:
        return 'help';
    }
  };

  const formatStatus = (status: string): string => {
    return String(status || 'unknown')
      .replace(/_/g, ' ')
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const validStages = (pipeline.stages || []).filter(stage => 
    stage && typeof stage === 'object' && stage.name
  );

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
              <span className="material-symbols-rounded text-2xl text-primary-700">
                oil_barrel
              </span>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                {pipeline.display_name || pipeline.name || pipeline.id}
              </h3>
              <p className="text-sm text-gray-500">{pipeline.id}</p>
            </div>
          </div>
          <span
            className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(
              pipeline.status
            )}`}
          >
            <span className="material-symbols-rounded text-sm">
              {getStatusIcon(pipeline.status)}
            </span>
            {formatStatus(pipeline.status)}
          </span>
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-3 gap-4">
          <div>
            <p className="text-xs text-gray-500 mb-1">Files</p>
            <p className="text-lg font-semibold text-gray-900">
              {(Number(pipeline.metrics?.file_count) || 0).toLocaleString()}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 mb-1">Records</p>
            <p className="text-lg font-semibold text-gray-900">
              {(Number(pipeline.metrics?.record_count) || 0).toLocaleString()}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 mb-1">Size</p>
            <p className="text-lg font-semibold text-gray-900">
              {String(pipeline.metrics?.data_size || '0 B')}
            </p>
          </div>
        </div>
      </div>

      {/* Stages */}
      {validStages.length > 0 && (
        <div className="p-6">
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center justify-between w-full text-left mb-3"
          >
            <h4 className="text-sm font-semibold text-gray-700">
              Pipeline Stages ({validStages.length})
            </h4>
            <span className="material-symbols-rounded text-gray-400">
              {expanded ? 'expand_less' : 'expand_more'}
            </span>
          </button>

          {expanded && (
            <div className="space-y-2">
              {validStages.map((stage, index) => (
                <div
                  key={`${pipeline.id}-stage-${index}`}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <span className="material-symbols-rounded text-sm text-gray-500">
                      {index === 0 ? 'download' : index === validStages.length - 1 ? 'check' : 'transform'}
                    </span>
                    <span className="text-sm font-medium text-gray-900">
                      {String(stage.name || 'Unknown')}
                    </span>
                  </div>
                  <span
                    className={`text-xs px-2 py-1 rounded-full ${getStatusColor(
                      stage.status
                    )}`}
                  >
                    {formatStatus(stage.status)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}