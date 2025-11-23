import React, { useState } from 'react';
import StageStatusBadge from './StageStatusBadge.tsx';
import type { Pipeline, Stage } from '../types';

interface PipelineHealthCardProps {
  pipeline: Pipeline;
}

export default function PipelineHealthCard({ pipeline }: PipelineHealthCardProps) {
  const [expandedStage, setExpandedStage] = useState<string | null>(null);

  const stages = pipeline.stages || [];

  const getOverallHealth = (): { status: string; color: string; icon: string } => {
    if (stages.length === 0) {
      return { status: 'Unknown', color: 'gray', icon: 'help' };
    }

    const hasError = stages.some(s => String(s.status || '').toLowerCase().includes('error'));
    const hasPending = stages.some(s => String(s.status || '').toLowerCase().includes('pending'));
    const allComplete = stages.every(s => String(s.status || '').toLowerCase().includes('complete'));

    if (hasError) {
      return { status: 'Error', color: 'red', icon: 'error' };
    }
    if (hasPending) {
      return { status: 'In Progress', color: 'yellow', icon: 'pending' };
    }
    if (allComplete) {
      return { status: 'Healthy', color: 'green', icon: 'check_circle' };
    }

    return { status: 'Unknown', color: 'gray', icon: 'help' };
  };

  const health = getOverallHealth();

  return (
    <div className="bg-white rounded-2xl shadow-md overflow-hidden">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">Pipeline Health</h2>
        
        <div className={`flex items-center gap-3 p-3 rounded-lg bg-${health.color}-50`}>
          <span className={`material-symbols-rounded text-${health.color}-600 text-3xl`}>
            {health.icon}
          </span>
          <div>
            <p className={`font-semibold text-${health.color}-900`}>{health.status}</p>
            <p className="text-sm text-gray-600">
              {stages.length} {stages.length === 1 ? 'stage' : 'stages'}
            </p>
          </div>
        </div>
      </div>

      <div className="divide-y divide-gray-100">
        {stages.map((stage, idx) => {
          const stageName = String(stage.name || `Stage ${idx + 1}`);
          const isExpanded = expandedStage === stageName;

          return (
            <div key={idx}>
              <button
                onClick={() => setExpandedStage(isExpanded ? null : stageName)}
                className="w-full px-4 py-3 hover:bg-gray-50 transition-colors text-left"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3 flex-grow min-w-0">
                    <StageStatusBadge status={String(stage.status || 'unknown')} />
                    <div className="flex-grow min-w-0">
                      <h3 className="font-medium text-gray-900 truncate">
                        {String(stageName).replace(/_/g, ' ')}
                      </h3>
                      {stage.records !== undefined && (
                        <p className="text-sm text-gray-600">
                          {Number(stage.records || 0).toLocaleString()} records
                        </p>
                      )}
                    </div>
                  </div>
                  <span
                    className={`material-symbols-rounded text-gray-400 transition-transform ${
                      isExpanded ? 'rotate-90' : ''
                    }`}
                  >
                    chevron_right
                  </span>
                </div>
              </button>

              {isExpanded && (
                <div className="px-4 py-3 bg-gray-50 border-t border-gray-100">
                  <dl className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <dt className="text-gray-600">Status:</dt>
                      <dd className="font-medium text-gray-900">
                        {String(stage.status || 'unknown').replace(/_/g, ' ')}
                      </dd>
                    </div>
                    {stage.files !== undefined && (
                      <div className="flex justify-between">
                        <dt className="text-gray-600">Files:</dt>
                        <dd className="font-medium text-gray-900">
                          {Number(stage.files || 0).toLocaleString()}
                        </dd>
                      </div>
                    )}
                    {stage.records !== undefined && (
                      <div className="flex justify-between">
                        <dt className="text-gray-600">Records:</dt>
                        <dd className="font-medium text-gray-900">
                          {Number(stage.records || 0).toLocaleString()}
                        </dd>
                      </div>
                    )}
                    {stage.last_updated && (
                      <div className="flex justify-between">
                        <dt className="text-gray-600">Last Updated:</dt>
                        <dd className="font-medium text-gray-900">
                          {new Date(String(stage.last_updated)).toLocaleDateString()}
                        </dd>
                      </div>
                    )}
                  </dl>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}