import React, { useState } from 'react';

interface Props {
  stage: 'download' | 'transform' | 'code';
  status: 'complete' | 'in-progress' | 'pending';
  count: number;
}

export default function PipelineHealthBadge({ stage, status, count }: Props) {
  const [showTooltip, setShowTooltip] = useState(false);

  const icons = {
    download: 'download',
    transform: 'transform',
    code: 'code'
  };

  const colors = {
    complete: 'bg-green-500',
    'in-progress': 'bg-blue-500',
    pending: 'bg-gray-400'
  };

  const statusText = {
    complete: 'Complete',
    'in-progress': 'In Progress',
    pending: 'Pending'
  };

  return (
    <div
      className="relative flex flex-col items-center"
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      <div className={`w-8 h-8 rounded-full ${colors[status]} flex items-center justify-center text-white shadow-md`}>
        <span className="material-symbols-rounded text-lg">{icons[stage]}</span>
      </div>
      <div className="text-xs font-bold text-gray-700 mt-1">{statusText[status]}</div>

      {showTooltip && (
        <div className="absolute top-full mt-2 bg-gray-900 text-white text-xs rounded px-3 py-2 whitespace-nowrap z-10 shadow-lg">
          {count} pipelines {statusText[status].toLowerCase()}
          <div className="absolute -top-1 left-1/2 transform -translate-x-1/2 w-2 h-2 bg-gray-900 rotate-45"></div>
        </div>
      )}
    </div>
  );
}