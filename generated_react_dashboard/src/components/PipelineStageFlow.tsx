import React, { useState } from 'react';
import { Pipeline } from '../types';
import HealthStatusIndicators from './HealthStatusIndicators.tsx';

interface Props {
  pipeline: Pipeline | undefined;
}

export default function PipelineStageFlow({ pipeline }: Props) {
  const [hoveredStage, setHoveredStage] = useState<string | null>(null);

  if (!pipeline) {
    return (
      <div className="bg-white rounded-lg border-2 border-gray-200 shadow-sm p-4">
        <h2 className="text-lg font-bold text-gray-900 mb-4">Pipeline Health</h2>
        <div className="text-center py-8 text-gray-500">
          <span className="material-symbols-rounded text-4xl block mb-2">info</span>
          <p className="text-sm">Select a pipeline to view stages</p>
        </div>
      </div>
    );
  }

  const stages = pipeline.stages || [];

  return (
    <div className="bg-white rounded-lg border-2 border-gray-200 shadow-sm">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-bold text-gray-900">Pipeline Health</h2>
        <p className="text-sm text-gray-600 mt-1">{pipeline.display_name || pipeline.name}</p>
      </div>

      <div className="p-4">
        {stages.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <span className="material-symbols-rounded text-4xl block mb-2">info</span>
            <p className="text-sm">No pipeline stages available</p>
          </div>
        ) : (
          <div className="space-y-3">
            {stages.map((stage, index) => {
              const stageName = String(stage.name || 'unknown');
              const stageStatus = String(stage.status || 'unknown');
              const isHovered = hoveredStage === stageName;

              return (
                <div key={index}>
                  <div
                    className="relative bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors cursor-pointer"
                    onMouseEnter={() => setHoveredStage(stageName)}
                    onMouseLeave={() => setHoveredStage(null)}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-gray-900 capitalize">
                          {stageName.replace(/_/g, ' ')}
                        </span>
                        <HealthStatusIndicators status={stageStatus} />
                      </div>
                    </div>

                    {(stage.file_count !== undefined || stage.record_count !== undefined) && (
                      <div className="flex gap-4 text-sm text-gray-600 mt-2">
                        {stage.file_count !== undefined && (
                          <div>
                            <span className="material-symbols-rounded text-base align-middle mr-1">description</span>
                            {Number(stage.file_count || 0).toLocaleString()} files
                          </div>
                        )}
                        {stage.record_count !== undefined && (
                          <div>
                            <span className="material-symbols-rounded text-base align-middle mr-1">table_rows</span>
                            {Number(stage.record_count || 0).toLocaleString()} records
                          </div>
                        )}
                      </div>
                    )}

                    {isHovered && stage.last_updated && (
                      <div className="absolute top-full left-0 mt-2 bg-gray-900 text-white text-xs rounded px-3 py-2 shadow-lg z-10 whitespace-nowrap">
                        Last updated: {new Date(stage.last_updated).toLocaleString()}
                      </div>
                    )}
                  </div>

                  {index < stages.length - 1 && (
                    <div className="flex justify-center py-1">
                      <span className="material-symbols-rounded text-gray-400">arrow_downward</span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}