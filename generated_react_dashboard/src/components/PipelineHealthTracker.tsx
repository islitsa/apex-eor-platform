import React from 'react';
import type { Pipeline, Stage } from '../types';

interface Props {
  pipeline: Pipeline | null;
}

export default function PipelineHealthTracker({ pipeline }: Props) {
  if (!pipeline) {
    return (
      <div className="bg-white rounded-2xl shadow-md p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Pipeline Health</h2>
        <div className="text-center text-gray-500 py-8">
          <span className="material-symbols-rounded text-4xl mb-2">pending</span>
          <p>Select a dataset to view pipeline health</p>
        </div>
      </div>
    );
  }

  const stages = pipeline.stages || [];
  const validStages = stages.filter(stage => 
    stage && typeof stage === 'object' && stage.name && stage.status
  );

  const getStatusIcon = (status: string): string => {
    const statusStr = String(status || '').toLowerCase();
    if (statusStr === 'complete' || statusStr === 'success') return 'check_circle';
    if (statusStr === 'running' || statusStr === 'in_progress') return 'pending';
    if (statusStr === 'failed' || statusStr === 'error') return 'error';
    return 'pending';
  };

  const getStatusColor = (status: string): string => {
    const statusStr = String(status || '').toLowerCase();
    if (statusStr === 'complete' || statusStr === 'success') return 'text-green-600 bg-green-50';
    if (statusStr === 'running' || statusStr === 'in_progress') return 'text-amber-600 bg-amber-50';
    if (statusStr === 'failed' || statusStr === 'error') return 'text-red-600 bg-red-50';
    return 'text-gray-600 bg-gray-50';
  };

  const getLineColor = (status: string): string => {
    const statusStr = String(status || '').toLowerCase();
    if (statusStr === 'complete' || statusStr === 'success') return 'bg-green-600';
    if (statusStr === 'running' || statusStr === 'in_progress') return 'bg-amber-600';
    if (statusStr === 'failed' || statusStr === 'error') return 'bg-red-600';
    return 'bg-gray-300';
  };

  return (
    <div className="bg-white rounded-2xl shadow-md p-6">
      <h2 className="text-xl font-bold text-gray-900 mb-6">Pipeline Health</h2>
      
      <div className="space-y-1">
        {validStages.map((stage, index) => (
          <div key={index} className="relative">
            <div className="flex items-start gap-4">
              <div className="relative flex flex-col items-center">
                <div className={`w-14 h-14 rounded-full flex items-center justify-center ${getStatusColor(stage.status)}`}>
                  <span className={`material-symbols-rounded text-2xl ${getStatusColor(stage.status).split(' ')[0]}`}>
                    {getStatusIcon(stage.status)}
                  </span>
                </div>
                {index < validStages.length - 1 && (
                  <div className={`w-0.5 h-12 ${getLineColor(stage.status)} mt-2`}></div>
                )}
              </div>
              
              <div className="flex-1 pt-3">
                <h3 className="font-semibold text-gray-900 capitalize mb-1">
                  {String(stage.name || '').replace(/_/g, ' ')}
                </h3>
                <div className="space-y-1 text-sm text-gray-600">
                  <div className="flex items-center justify-between">
                    <span>Status</span>
                    <span className="font-medium capitalize">
                      {String(stage.status || 'unknown').replace(/_/g, ' ')}
                    </span>
                  </div>
                  {stage.file_count !== undefined && (
                    <div className="flex items-center justify-between">
                      <span>Files</span>
                      <span className="font-medium">
                        {Number(stage.file_count || 0).toLocaleString()}
                      </span>
                    </div>
                  )}
                  {stage.record_count !== undefined && (
                    <div className="flex items-center justify-between">
                      <span>Records</span>
                      <span className="font-medium">
                        {Number(stage.record_count || 0).toLocaleString()}
                      </span>
                    </div>
                  )}
                  {stage.last_updated && (
                    <div className="flex items-center justify-between">
                      <span>Updated</span>
                      <span className="font-medium text-xs">
                        {new Date(stage.last_updated).toLocaleDateString()}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {validStages.length === 0 && (
        <div className="text-center text-gray-500 py-8">
          <span className="material-symbols-rounded text-4xl mb-2">info</span>
          <p>No pipeline stages available</p>
        </div>
      )}
    </div>
  );
}