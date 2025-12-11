import React from 'react';
import { Pipeline } from '../types';

interface Props {
  pipeline: Pipeline | null;
}

export default function PipelineHealthIndicator({ pipeline }: Props) {
  if (!pipeline) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <span className="material-symbols-rounded">trending_up</span>
          Pipeline Health
        </h2>
        <p className="text-gray-500">No pipeline selected</p>
      </div>
    );
  }

  const stages = pipeline.stages || [];
  const stageIcons: Record<string, string> = {
    'download': 'download',
    'extract': 'folder_zip',
    'parsing': 'description',
    'complete': 'check_circle'
  };

  const statusColors: Record<string, string> = {
    'complete': 'text-green-600 bg-green-50',
    'pending': 'text-yellow-600 bg-yellow-50',
    'processing': 'text-blue-600 bg-blue-50',
    'error': 'text-red-600 bg-red-50'
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
      <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
        <span className="material-symbols-rounded">trending_up</span>
        Pipeline Health
      </h2>

      <div className="space-y-3">
        {stages.map((stage, index) => {
          const stageName = String(stage.name || '');
          const stageStatus = String(stage.status || 'unknown');
          const icon = stageIcons[stageName] || 'pending';
          const colorClass = statusColors[stageStatus] || 'text-gray-600 bg-gray-50';

          return (
            <div key={index} className="flex items-center gap-4">
              <span className={`material-symbols-rounded ${colorClass.split(' ')[0]} p-2 rounded-full ${colorClass.split(' ')[1]}`}>
                {icon}
              </span>
              <div className="flex-1">
                <div className="font-medium text-gray-900 capitalize">
                  {String(stageName || '').replace(/_/g, ' ')}
                </div>
                <div className="text-sm text-gray-600 capitalize">
                  {String(stageStatus || '').replace(/_/g, ' ')}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Overall Status</span>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusColors[pipeline.status] || 'text-gray-600 bg-gray-50'}`}>
            {String(pipeline.status || 'unknown').replace(/_/g, ' ')}
          </span>
        </div>
      </div>
    </div>
  );
}