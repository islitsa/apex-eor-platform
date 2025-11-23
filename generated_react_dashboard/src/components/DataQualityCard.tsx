import React from 'react';
import type { Pipeline } from '../types.ts';

interface DataQualityCardProps {
  pipeline?: Pipeline;
}

export function DataQualityCard({ pipeline }: DataQualityCardProps) {
  if (!pipeline) {
    return (
      <div className="bg-white rounded-2xl shadow-md p-6">
        <div className="flex items-center gap-3 mb-6">
          <span className="material-symbols-rounded text-gray-400 text-[24px]">verified</span>
          <h2 className="text-xl font-bold text-gray-900">Data Quality</h2>
        </div>
        <p className="text-gray-500">No quality metrics available</p>
      </div>
    );
  }

  const stages = pipeline.stages || {};
  const validationStage = stages.validation;
  const parsingStage = stages.parsing;
  
  // Calculate quality metrics based on stage completion
  const qualityMetrics = [
    {
      label: 'Parsing Success',
      value: parsingStage?.status === 'complete' ? 100 : 0,
      icon: 'code',
      color: 'blue'
    },
    {
      label: 'Validation',
      value: validationStage?.status === 'complete' ? 100 : validationStage?.status === 'not_started' ? 0 : 50,
      icon: 'verified',
      color: 'green'
    },
    {
      label: 'Completeness',
      value: pipeline.metadata?.parsed_files ? 100 : 0,
      icon: 'check_circle',
      color: 'purple'
    }
  ];

  const overallQuality = Math.round(
    qualityMetrics.reduce((sum, m) => sum + m.value, 0) / qualityMetrics.length
  );

  const getQualityColor = (value: number) => {
    if (value >= 80) return 'text-green-600';
    if (value >= 50) return 'text-amber-600';
    return 'text-red-600';
  };

  const getBarColor = (color: string) => {
    const colors: Record<string, string> = {
      blue: 'bg-blue-600',
      green: 'bg-green-600',
      purple: 'bg-purple-600'
    };
    return colors[color] || 'bg-gray-600';
  };

  return (
    <div className="bg-white rounded-2xl shadow-md p-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <span className="material-symbols-rounded text-green-600 text-[24px]">verified</span>
        <h2 className="text-xl font-bold text-gray-900">Data Quality</h2>
      </div>

      {/* Overall Score */}
      <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-6 mb-6">
        <p className="text-sm font-medium text-gray-600 mb-2">Overall Quality Score</p>
        <div className="flex items-end gap-3">
          <p className={`text-5xl font-bold ${getQualityColor(overallQuality)}`}>
            {overallQuality}
          </p>
          <p className="text-2xl font-semibold text-gray-400 mb-1">/ 100</p>
        </div>
      </div>

      {/* Quality Metrics */}
      <div className="space-y-4">
        {qualityMetrics.map(metric => (
          <div key={metric.label}>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className={`material-symbols-rounded text-${metric.color}-600 text-[18px]`}>
                  {metric.icon}
                </span>
                <span className="text-sm font-medium text-gray-700">{metric.label}</span>
              </div>
              <span className={`text-sm font-bold ${getQualityColor(metric.value)}`}>
                {metric.value}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-1">
              <div 
                className={`${getBarColor(metric.color)} h-1 rounded-full transition-all duration-500`}
                style={{ width: `${metric.value}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Notes */}
      {parsingStage?.note && (
        <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <div className="flex gap-2">
            <span className="material-symbols-rounded text-blue-600 text-[18px]">info</span>
            <p className="text-xs text-blue-800">{parsingStage.note}</p>
          </div>
        </div>
      )}
    </div>
  );
}