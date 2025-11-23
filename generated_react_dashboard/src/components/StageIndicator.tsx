import React from 'react';
import { Stage } from '../types.ts';

interface StageIndicatorProps {
  stage: Stage;
}

export function StageIndicator({ stage }: StageIndicatorProps) {
  const status = String(stage.status || 'unknown').toLowerCase();
  
  const statusColors: Record<string, string> = {
    complete: 'bg-green-500',
    completed: 'bg-green-500',
    processed: 'bg-green-500',
    processing: 'bg-blue-500',
    pending: 'bg-yellow-500',
    error: 'bg-red-500',
    failed: 'bg-red-500'
  };

  const bgColor = statusColors[status] || 'bg-slate-400';

  return (
    <div className="flex flex-col items-center gap-1">
      <div className={`${bgColor} rounded-full w-10 h-10 flex items-center justify-center shadow-sm`}>
        <span className="material-symbols-rounded text-white text-sm">
          {status === 'complete' || status === 'completed' || status === 'processed' ? 'check' : 
           status === 'processing' ? 'sync' :
           status === 'error' || status === 'failed' ? 'close' : 'schedule'}
        </span>
      </div>
      <span className="text-xs text-slate-600 font-medium text-center max-w-[80px] truncate">
        {String(stage.name || 'unknown').replace(/_/g, ' ')}
      </span>
    </div>
  );
}