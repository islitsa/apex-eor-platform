import React, { useState } from 'react';
import DataVolumeIndicator from './DataVolumeIndicator';
import InlineFileExplorer from './InlineFileExplorer';
import { Pipeline } from '../types';

interface DatasetExpansionCardProps {
  pipeline: Pipeline;
}

export default function DatasetExpansionCard({ pipeline }: DatasetExpansionCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const formatNumber = (num: number): string => {
    return Number(num || 0).toLocaleString();
  };

  const parseDataSize = (dataSize: string): number => {
    if (!dataSize) return 0;
    const match = String(dataSize).match(/([\d.]+)\s*(GB|MB|KB|TB)?/i);
    if (!match) return 0;
    const value = parseFloat(match[1]);
    const unit = (match[2] || 'GB').toUpperCase();
    
    // Convert to GB
    switch (unit) {
      case 'TB': return value * 1024;
      case 'GB': return value;
      case 'MB': return value / 1024;
      case 'KB': return value / (1024 * 1024);
      default: return value;
    }
  };

  const getStatusColor = (status: string): string => {
    const statusStr = String(status || 'unknown').toLowerCase();
    if (statusStr === 'complete' || statusStr === 'active') return 'green';
    if (statusStr === 'processing' || statusStr === 'running') return 'blue';
    if (statusStr === 'error' || statusStr === 'failed') return 'red';
    return 'gray';
  };

  const cardHeight = isExpanded ? '480px' : '160px';
  const statusColor = getStatusColor(pipeline.status);
  
  // Parse data size from string format (e.g., "63.7 GB")
  const dataSizeInGB = parseDataSize(pipeline.metrics?.data_size || '0 GB');

  return (
    <div 
      className="bg-white rounded-2xl shadow-md hover:shadow-lg transition-all duration-200 overflow-hidden"
      style={{ width: '600px', height: cardHeight }}
    >
      {/* Card Header */}
      <div 
        className="p-6 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <span className="material-symbols-rounded text-blue-600 text-3xl">
              oil_barrel
            </span>
            <div>
              <h3 className="text-xl font-bold text-gray-900">
                {String(pipeline.display_name || pipeline.name || 'Unknown Dataset')}
              </h3>
              <p className="text-sm text-gray-500 mt-1">
                {formatNumber(Number(pipeline.metrics?.record_count || 0))} records • {' '}
                {pipeline.metrics?.data_size || '0 GB'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full bg-${statusColor}-500 animate-pulse`}></div>
              <span className="text-sm text-gray-600 capitalize">
                {String(pipeline.status || 'unknown')}
              </span>
            </div>
            <button className="p-1 hover:bg-gray-100 rounded-full transition-colors">
              <span className="material-symbols-rounded text-gray-600">
                {isExpanded ? 'expand_less' : 'expand_more'}
              </span>
            </button>
          </div>
        </div>

        {/* Data Volume Indicator */}
        <DataVolumeIndicator 
          pipelineName={String(pipeline.name || '')}
          sizeBytes={dataSizeInGB * 1024 * 1024 * 1024}
        />
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="px-6 pb-6">
          <InlineFileExplorer pipeline={pipeline} />
        </div>
      )}
    </div>
  );
}