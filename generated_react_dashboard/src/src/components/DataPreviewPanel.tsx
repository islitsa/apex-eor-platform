import React from 'react';
import { useDataSource } from '../dataHooks.tsx';

interface DataPreviewPanelProps {
  pipelineId: string;
  filePath: string;
}

export default function DataPreviewPanel({ pipelineId, filePath }: DataPreviewPanelProps) {
  const sourceId = pipelineId.replace('fracfocus_', '');
  const { data, total, loading, error } = useDataSource(sourceId, { limit: 5 });

  return (
    <div className="border border-outline-variant rounded-lg p-4 h-full">
      <div className="flex items-center gap-2 mb-4">
        <span className="material-symbols-rounded text-primary">preview</span>
        <h4 className="text-base font-bold text-on-surface">Data Preview</h4>
      </div>

      <div className="text-xs text-on-surface-variant mb-3 break-all">
        {filePath}
      </div>

      {loading && (
        <div className="text-sm text-on-surface-variant">Loading preview...</div>
      )}

      {error && (
        <div className="text-sm text-red-600">Error: {error}</div>
      )}

      {!loading && !error && data.length === 0 && (
        <div className="text-sm text-on-surface-variant">No data available for preview</div>
      )}

      {!loading && !error && data.length > 0 && (
        <div>
          <div className="text-xs text-on-surface-variant mb-2">
            Showing 5 of {total.toLocaleString()} records
          </div>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {data.map((row, idx) => (
              <div key={idx} className="bg-surface-container rounded p-3 text-xs">
                <div className="font-mono space-y-1">
                  {Object.entries(row).slice(0, 6).map(([key, value]) => (
                    <div key={key} className="flex gap-2">
                      <span className="font-bold text-on-surface-variant min-w-24">
                        {key}:
                      </span>
                      <span className="text-on-surface break-all">
                        {String(value)}
                      </span>
                    </div>
                  ))}
                  {Object.keys(row).length > 6 && (
                    <div className="text-on-surface-variant italic">
                      ... {Object.keys(row).length - 6} more fields
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}