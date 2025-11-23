import React, { useMemo } from 'react';
import { Pipeline } from '../types.ts';

interface StageOverviewProps {
  pipelines: Pipeline[];
}

export function StageOverview({ pipelines }: StageOverviewProps) {
  const stageStats = useMemo(() => {
    const stats: Record<string, { total: number; processed: number; error: number }> = {};

    pipelines.forEach(pipeline => {
      if (!pipeline.stages || !Array.isArray(pipeline.stages)) return;

      pipeline.stages.forEach(stage => {
        if (!stage || typeof stage !== 'object') return;
        
        const stageName = String(stage.name || 'unknown');
        const stageStatus = String(stage.status || 'unknown').toLowerCase();

        if (!stats[stageName]) {
          stats[stageName] = { total: 0, processed: 0, error: 0 };
        }

        stats[stageName].total += 1;
        if (stageStatus === 'processed' || stageStatus === 'complete') {
          stats[stageName].processed += 1;
        } else if (stageStatus === 'error' || stageStatus === 'failed') {
          stats[stageName].error += 1;
        }
      });
    });

    return Object.entries(stats).map(([name, data]) => ({
      name,
      ...data,
      percentage: data.total > 0 ? Math.round((data.processed / data.total) * 100) : 0
    }));
  }, [pipelines]);

  if (stageStats.length === 0) return null;

  return (
    <div className="mt-8 bg-white rounded-2xl shadow-md p-6 border border-slate-200">
      <h2 className="text-2xl font-bold text-slate-900 mb-6 flex items-center gap-2">
        <span className="material-symbols-rounded text-slate-700">account_tree</span>
        Pipeline Stages Overview
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {stageStats.map((stage, index) => (
          <div key={index} className="bg-slate-50 rounded-xl p-4 border border-slate-200">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-slate-900 capitalize">
                {stage.name.replace(/_/g, ' ')}
              </h3>
              <span className="text-sm font-medium text-slate-600">
                {stage.processed}/{stage.total}
              </span>
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-slate-200 rounded-full h-2.5 mb-3">
              <div
                className={`h-2.5 rounded-full transition-all duration-500 ${
                  stage.error > 0 ? 'bg-red-500' : 'bg-green-500'
                }`}
                style={{ width: `${stage.percentage}%` }}
              ></div>
            </div>

            {/* Stats */}
            <div className="flex items-center gap-4 text-sm">
              <div className="flex items-center gap-1">
                <span className="material-symbols-rounded text-green-600 text-sm">check_circle</span>
                <span className="text-slate-700">{stage.processed}</span>
              </div>
              {stage.error > 0 && (
                <div className="flex items-center gap-1">
                  <span className="material-symbols-rounded text-red-600 text-sm">error</span>
                  <span className="text-slate-700">{stage.error}</span>
                </div>
              )}
              <div className="ml-auto text-slate-600 font-medium">
                {stage.percentage}%
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}