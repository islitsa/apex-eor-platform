import React from 'react';
import type { Pipeline } from '../types.ts';
import { extractStages } from '../utils.ts';
import StatusBadge from './StatusBadge.tsx';

interface PipelineVisualizationProps {
  pipeline: Pipeline | null;
}

export default function PipelineVisualization({ pipeline }: PipelineVisualizationProps) {
  if (!pipeline) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 h-full flex items-center justify-center">
        <div className="text-center text-gray-500">
          <span className="material-symbols-rounded text-6xl mb-4 block">analytics</span>
          <p className="text-lg">Select a dataset to view pipeline details</p>
        </div>
      </div>
    );
  }

  const stages = extractStages(pipeline);

  return (
    <div className="bg-white rounded-lg shadow-md p-6 h-full">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Pipeline Visualization</h2>

      {/* Pipeline Flow */}
      <div className="space-y-6">
        {stages.map((stage, idx) => (
          <div key={idx}>
            <div className="flex items-center gap-4">
              {/* Stage Number */}
              <div className="flex-shrink-0 w-10 h-10 rounded-full bg-teal-500 text-white flex items-center justify-center font-bold">
                {idx + 1}
              </div>

              {/* Stage Info */}
              <div className="flex-1 bg-gray-50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-lg font-bold text-gray-900">{stage.displayName}</h3>
                  <StatusBadge status={stage.status} />
                </div>
                <div className="text-sm text-gray-600">
                  Stage: <span className="font-medium">{stage.name}</span>
                </div>
              </div>
            </div>

            {/* Connector Arrow */}
            {idx < stages.length - 1 && (
              <div className="ml-5 my-2">
                <div className="w-0.5 h-8 bg-gray-300"></div>
                <span className="material-symbols-rounded text-gray-400 -ml-3">arrow_downward</span>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Additional Info */}
      <div className="mt-8 pt-6 border-t border-gray-200">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Pipeline Details</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-sm font-bold text-gray-700">Pipeline ID</div>
            <div className="text-sm text-gray-900 mt-1 font-mono">{pipeline.id}</div>
          </div>
          <div>
            <div className="text-sm font-bold text-gray-700">Status</div>
            <div className="mt-1">
              <StatusBadge status={pipeline.status} />
            </div>
          </div>
          <div>
            <div className="text-sm font-bold text-gray-700">Data Size</div>
            <div className="text-sm text-gray-900 mt-1">{pipeline.data_size}</div>
          </div>
          <div>
            <div className="text-sm font-bold text-gray-700">Files</div>
            <div className="text-sm text-gray-900 mt-1">{pipeline.files}</div>
          </div>
        </div>
      </div>
    </div>
  );
}