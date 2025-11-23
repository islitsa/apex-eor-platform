import React from 'react';
import type { Pipeline } from '../types';

interface PipelineHealthStripProps {
  pipelines: Pipeline[];
}

export default function PipelineHealthStrip({ pipelines }: PipelineHealthStripProps) {
  const stageNames = ['downloads', 'extracted', 'parsed'];
  
  const getStageHealth = (stageName: string) => {
    let completed = 0;
    let total = 0;

    pipelines.forEach(pipeline => {
      const stage = pipeline.stages?.find(s => 
        String(s.name || '').toLowerCase() === stageName.toLowerCase()
      );
      if (stage) {
        total++;
        if (String(stage.status || '').toLowerCase() === 'complete') {
          completed++;
        }
      }
    });

    return { completed, total, percentage: total > 0 ? (completed / total) * 100 : 0 };
  };

  return (
    <div className="bg-gradient-to-r from-gray-800 to-gray-900 rounded-2xl shadow-lg p-8 h-full">
      <h2 className="text-white text-xl font-bold mb-6">Pipeline Health Overview</h2>
      
      <div className="flex items-center justify-between gap-8">
        {stageNames.map((stageName, index) => {
          const health = getStageHealth(stageName);
          const isComplete = health.percentage === 100;
          
          return (
            <React.Fragment key={stageName}>
              <div className="flex flex-col items-center gap-3">
                <div className={`w-16 h-16 rounded-full flex items-center justify-center transition-all ${
                  isComplete 
                    ? 'bg-green-500 animate-pulse' 
                    : 'bg-gray-600'
                }`}>
                  <span className="material-symbols-rounded text-white text-3xl">
                    {isComplete ? 'check_circle' : 'pending'}
                  </span>
                </div>
                <div className="text-center">
                  <p className="text-white font-semibold text-lg capitalize">
                    {String(stageName).replace(/_/g, ' ')}
                  </p>
                  <p className="text-gray-300 text-sm">
                    {health.completed}/{health.total} complete
                  </p>
                </div>
              </div>
              
              {index < stageNames.length - 1 && (
                <div className="flex-1 h-1 bg-gray-600 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-green-500 transition-all duration-500"
                    style={{ width: `${health.percentage}%` }}
                  />
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}