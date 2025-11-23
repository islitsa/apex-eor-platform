import React from 'react';
import type { Pipeline } from '../types.ts';

interface PipelineStagesProps {
  pipelines: Pipeline[];
}

export default function PipelineStages({ pipelines }: PipelineStagesProps) {
  const getStageStatus = (value: any): 'complete' | 'in_progress' | 'not_started' | 'info' => {
    if (typeof value === 'string') {
      if (value === 'complete') return 'complete';
      if (value === 'in_progress') return 'in_progress';
      if (value === 'not_started') return 'not_started';
    }
    return 'info';
  };

  const getStageIcon = (status: string) => {
    switch (status) {
      case 'complete':
        return 'check_circle';
      case 'in_progress':
        return 'pending';
      case 'not_started':
        return 'radio_button_unchecked';
      default:
        return 'info';
    }
  };

  const getStageColor = (status: string) => {
    switch (status) {
      case 'complete':
        return 'text-success bg-green-50';
      case 'in_progress':
        return 'text-warning bg-yellow-50';
      case 'not_started':
        return 'text-text-secondary bg-gray-50';
      default:
        return 'text-primary bg-blue-50';
    }
  };

  const formatStageName = (key: string) => {
    return key.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  return (
    <div className="space-y-4">
      {pipelines.map((pipeline, idx) => (
        <div key={pipeline.id} className="bg-surface rounded-lg p-4 shadow-sm">
          <div className="text-sm font-medium text-text-secondary mb-3">
            {pipeline.name || formatStageName(pipeline.id)}
          </div>
          <div className="space-y-2">
            {Object.entries(pipeline.stages).map(([key, value]) => {
              const status = getStageStatus(value);
              const isInfoField = !['complete', 'in_progress', 'not_started'].includes(String(value));
              
              if (isInfoField) {
                return (
                  <div key={key} className="flex items-start gap-2 text-xs">
                    <span className="material-symbols-rounded text-primary" style={{ fontSize: '16px' }}>
                      info
                    </span>
                    <div className="flex-1">
                      <span className="text-text-secondary">{formatStageName(key)}:</span>
                      <span className="text-text-primary ml-1 font-medium">
                        {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                      </span>
                    </div>
                  </div>
                );
              }

              return (
                <div key={key} className={`flex items-center gap-2 p-2 rounded ${getStageColor(status)}`}>
                  <span className={`material-symbols-rounded ${getStageColor(status).split(' ')[0]}`} style={{ fontSize: '18px' }}>
                    {getStageIcon(status)}
                  </span>
                  <span className="text-sm font-medium flex-1">{formatStageName(key)}</span>
                  <span className="text-xs">{String(value)}</span>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}