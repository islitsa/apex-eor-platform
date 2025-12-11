import React from 'react';
import { Pipeline } from '../types.ts';

interface PipelineHealthBannerProps {
  pipelines: Pipeline[];
  summary: {
    total_pipelines: number;
    total_records: number;
    total_size: number;
  };
}

function PipelineHealthBanner({ pipelines, summary }: PipelineHealthBannerProps) {
  const completedPipelines = pipelines.filter(p => p.status === 'processed').length;
  const processingPipelines = pipelines.filter(p => p.status === 'processing').length;
  const failedPipelines = pipelines.filter(p => p.status === 'failed').length;

  const formatNumber = (num: number): string => {
    return Number(num || 0).toLocaleString();
  };

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg">
      <div className="max-w-[1200px] mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
              <span className="material-symbols-rounded text-green-600">check_circle</span>
              <div>
                <div className="text-xs text-gray-600">Completed</div>
                <div className="text-lg font-semibold text-gray-900">{completedPipelines}</div>
              </div>
            </div>

            {processingPipelines > 0 && (
              <div className="flex items-center gap-2">
                <span className="material-symbols-rounded text-blue-600">pending</span>
                <div>
                  <div className="text-xs text-gray-600">Processing</div>
                  <div className="text-lg font-semibold text-gray-900">{processingPipelines}</div>
                </div>
              </div>
            )}

            {failedPipelines > 0 && (
              <div className="flex items-center gap-2">
                <span className="material-symbols-rounded text-red-600">error</span>
                <div>
                  <div className="text-xs text-gray-600">Failed</div>
                  <div className="text-lg font-semibold text-gray-900">{failedPipelines}</div>
                </div>
              </div>
            )}
          </div>

          <div className="flex items-center gap-6">
            <div>
              <div className="text-xs text-gray-600">Total Pipelines</div>
              <div className="text-lg font-semibold text-gray-900">{summary.total_pipelines}</div>
            </div>
            <div>
              <div className="text-xs text-gray-600">Total Records</div>
              <div className="text-lg font-semibold text-gray-900">{formatNumber(summary.metrics.record_count)}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PipelineHealthBanner;