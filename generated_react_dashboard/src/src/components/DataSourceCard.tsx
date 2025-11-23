import React, { useState } from 'react';
import { Pipeline } from '../types.ts';
import FileTree from './FileTree.tsx';
import DataPreviewPanel from './DataPreviewPanel.tsx';

interface DataSourceCardProps {
  pipeline: Pipeline;
  isExpanded: boolean;
  onToggle: () => void;
}

export default function DataSourceCard({ pipeline, isExpanded, onToggle }: DataSourceCardProps) {
  const [selectedFile, setSelectedFile] = useState<string | null>(null);

  const stageEntries = Object.entries(pipeline.stages);
  const completedStages = stageEntries.filter(([_, stage]) => stage.status === 'complete').length;

  return (
    <div 
      className={`bg-white rounded-lg shadow-md transition-all duration-300 ${
        isExpanded ? 'min-h-[400px]' : 'h-[120px]'
      }`}
    >
      <div className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-3">
              <span className="material-symbols-rounded text-primary text-3xl">science</span>
              <h3 className="text-2xl font-bold text-on-surface">{pipeline.name}</h3>
            </div>
            
            <div className="flex items-center gap-6 text-sm text-on-surface-variant">
              <div className="flex items-center gap-2">
                <span className="material-symbols-rounded text-base">folder</span>
                <span className="font-medium">{pipeline.file_count} files</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="material-symbols-rounded text-base">storage</span>
                <span className="font-medium">{pipeline.data_size}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="material-symbols-rounded text-base">
                  {pipeline.status === 'processed' ? 'check_circle' : 'pending'}
                </span>
                <span className="font-medium capitalize">{pipeline.status}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="material-symbols-rounded text-base">timeline</span>
                <span className="font-medium">{completedStages}/{stageEntries.length} stages complete</span>
              </div>
            </div>
          </div>

          <button
            onClick={onToggle}
            className="w-10 h-10 rounded-full bg-primary text-on-primary flex items-center justify-center shadow-md hover:shadow-lg transition-shadow"
            aria-label={isExpanded ? 'Collapse' : 'Expand'}
          >
            <span className={`material-symbols-rounded transition-transform duration-300 ${
              isExpanded ? 'rotate-180' : ''
            }`}>
              expand_more
            </span>
          </button>
        </div>

        {isExpanded && (
          <div className="mt-6 pt-6 border-t border-outline-variant">
            <div className="flex gap-6">
              <div className="flex-1">
                <FileTree 
                  pipeline={pipeline}
                  onFileSelect={setSelectedFile}
                  selectedFile={selectedFile}
                />
              </div>
              
              {selectedFile && (
                <div className="w-96">
                  <DataPreviewPanel 
                    pipelineId={pipeline.id}
                    filePath={selectedFile}
                  />
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}