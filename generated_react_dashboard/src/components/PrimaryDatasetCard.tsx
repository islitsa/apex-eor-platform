import React, { useState } from 'react';
import type { Pipeline } from '../types';
import DataVolumeBadge from './DataVolumeBadge';
import ProductionFilesTree from './ProductionFilesTree';
import FileSizeIndicator from './FileSizeIndicator';

interface PrimaryDatasetCardProps {
  pipeline: Pipeline;
}

export default function PrimaryDatasetCard({ pipeline }: PrimaryDatasetCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const formatNumber = (num: number | undefined): string => {
    return Number(num || 0).toLocaleString();
  };

  const formatDate = (dateStr: string | undefined): string => {
    if (!dateStr) return 'Unknown';
    try {
      return new Date(dateStr).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch {
      return String(dateStr);
    }
  };

  const getStatusColor = (status: string | undefined): string => {
    const statusStr = String(status || 'unknown').toLowerCase();
    if (statusStr.includes('complete') || statusStr.includes('success')) return 'text-green-600';
    if (statusStr.includes('running') || statusStr.includes('processing')) return 'text-blue-600';
    if (statusStr.includes('error') || statusStr.includes('failed')) return 'text-red-600';
    return 'text-gray-600';
  };

  const parseSizeToBytes = (sizeStr: string | undefined): number => {
    if (!sizeStr) return 0;
    const match = sizeStr.match(/^([\d.]+)\s*(GB|MB|KB|B)?$/i);
    if (!match) return 0;
    
    const value = parseFloat(match[1]);
    const unit = (match[2] || 'B').toUpperCase();
    
    switch (unit) {
      case 'GB': return value * 1024 * 1024 * 1024;
      case 'MB': return value * 1024 * 1024;
      case 'KB': return value * 1024;
      default: return value;
    }
  };

  const totalSizeBytes = parseSizeToBytes(pipeline.metrics?.data_size);
  const maxSize = 100 * 1024 * 1024 * 1024; // 100 GB reference
  const utilizationPercent = Math.min((totalSizeBytes / maxSize) * 100, 100);

  return (
    <div
      className={`bg-white rounded-xl shadow-md p-6 transition-all duration-200 ease-in-out cursor-pointer hover:shadow-lg relative ${
        isExpanded ? 'w-[600px]' : 'w-[400px]'
      }`}
      onClick={() => setIsExpanded(!isExpanded)}
    >
      {/* Data Volume Badge */}
      <div className="absolute top-4 right-4">
        <DataVolumeBadge recordCount={Number(pipeline.metrics?.record_count || 0)} />
      </div>

      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <span className="material-symbols-rounded text-orange-600 text-3xl">oil_barrel</span>
        <div>
          <h3 className="text-2xl font-bold text-gray-900">{String(pipeline.display_name || pipeline.name || pipeline.id)}</h3>
          <p className="text-base text-gray-600 mt-1">
            Railroad Commission of Texas
          </p>
        </div>
      </div>

      {/* Metadata */}
      <div className="space-y-2 mb-4">
        <div className="flex items-center gap-2 text-gray-700">
          <span className="material-symbols-rounded text-sm">folder</span>
          <span className="text-base">{formatNumber(pipeline.metrics?.file_count)} files</span>
        </div>
        <div className="flex items-center gap-2 text-gray-700">
          <span className="material-symbols-rounded text-sm">storage</span>
          <span className="text-base">Size: {pipeline.metrics?.data_size || '0 B'}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="material-symbols-rounded text-sm">info</span>
          <span className={`text-base font-medium ${getStatusColor(pipeline.status)}`}>
            {String(pipeline.status || 'unknown').replace(/_/g, ' ').toUpperCase()}
          </span>
        </div>
      </div>

      {/* File Size Indicator */}
      <div className="mb-4">
        <FileSizeIndicator sizeBytes={totalSizeBytes} utilizationPercent={utilizationPercent} />
      </div>

      {/* Expand/Collapse Indicator */}
      <div className="flex items-center justify-center text-gray-400 mt-4">
        <span
          className={`material-symbols-rounded transition-transform duration-200 ${
            isExpanded ? 'rotate-180' : ''
          }`}
        >
          expand_more
        </span>
      </div>

      {/* Production Files Tree (Expanded State) */}
      {isExpanded && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <ProductionFilesTree pipeline={pipeline} />
        </div>
      )}
    </div>
  );
}