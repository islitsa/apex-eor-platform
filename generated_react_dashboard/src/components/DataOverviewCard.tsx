import React from 'react';
import type { PipelineSummary, Pipeline } from '../types.ts';

interface DataOverviewCardProps {
  summary: PipelineSummary;
  chemicalPipeline?: Pipeline;
}

export function DataOverviewCard({ summary, chemicalPipeline }: DataOverviewCardProps) {
  const parsedFiles = chemicalPipeline?.metadata?.parsed_files || 0;
  const extractionDate = chemicalPipeline?.metadata?.extraction_date 
    ? new Date(chemicalPipeline.metadata.extraction_date).toLocaleDateString()
    : 'N/A';

  return (
    <div className="bg-white rounded-2xl shadow-lg h-full p-6 flex flex-col">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <span className="material-symbols-rounded text-blue-600 text-[32px]">analytics</span>
        <h2 className="text-3xl font-bold text-gray-900">Chemical Data Overview</h2>
      </div>

      {/* Main Stats Grid */}
      <div className="flex-1 grid grid-cols-3 gap-6 mb-6">
        {/* Total Size */}
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 flex flex-col justify-between">
          <div>
            <span className="material-symbols-rounded text-blue-600 text-[40px] mb-2 block">storage</span>
            <p className="text-sm font-medium text-blue-800 mb-1">Total Data Size</p>
          </div>
          <p className="text-4xl font-bold text-blue-900">{summary.total_size}</p>
        </div>

        {/* Pipelines */}
        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 flex flex-col justify-between">
          <div>
            <span className="material-symbols-rounded text-green-600 text-[40px] mb-2 block">account_tree</span>
            <p className="text-sm font-medium text-green-800 mb-1">Active Pipelines</p>
          </div>
          <p className="text-4xl font-bold text-green-900">{summary.total_pipelines}</p>
        </div>

        {/* Parsed Files */}
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 flex flex-col justify-between">
          <div>
            <span className="material-symbols-rounded text-purple-600 text-[40px] mb-2 block">description</span>
            <p className="text-sm font-medium text-purple-800 mb-1">Parsed Files</p>
          </div>
          <p className="text-4xl font-bold text-purple-900">{parsedFiles}</p>
        </div>
      </div>

      {/* Pipeline Details */}
      <div className="bg-gray-50 rounded-xl p-6 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <span className="material-symbols-rounded text-gray-700 text-[20px]">database</span>
          <h3 className="text-lg font-bold text-gray-900">FracFocus Chemical Data</h3>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600 mb-1">Status</p>
            <div className="flex items-center gap-2">
              <span className="material-symbols-rounded text-green-600 text-[20px]">check_circle</span>
              <p className="text-base font-semibold text-gray-900 capitalize">
                {chemicalPipeline?.status || 'Unknown'}
              </p>
            </div>
          </div>
          <div>
            <p className="text-sm text-gray-600 mb-1">Last Extraction</p>
            <p className="text-base font-semibold text-gray-900">{extractionDate}</p>
          </div>
        </div>
      </div>

      {/* CTA Button */}
      <button className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-4 px-6 rounded-lg transition-colors flex items-center justify-center gap-2 shadow-md hover:shadow-lg">
        <span className="text-lg">Explore Data</span>
        <span className="material-symbols-rounded text-[20px]">arrow_forward</span>
      </button>
    </div>
  );
}