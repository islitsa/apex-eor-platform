import React, { useState } from 'react';
import { Pipeline } from '../types';
import FileNavigationTree from './FileNavigationTree';
import DataPreviewTable from './DataPreviewTable';

interface DatasetExpansionCardProps {
  pipeline: Pipeline;
  isExpanded: boolean;
  onToggle: () => void;
}

export default function DatasetExpansionCard({ 
  pipeline, 
  isExpanded, 
  onToggle 
}: DatasetExpansionCardProps) {
  const [selectedFile, setSelectedFile] = useState<string | null>(null);

  return (
    <div className="w-full max-w-[600px] mx-auto">
      <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
        {/* Card Header - Always Visible */}
        <button
          onClick={onToggle}
          className="w-full px-6 py-5 flex items-center justify-between hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center gap-4">
            <span className="material-symbols-rounded text-blue-600 text-3xl">science</span>
            <div className="text-left">
              <h3 className="text-2xl font-bold text-gray-900">
                {String(pipeline.display_name || pipeline.name || 'Unknown')}
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                {Number(pipeline.metrics?.file_count || 0).toLocaleString()} files • {' '}
                {Number(pipeline.metrics?.record_count || 0).toLocaleString()} records • {' '}
                {String(pipeline.metrics?.data_size || '0 B')}
              </p>
            </div>
          </div>
          
          <span className={`material-symbols-rounded text-gray-600 text-3xl transition-transform ${
            isExpanded ? 'rotate-180' : ''
          }`}>
            expand_more
          </span>
        </button>

        {/* Expanded Content */}
        {isExpanded && (
          <div className="border-t border-gray-200">
            {/* File Navigation Tree */}
            <div className="p-6" style={{ marginTop: '40px' }}>
              <FileNavigationTree 
                pipeline={pipeline}
                selectedFile={selectedFile}
                onSelectFile={setSelectedFile}
              />
            </div>

            {/* Data Preview Table */}
            {selectedFile && (
              <div className="px-6 pb-6" style={{ marginTop: '40px' }}>
                <DataPreviewTable 
                  pipelineId={pipeline.id}
                  filePath={selectedFile}
                />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}