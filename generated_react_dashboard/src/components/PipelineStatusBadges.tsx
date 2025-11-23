import React, { useState } from 'react';
import { Pipeline } from '../types';

interface Props {
  pipelines: Pipeline[];
}

export default function PipelineStatusBadges({ pipelines }: Props) {
  const [hoveredStage, setHoveredStage] = useState<string | null>(null);

  const getStageStatus = (pipeline: Pipeline, stageName: string) => {
    const stage = pipeline.stages?.find(s => 
      String(s.name || '').toLowerCase() === stageName.toLowerCase()
    );
    return stage?.status || 'unknown';
  };

  const getStatusColor = (status: string) => {
    const statusStr = String(status || 'unknown').toLowerCase();
    if (statusStr === 'complete' || statusStr === 'healthy') return 'bg-green-500';
    if (statusStr === 'processing' || statusStr === 'in_progress') return 'bg-amber-500';
    if (statusStr === 'error' || statusStr === 'failed') return 'bg-red-500';
    return 'bg-gray-400';
  };

  const getStatusIcon = (status: string) => {
    const statusStr = String(status || 'unknown').toLowerCase();
    if (statusStr === 'complete' || statusStr === 'healthy') return 'check_circle';
    if (statusStr === 'processing' || statusStr === 'in_progress') return 'sync';
    if (statusStr === 'error' || statusStr === 'failed') return 'error';
    return 'help';
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
      <h3 className="text-lg font-bold text-gray-900 mb-4">Pipeline Health by Stage</h3>
      
      <div className="space-y-4">
        {pipelines.map(pipeline => {
          const stageNames = pipeline.stages
            ?.filter(s => s.name && typeof s.name === 'string')
            .map(s => s.name) || [];

          return (
            <div key={pipeline.id} className="border-b border-gray-100 pb-4 last:border-b-0 last:pb-0">
              <div className="flex items-center gap-3 mb-3">
                <span className="material-symbols-rounded text-blue-600">science</span>
                <h4 className="font-bold text-gray-900">{pipeline.display_name || pipeline.name}</h4>
              </div>
              
              <div className="flex items-center gap-3 ml-9">
                {stageNames.map((stageName, idx) => {
                  const status = getStageStatus(pipeline, stageName);
                  const stageKey = `${pipeline.id}-${stageName}`;
                  
                  return (
                    <div key={idx} className="relative">
                      <div
                        className={`w-8 h-8 rounded-full ${getStatusColor(status)} flex items-center justify-center cursor-pointer transition-transform hover:scale-110`}
                        onMouseEnter={() => setHoveredStage(stageKey)}
                        onMouseLeave={() => setHoveredStage(null)}
                      >
                        <span className="material-symbols-rounded text-white text-sm">
                          {getStatusIcon(status)}
                        </span>
                      </div>
                      
                      {hoveredStage === stageKey && (
                        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded shadow-lg whitespace-nowrap z-10">
                          <div className="font-semibold">{String(stageName || '').replace(/_/g, ' ')}</div>
                          <div className="text-gray-300">{String(status || 'unknown').replace(/_/g, ' ')}</div>
                          <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
                            <div className="border-4 border-transparent border-t-gray-900"></div>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}