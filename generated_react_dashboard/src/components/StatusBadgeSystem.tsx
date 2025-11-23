import React from 'react';

interface StatusBadgeSystemProps {
  status: string;
}

export default function StatusBadgeSystem({ status }: StatusBadgeSystemProps) {
  const normalizedStatus = String(status || 'unknown').toLowerCase();
  
  let bgColor = 'bg-gray-500';
  let textColor = 'text-white';
  let displayText = String(status || 'unknown').replace(/_/g, ' ');

  if (normalizedStatus === 'complete' || normalizedStatus === 'completed') {
    bgColor = 'bg-green-600';
    displayText = 'Complete';
  } else if (normalizedStatus === 'error' || normalizedStatus === 'failed') {
    bgColor = 'bg-red-600';
    displayText = 'Error';
  } else if (normalizedStatus === 'running' || normalizedStatus === 'in_progress') {
    bgColor = 'bg-amber-600';
    displayText = 'Running';
  } else if (normalizedStatus === 'pending') {
    bgColor = 'bg-amber-500';
    displayText = 'Pending';
  }

  return (
    <span className={`inline-block px-2 py-1 rounded-md text-xs font-bold ${bgColor} ${textColor}`}>
      {displayText}
    </span>
  );
}