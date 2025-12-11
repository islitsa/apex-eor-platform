import React from 'react';
import type { Pipeline } from '../types';

interface Props {
  pipeline: Pipeline;
}

export default function DatasetMetricsHeader({ pipeline }: Props) {
  const fileCount = pipeline.metrics?.file_count || 0;
  const recordCount = pipeline.metrics?.record_count || 0;
  const dataSize = pipeline.metrics?.data_size || '0 B';

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">{pipeline.display_name}</h2>

      <div className="grid grid-cols-3 gap-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="material-symbols-rounded text-blue-600">folder</span>
            <span className="text-sm font-semibold text-gray-600">Files</span>
          </div>
          <div className="text-3xl font-bold text-gray-900">{fileCount.toLocaleString()}</div>
        </div>

        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="material-symbols-rounded text-green-600">database</span>
            <span className="text-sm font-semibold text-gray-600">Records</span>
          </div>
          <div className="text-3xl font-bold text-gray-900">{recordCount.toLocaleString()}</div>
        </div>

        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="material-symbols-rounded text-purple-600">storage</span>
            <span className="text-sm font-semibold text-gray-600">Size</span>
          </div>
          <div className="text-3xl font-bold text-gray-900">{dataSize}</div>
        </div>
      </div>

      {/* Pipeline Stages */}
      {pipeline.stages && pipeline.stages.length > 0 && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <div className="text-sm font-semibold text-gray-700 mb-3">Pipeline Stages</div>
          <div className="flex gap-4">
            {pipeline.stages.map((stage, idx) => (
              <div key={idx} className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${
                  String(stage.status || '').toLowerCase() === 'complete' ? 'bg-green-500' :
                  String(stage.status || '').toLowerCase() === 'processing' ? 'bg-blue-500' :
                  'bg-gray-400'
                }`}></div>
                <span className="text-sm text-gray-700 capitalize">
                  {String(stage.name || '').replace(/_/g, ' ')}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}