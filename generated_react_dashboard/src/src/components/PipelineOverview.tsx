import React from 'react';
import type { Pipeline } from '../types.ts';

interface PipelineOverviewProps {
  pipelines: Pipeline[];
  selectedPipeline: Pipeline;
  onSelectPipeline: (pipeline: Pipeline) => void;
}

export default function PipelineOverview({ pipelines, selectedPipeline, onSelectPipeline }: PipelineOverviewProps) {
  const getStatusColor = (status: string) => {
    const statusStr = String(status || 'unknown').toLowerCase();
    switch (statusStr) {
      case 'processed':
      case 'complete':
        return 'text-green-600 bg-green-50';
      case 'processing':
        return 'text-blue-600 bg-blue-50';
      case 'error':
      case 'failed':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
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
    <div className="space-y-4">
      <h2 className="text-xl font-semibold text-gray-900">Data Sources</h2>
      
      <div className="grid grid-cols-1 gap-4">
        {pipelines.map((pipeline) => (
          <div
            key={pipeline.id}
            onClick={() => onSelectPipeline(pipeline)}
            className={`bg-white rounded-lg shadow-md p-6 cursor-pointer transition-all hover:shadow-lg ${
              selectedPipeline.id === pipeline.id ? 'ring-2 ring-primary-600' : ''
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {pipeline.display_name || pipeline.name}
                  </h3>
                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(pipeline.status)}`}>
                    <span className="material-symbols-rounded text-sm mr-1">{getStatusIcon(pipeline.status)}</span>
                    {String(pipeline.status || 'unknown').replace(/_/g, ' ')}
                  </span>
                </div>
                
                <div className="grid grid-cols-3 gap-4 mt-4">
                  <div className="flex items-center text-gray-600">
                    <span className="material-symbols-rounded text-xl mr-2">folder</span>
                    <div>
                      <p className="text-2xl font-bold text-gray-900">
                        {(pipeline.metrics?.file_count || 0).toLocaleString()}
                      </p>
                      <p className="text-sm">Files</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center text-gray-600">
                    <span className="material-symbols-rounded text-xl mr-2">table_rows</span>
                    <div>
                      <p className="text-2xl font-bold text-gray-900">
                        {(pipeline.metrics?.record_count || 0).toLocaleString()}
                      </p>
                      <p className="text-sm">Records</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center text-gray-600">
                    <span className="material-symbols-rounded text-xl mr-2">storage</span>
                    <div>
                      <p className="text-2xl font-bold text-gray-900">
                        {pipeline.metrics?.data_size || '0 B'}
                      </p>
                      <p className="text-sm">Size</p>
                    </div>
                  </div>
                </div>

                <div className="mt-4 flex items-center gap-2">
                  <span className="text-sm text-gray-500">Pipeline Stages:</span>
                  {pipeline.stages?.map((stage, idx) => (
                    <span
                      key={idx}
                      className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${getStatusColor(stage.status)}`}
                    >
                      {String(stage.name || 'unknown').replace(/_/g, ' ')}
                    </span>
                  )) || <span className="text-sm text-gray-400">No stages</span>}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}