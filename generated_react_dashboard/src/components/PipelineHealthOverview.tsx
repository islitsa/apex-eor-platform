import React, { useMemo } from 'react';
import StageStatusBadges from './StageStatusBadges.tsx';
import type { Pipeline, StageStatus } from '../types';

interface Props {
  pipelines: Pipeline[];
}

export default function PipelineHealthOverview({ pipelines }: Props) {
  const stageMetrics = useMemo(() => {
    const stageMap = new Map<string, StageStatus>();

    pipelines.forEach(pipeline => {
      if (!pipeline.stages || !Array.isArray(pipeline.stages)) return;

      pipeline.stages.forEach(stage => {
        if (!stage || typeof stage !== 'object') return;
        
        const stageName = String(stage.name || 'unknown');
        const stageStatus = String(stage.status || 'unknown');

        if (!stageMap.has(stageName)) {
          stageMap.set(stageName, {
            name: stageName,
            status: stageStatus,
            count: 0
          });
        }

        const existing = stageMap.get(stageName)!;
        existing.count += 1;

        // Update status to worst case (error > pending > complete)
        if (stageStatus === 'error' || existing.status === 'error') {
          existing.status = 'error';
        } else if (stageStatus === 'pending' || existing.status === 'pending') {
          existing.status = 'pending';
        } else if (stageStatus === 'complete') {
          existing.status = 'complete';
        }
      });
    });

    return Array.from(stageMap.values());
  }, [pipelines]);

  if (stageMetrics.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-md p-8 text-center">
        <span className="material-symbols-rounded text-gray-400 text-4xl mb-2">info</span>
        <p className="text-gray-600">No pipeline stages available</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stageMetrics.map(stage => (
        <div
          key={stage.name}
          className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition-shadow"
        >
          <div className="flex items-start justify-between mb-4">
            <h3 className="text-3xl font-bold text-gray-900 capitalize">
              {String(stage.name || '').replace(/_/g, ' ')}
            </h3>
            <StageStatusBadges status={stage.status} />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-5xl font-bold text-gray-900">{stage.count}</span>
            <span className="text-lg text-gray-500">pipeline{stage.count !== 1 ? 's' : ''}</span>
          </div>
        </div>
      ))}
    </div>
  );
}