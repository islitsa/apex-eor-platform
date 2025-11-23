import React from 'react';
import StatusIndicators from './StatusIndicators.tsx';
import type { Pipeline } from '../types';

interface PipelineHealthDashboardProps {
  pipelines: Pipeline[];
}

export default function PipelineHealthDashboard({ pipelines }: PipelineHealthDashboardProps) {
  // Aggregate stages across all pipelines
  const stageHealth = React.useMemo(() => {
    const stageMap = new Map<string, { total: number; complete: number; failed: number; processing: number }>();

    pipelines.forEach(pipeline => {
      pipeline.stages?.forEach(stage => {
        const stageName = String(stage.name || '');
        if (!stageMap.has(stageName)) {
          stageMap.set(stageName, { total: 0, complete: 0, failed: 0, processing: 0 });
        }
        const stats = stageMap.get(stageName)!;
        stats.total++;

        const status = String(stage.status || 'unknown').toLowerCase();
        if (status === 'complete' || status === 'completed') {
          stats.complete++;
        } else if (status === 'failed' || status === 'error') {
          stats.failed++;
        } else {
          stats.processing++;
        }
      });
    });

    return Array.from(stageMap.entries()).map(([name, stats]) => ({
      name,
      ...stats,
      completionRate: stats.total > 0 ? (stats.complete / stats.total) * 100 : 0
    }));
  }, [pipelines]);

  return (
    <div className="bg-white rounded-lg shadow-md p-6 h-full">
      <div className="flex items-center gap-3 mb-6">
        <span className="material-symbols-rounded text-blue-600">download</span>
        <h2 className="text-xl font-bold text-gray-900">Data Pipeline Health</h2>
      </div>

      <div className="flex items-center justify-between gap-8 h-[120px]">
        {stageHealth.length === 0 ? (
          <div className="text-gray-500 text-center w-full">No pipeline stages available</div>
        ) : (
          stageHealth.map((stage, index) => (
            <React.Fragment key={stage.name}>
              <div className="flex flex-col items-center gap-3 flex-1">
                {/* Stage Circle */}
                <div className="relative">
                  <div className={`w-20 h-20 rounded-full flex items-center justify-center ${
                    stage.completionRate === 100
                      ? 'bg-green-100 border-4 border-green-500'
                      : stage.failed > 0
                      ? 'bg-red-100 border-4 border-red-500'
                      : 'bg-yellow-100 border-4 border-yellow-500'
                  }`}>
                    <StatusIndicators
                      status={
                        stage.completionRate === 100
                          ? 'complete'
                          : stage.failed > 0
                          ? 'failed'
                          : 'processing'
                      }
                      size="large"
                    />
                  </div>
                  <div className="absolute -bottom-1 -right-1 bg-white rounded-full px-2 py-0.5 text-xs font-bold border border-gray-200">
                    {Math.round(stage.completionRate)}%
                  </div>
                </div>

                {/* Stage Name */}
                <div className="text-center">
                  <div className="text-base font-bold text-gray-900 capitalize">
                    {String(stage.name || '').replace(/_/g, ' ')}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {stage.complete}/{stage.total} complete
                  </div>
                </div>
              </div>

              {/* Connector Line */}
              {index < stageHealth.length - 1 && (
                <div className="flex-shrink-0 w-16 h-1 bg-gradient-to-r from-gray-300 to-gray-300 relative top-[-20px]">
                  <div
                    className={`h-full transition-all ${
                      stage.completionRate === 100 ? 'bg-green-500' : 'bg-yellow-500'
                    }`}
                    style={{ width: `${stage.completionRate}%` }}
                  />
                </div>
              )}
            </React.Fragment>
          ))
        )}
      </div>
    </div>
  );
}