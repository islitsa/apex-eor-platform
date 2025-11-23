import React from 'react';
import StatusBadgeSystem from './StatusBadgeSystem.tsx';
import type { Pipeline } from '../types';

interface PipelineHealthSidebarProps {
  pipeline: Pipeline;
}

export default function PipelineHealthSidebar({ pipeline }: PipelineHealthSidebarProps) {
  const stages = pipeline.stages || [];

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-bold text-gray-900 mb-6">Pipeline Health</h2>

      <div className="space-y-4">
        {stages.map((stage, index) => {
          const stageName = String(stage.name || 'unknown');
          const stageStatus = String(stage.status || 'unknown');
          
          return (
            <div key={index} className="border-b border-gray-100 pb-4 last:border-0">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-base font-semibold text-gray-900 capitalize">
                  {stageName.replace(/_/g, ' ')}
                </h3>
                <StatusBadgeSystem status={stageStatus} />
              </div>

              <div className="space-y-1 text-sm text-gray-600">
                {stage.file_count !== undefined && (
                  <div className="flex justify-between">
                    <span>Files:</span>
                    <span className="font-medium">{Number(stage.file_count || 0).toLocaleString()}</span>
                  </div>
                )}
                {stage.record_count !== undefined && (
                  <div className="flex justify-between">
                    <span>Records:</span>
                    <span className="font-medium">{Number(stage.record_count || 0).toLocaleString()}</span>
                  </div>
                )}
                {stage.last_updated && (
                  <div className="flex justify-between">
                    <span>Updated:</span>
                    <span className="font-medium">
                      {new Date(stage.last_updated).toLocaleDateString()}
                    </span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {stages.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <span className="material-symbols-rounded text-3xl mb-2">info</span>
          <p className="text-sm">No pipeline stages available</p>
        </div>
      )}
    </div>
  );
}