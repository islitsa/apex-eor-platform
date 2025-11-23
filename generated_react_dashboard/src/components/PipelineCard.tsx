import React from 'react';
import type { Pipeline } from '../types.ts';

interface PipelineCardProps {
  pipeline: Pipeline;
  onClick: () => void;
}

export default function PipelineCard({ pipeline, onClick }: PipelineCardProps) {
  const getStatusColor = (status: string) => {
    const statusStr = String(status || 'unknown').toLowerCase();
    switch (statusStr) {
      case 'processed':
      case 'complete':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'processing':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'error':
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    const statusStr = String(status || 'unknown').toLowerCase();
    switch (statusStr) {
      case 'processed':
      case 'complete':
        return 'check_circle';
      case 'processing':
        return 'sync';
      case 'error':
      case 'failed':
        return 'error';
      default:
        return 'help';
    }
  };

  return (
    <div
      onClick={onClick}
      className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:shadow-md transition-all cursor-pointer hover:border-blue-300"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            {pipeline.display_name}
          </h3>
          <div className="flex items-center gap-2">
            <span
              className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium border ${getStatusColor(
                pipeline.status
              )}`}
            >
              <span className="material-symbols-rounded text-[18px]">
                {getStatusIcon(pipeline.status)}
              </span>
              {String(pipeline.status || 'unknown').replace(/_/g, ' ')}
            </span>
          </div>
        </div>
        <span className="material-symbols-rounded text-gray-400">chevron_right</span>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-4">
        <div>
          <p className="text-sm text-gray-600 mb-1">Files</p>
          <p className="text-2xl font-bold text-gray-900">
            {(pipeline.metrics?.file_count || 0).toLocaleString()}
          </p>
        </div>
        <div>
          <p className="text-sm text-gray-600 mb-1">Records</p>
          <p className="text-2xl font-bold text-gray-900">
            {(pipeline.metrics?.record_count || 0).toLocaleString()}
          </p>
        </div>
        <div>
          <p className="text-sm text-gray-600 mb-1">Size</p>
          <p className="text-2xl font-bold text-gray-900">
            {pipeline.metrics?.data_size || '0 B'}
          </p>
        </div>
      </div>

      <div>
        <p className="text-sm font-medium text-gray-700 mb-2">Pipeline Stages</p>
        <div className="flex items-center gap-2">
          {pipeline.stages?.map((stage, index) => (
            <React.Fragment key={index}>
              <div
                className={`flex items-center gap-1 px-3 py-1 rounded-lg text-sm ${getStatusColor(
                  stage.status
                )}`}
              >
                <span className="material-symbols-rounded text-[16px]">
                  {getStatusIcon(stage.status)}
                </span>
                <span className="font-medium">
                  {String(stage.name || 'unknown').replace(/_/g, ' ')}
                </span>
              </div>
              {index < pipeline.stages.length - 1 && (
                <span className="material-symbols-rounded text-gray-400 text-[16px]">
                  arrow_forward
                </span>
              )}
            </React.Fragment>
          )) ?? null}
        </div>
      </div>
    </div>
  );
}