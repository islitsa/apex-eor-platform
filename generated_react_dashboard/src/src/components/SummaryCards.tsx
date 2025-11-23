import React from 'react';
import type { Pipeline } from '../types.ts';

interface SummaryCardsProps {
  pipelineId: string;
  pipelines: Pipeline[];
}

export default function SummaryCards({ pipelineId, pipelines }: SummaryCardsProps) {
  const pipeline = pipelines.find(p => p.id === pipelineId);

  if (!pipeline) return null;

  const getDateRange = () => {
    const dates: string[] = [];
    Object.values(pipeline.stages).forEach(stage => {
      if (stage.date) dates.push(stage.date);
    });

    if (dates.length === 0) return 'N/A';
    dates.sort();
    const earliest = new Date(dates[0]).toLocaleDateString();
    const latest = new Date(dates[dates.length - 1]).toLocaleDateString();
    return `${earliest} - ${latest}`;
  };

  const completedStages = Object.values(pipeline.stages).filter(s => s.status === 'complete').length;

  return (
    <div className="grid grid-cols-3 gap-4">
      <div className="bg-white rounded-lg shadow-md p-6 h-32 flex flex-col justify-between">
        <div className="flex items-center gap-3">
          <span className="material-symbols-rounded text-3xl text-blue-500">water_drop</span>
          <div className="text-sm font-medium text-gray-500">Total Files</div>
        </div>
        <div className="text-3xl font-bold text-gray-900">{pipeline.file_count.toLocaleString()}</div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6 h-32 flex flex-col justify-between">
        <div className="flex items-center gap-3">
          <span className="material-symbols-rounded text-3xl text-green-500">calendar_today</span>
          <div className="text-sm font-medium text-gray-500">Date Range</div>
        </div>
        <div className="text-lg font-bold text-gray-900">{getDateRange()}</div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6 h-32 flex flex-col justify-between">
        <div className="flex items-center gap-3">
          <span className="material-symbols-rounded text-3xl text-purple-500">check_circle</span>
          <div className="text-sm font-medium text-gray-500">Completed Stages</div>
        </div>
        <div className="text-3xl font-bold text-gray-900">
          {completedStages} / {Object.keys(pipeline.stages).length}
        </div>
      </div>
    </div>
  );
}