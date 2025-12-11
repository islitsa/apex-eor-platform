import React from 'react';
import { Pipeline } from '../types';
import HealthStatusBadges from './HealthStatusBadges';

interface PipelineHealthTrackerProps {
  pipelines: Pipeline[];
}

export default function PipelineHealthTracker({ pipelines }: PipelineHealthTrackerProps) {
  return (
    <div className="bg-white rounded-2xl shadow-lg p-8">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Pipeline Health Status</h2>
      
      <div className="space-y-6">
        {pipelines.map(pipeline => (
          <div key={pipeline.id} className="border-b border-gray-200 last:border-0 pb-6 last:pb-0">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-gray-800">
                {String(pipeline.display_name || pipeline.name || 'Unknown')}
              </h3>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                String(pipeline.status || '').toLowerCase() === 'processed' 
                  ? 'bg-green-100 text-green-800'
                  : String(pipeline.status || '').toLowerCase() === 'processing'
                  ? 'bg-amber-100 text-amber-800'
                  : 'bg-gray-100 text-gray-800'
              }`}>
                {String(pipeline.status || 'unknown').replace(/_/g, ' ').toUpperCase()}
              </span>
            </div>
            
            <HealthStatusBadges stages={pipeline.stages || []} />
          </div>
        ))}
      </div>
    </div>
  );
}