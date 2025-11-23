import React from 'react';
import type { Pipeline } from '../types.ts';
import StatusBadgeSystem from './StatusBadgeSystem.tsx';

interface PipelineHealthMonitorProps {
  pipeline: Pipeline;
}

export default function PipelineHealthMonitor({ pipeline }: PipelineHealthMonitorProps) {
  const stages = pipeline.stages || [];

  // Filter out metadata entries and only show actual stages
  const actualStages = stages.filter(stage => 
    stage.name && 
    typeof stage.status === 'string' &&
    !stage.name.includes('_at') &&
    !stage.name.includes('count')
  );

  const getStageIcon = (stageName: string, status: string) => {
    const normalizedStatus = String(status || 'unknown').toLowerCase();
    
    if (normalizedStatus === 'complete' || normalizedStatus === 'completed') {
      return 'check_circle';
    } else if (normalizedStatus === 'error' || normalizedStatus === 'failed') {
      return 'error';
    } else if (normalizedStatus === 'running' || normalizedStatus === 'in_progress') {
      return 'pending';
    }
    return 'pending';
  };

  const getStageLabel = (stageName: string) => {
    const name = String(stageName || '');
    if (name === 'downloads') return 'Download';
    if (name === 'extracted') return 'Extract';
    if (name === 'parsed') return 'Parse';
    if (name === 'validated') return 'Validate';
    return name.charAt(0).toUpperCase() + name.slice(1);
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 sticky top-6">
      <h3 className="text-base font-bold text-gray-900 mb-6">Pipeline Stages</h3>
      
      <div className="space-y-6">
        {actualStages.map((stage, index) => {
          const icon = getStageIcon(stage.name, stage.status);
          const label = getStageLabel(stage.name);
          const status = String(stage.status || 'unknown');

          return (
            <div key={`${stage.name}-${index}`}>
              <div className="flex flex-col items-center">
                <div className="w-20 h-20 rounded-full bg-gray-50 border-2 border-gray-200 flex items-center justify-center mb-3">
                  <span className={`material-symbols-rounded text-4xl ${
                    status === 'complete' || status === 'completed' ? 'text-green-600' :
                    status === 'error' || status === 'failed' ? 'text-red-600' :
                    'text-amber-600'
                  }`}>
                    {icon}
                  </span>
                </div>
                <div className="text-center">
                  <div className="font-bold text-sm text-gray-900 mb-1">{label}</div>
                  <StatusBadgeSystem status={status} />
                </div>
                {stage.record_count !== undefined && (
                  <div className="text-xs text-gray-500 mt-2">
                    {Number(stage.record_count || 0).toLocaleString()} records
                  </div>
                )}
              </div>
              {index < actualStages.length - 1 && (
                <div className="flex justify-center my-3">
                  <div className="w-0.5 h-8 bg-gray-300"></div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {actualStages.length === 0 && (
        <div className="text-center text-sm text-gray-500 py-8">
          No pipeline stages available
        </div>
      )}
    </div>
  );
}