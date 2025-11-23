import React from 'react';
import { Pipeline } from '../types.ts';

interface PipelineStatusProps {
  pipeline: Pipeline;
}

export default function PipelineStatus({ pipeline }: PipelineStatusProps) {
  const getStatusColor = (status: string | number | undefined) => {
    const statusStr = String(status || 'unknown').toLowerCase();
    if (statusStr.includes('complete') || statusStr.includes('processed')) return 'text-green-600 bg-green-50';
    if (statusStr.includes('processing') || statusStr.includes('running')) return 'text-blue-600 bg-blue-50';
    if (statusStr.includes('error') || statusStr.includes('failed')) return 'text-red-600 bg-red-50';
    return 'text-gray-600 bg-gray-50';
  };

  const getStatusIcon = (status: string | number | undefined) => {
    const statusStr = String(status || 'unknown').toLowerCase();
    if (statusStr.includes('complete') || statusStr.includes('processed')) return 'check_circle';
    if (statusStr.includes('processing') || statusStr.includes('running')) return 'sync';
    if (statusStr.includes('error') || statusStr.includes('failed')) return 'error';
    return 'help';
  };

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6 mb-8">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <span className="material-symbols-rounded text-blue-600 text-3xl">account_tree</span>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              {pipeline.display_name || pipeline.name || 'Unknown Pipeline'}
            </h2>
            <p className="text-gray-600 text-sm">Pipeline ID: {pipeline.id}</p>
          </div>
        </div>
        <div className={`px-4 py-2 rounded-full ${getStatusColor(pipeline.status)}`}>
          <div className="flex items-center gap-2">
            <span className="material-symbols-rounded text-lg">
              {getStatusIcon(pipeline.status)}
            </span>
            <span className="font-medium capitalize">
              {String(pipeline.status || 'unknown').replace(/_/g, ' ')}
            </span>
          </div>
        </div>
      </div>

      {/* Pipeline Metrics */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="text-gray-600 text-sm mb-1">Files</div>
          <div className="text-2xl font-bold text-gray-900">
            {Number(pipeline.metrics?.file_count || 0).toLocaleString()}
          </div>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="text-gray-600 text-sm mb-1">Records</div>
          <div className="text-2xl font-bold text-gray-900">
            {Number(pipeline.metrics?.record_count || 0).toLocaleString()}
          </div>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="text-gray-600 text-sm mb-1">Size</div>
          <div className="text-2xl font-bold text-gray-900">
            {pipeline.metrics?.data_size || '0 B'}
          </div>
        </div>
      </div>

      {/* Pipeline Stages */}
      {pipeline.stages && pipeline.stages.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wide">
            Pipeline Stages
          </h3>
          <div className="flex items-center gap-2">
            {pipeline.stages.map((stage, index) => (
              <React.Fragment key={index}>
                <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${getStatusColor(stage.status)}`}>
                  <span className="material-symbols-rounded text-lg">
                    {getStatusIcon(stage.status)}
                  </span>
                  <span className="font-medium capitalize">
                    {String(stage.name || 'unknown').replace(/_/g, ' ')}
                  </span>
                </div>
                {index < pipeline.stages.length - 1 && (
                  <span className="material-symbols-rounded text-gray-400">arrow_forward</span>
                )}
              </React.Fragment>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}