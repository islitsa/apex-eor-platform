import React from 'react';
import { Pipeline } from '../types';
import PipelineStatusBadges from './PipelineStatusBadges.tsx';

interface Props {
  pipelines: Pipeline[];
  totalFiles: number;
  totalRecords: number;
  totalSize: number;
}

export default function PipelineHealthHeader({ pipelines, totalFiles, totalRecords, totalSize }: Props) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
      {/* Total Pipelines */}
      <div className="bg-blue-50 rounded-lg p-6 border border-blue-100">
        <div className="flex items-center justify-between mb-2">
          <span className="material-symbols-rounded text-blue-600">storage</span>
          <span className="text-sm font-medium text-blue-700">Pipelines</span>
        </div>
        <div className="text-3xl font-bold text-blue-900">{pipelines.length}</div>
        <div className="text-sm text-blue-600 mt-1">Active Sources</div>
      </div>

      {/* Total Files */}
      <div className="bg-green-50 rounded-lg p-6 border border-green-100">
        <div className="flex items-center justify-between mb-2">
          <span className="material-symbols-rounded text-green-600">folder</span>
          <span className="text-sm font-medium text-green-700">Files</span>
        </div>
        <div className="text-3xl font-bold text-green-900">{totalFiles.toLocaleString()}</div>
        <div className="text-sm text-green-600 mt-1">Total Files</div>
      </div>

      {/* Total Records */}
      <div className="bg-purple-50 rounded-lg p-6 border border-purple-100">
        <div className="flex items-center justify-between mb-2">
          <span className="material-symbols-rounded text-purple-600">description</span>
          <span className="text-sm font-medium text-purple-700">Records</span>
        </div>
        <div className="text-3xl font-bold text-purple-900">{totalRecords.toLocaleString()}</div>
        <div className="text-sm text-purple-600 mt-1">Total Records</div>
      </div>

      {/* Total Size */}
      <div className="bg-orange-50 rounded-lg p-6 border border-orange-100">
        <div className="flex items-center justify-between mb-2">
          <span className="material-symbols-rounded text-orange-600">hard_drive</span>
          <span className="text-sm font-medium text-orange-700">Storage</span>
        </div>
        <div className="text-3xl font-bold text-orange-900">{totalSize.toFixed(2)}</div>
        <div className="text-sm text-orange-600 mt-1">GB Total</div>
      </div>

      {/* Pipeline Health Badges */}
      <div className="md:col-span-4">
        <PipelineStatusBadges pipelines={pipelines} />
      </div>
    </div>
  );
}