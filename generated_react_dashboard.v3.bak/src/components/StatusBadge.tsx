import React from 'react';

interface StatusBadgeProps {
  status: string;
}

function StatusBadge({ status }: StatusBadgeProps) {
  const normalizedStatus = String(status || '').toLowerCase();
  
  let bgColor = 'bg-gray-400';
  let icon = 'pending';
  
  if (normalizedStatus === 'completed' || normalizedStatus === 'processed') {
    bgColor = 'bg-green-500';
    icon = 'check_circle';
  } else if (normalizedStatus === 'running' || normalizedStatus === 'processing') {
    bgColor = 'bg-yellow-500';
    icon = 'pending';
  } else if (normalizedStatus === 'failed' || normalizedStatus === 'error') {
    bgColor = 'bg-red-500';
    icon = 'error';
  }

  return (
    <div className={`inline-flex items-center gap-1 h-6 px-3 rounded-full ${bgColor}`}>
      <span className="material-symbols-rounded text-white text-xs">{icon}</span>
      <span className="text-white text-xs font-semibold uppercase">{status}</span>
    </div>
  );
}

export { StatusBadge };
export default StatusBadge;