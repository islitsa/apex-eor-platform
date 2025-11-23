import React from 'react';
import type { Stage } from '../types.ts';

interface PipelineHealthBannerProps {
  stages: Stage[];
}

export default function PipelineHealthBanner({ stages }: PipelineHealthBannerProps) {
  const getStageIcon = (stageName: string): string => {
    const name = String(stageName || '').toLowerCase();
    if (name.includes('download')) return 'download';
    if (name.includes('extract')) return 'transform';
    if (name.includes('parse') || name.includes('process')) return 'done';
    if (name.includes('storage') || name.includes('store')) return 'storage';
    return 'circle';
  };

  const getStageColor = (status: string): string => {
    const statusStr = String(status || 'unknown').toLowerCase();
    if (statusStr === 'complete' || statusStr === 'success') return 'bg-green-500 text-white';
    if (statusStr === 'processing' || statusStr === 'running') return 'bg-yellow-500 text-white';
    if (statusStr === 'error' || statusStr === 'failed') return 'bg-red-500 text-white';
    return 'bg-gray-300 text-gray-600';
  };

  // Filter out metadata fields that aren't actual stages
  const actualStages = stages.filter(stage => 
    stage.name && typeof stage.status === 'string'
  );

  if (actualStages.length === 0) {
    return (
      <div className="bg-gray-50 rounded-xl p-6">
        <div className="flex items-center gap-2 mb-4">
          <span className="material-symbols-rounded text-gray-700">timeline</span>
          <h3 className="text-xl font-semibold text-gray-900">Pipeline Health</h3>
        </div>
        <p className="text-gray-600">No pipeline stages available</p>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6">
      <div className="flex items-center gap-2 mb-6">
        <span className="material-symbols-rounded text-gray-700">timeline</span>
        <h3 className="text-xl font-semibold text-gray-900">Pipeline Health</h3>
      </div>

      <div className="flex items-center justify-between relative">
        {/* Progress Line */}
        <div className="absolute top-6 left-6 right-6 h-1 bg-gray-300 -z-0" />

        {actualStages.map((stage, index) => (
          <div key={index} className="flex flex-col items-center gap-3 relative z-10">
            {/* Stage Circle */}
            <div
              className={`w-12 h-12 rounded-full flex items-center justify-center shadow-md transition-all duration-200 hover:scale-110 ${getStageColor(
                stage.status
              )}`}
            >
              <span className="material-symbols-rounded text-2xl">
                {getStageIcon(stage.name)}
              </span>
            </div>

            {/* Stage Info */}
            <div className="text-center min-w-[120px]">
              <div className="font-semibold text-gray-900 text-sm">
                {String(stage.name || 'Unknown').replace(/_/g, ' ')}
              </div>
              <div className="text-xs text-gray-600 mt-1">
                {String(stage.status || 'unknown').replace(/_/g, ' ')}
              </div>
              {stage.records !== undefined && (
                <div className="text-xs text-gray-500 mt-1">
                  {Number(stage.records || 0).toLocaleString()} records
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}