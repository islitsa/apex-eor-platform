import React, { useState } from 'react';
import { Pipeline } from '../types';
import FileBrowserPanel from './FileBrowserPanel.tsx';
import HealthStatusIndicators from './HealthStatusIndicators.tsx';

interface Props {
  pipelines: Pipeline[];
  selectedPipeline: Pipeline | undefined;
  onSelectPipeline: (id: string) => void;
}

export default function DatasetOverviewCard({ pipelines, selectedPipeline, onSelectPipeline }: Props) {
  const [expandedPipeline, setExpandedPipeline] = useState<string | null>(null);

  const handleToggleExpand = (pipelineId: string) => {
    setExpandedPipeline(expandedPipeline === pipelineId ? null : pipelineId);
  };

  return (
    <div className="bg-white rounded-lg border-2 border-gray-200 shadow-sm">
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center gap-3 mb-2">
          <span className="material-symbols-rounded text-blue-600">database</span>
          <h2 className="text-lg font-bold text-gray-900">Chemical Data Sources</h2>
        </div>
        <p className="text-sm text-gray-600">{pipelines.length} active pipeline{pipelines.length !== 1 ? 's' : ''}</p>
      </div>

      <div className="divide-y divide-gray-200">
        {pipelines.map(pipeline => (
          <div key={pipeline.id} className="p-4">
            <div
              className="flex items-start justify-between cursor-pointer hover:bg-gray-50 -m-2 p-2 rounded transition-colors"
              onClick={() => {
                onSelectPipeline(pipeline.id);
                handleToggleExpand(pipeline.id);
              }}
            >
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <h3 className="font-bold text-gray-900">{pipeline.display_name || pipeline.name}</h3>
                  <HealthStatusIndicators status={pipeline.status} />
                </div>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <span className="text-gray-600">Records:</span>
                    <span className="ml-2 font-semibold text-2xl text-gray-900 block">
                      {(pipeline.metrics?.record_count || 0).toLocaleString()}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-600">Files:</span>
                    <span className="ml-2 font-semibold text-2xl text-gray-900 block">
                      {(pipeline.metrics?.file_count || 0).toLocaleString()}
                    </span>
                  </div>
                </div>
                <div className="mt-2 text-sm text-gray-600">
                  <span className="material-symbols-rounded text-base align-middle mr-1">storage</span>
                  {pipeline.metrics?.data_size || '0 MB'}
                </div>
              </div>
              <span className="material-symbols-rounded text-gray-400">
                {expandedPipeline === pipeline.id ? 'expand_less' : 'expand_more'}
              </span>
            </div>

            {expandedPipeline === pipeline.id && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <FileBrowserPanel pipeline={pipeline} />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}