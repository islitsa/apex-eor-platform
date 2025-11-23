import React from 'react';

interface StageIndicatorProps {
  name: string;
  status: string;
  date?: string;
  note?: string;
}

export default function StageIndicator({ name, status, date, note }: StageIndicatorProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'complete':
        return 'bg-success text-white';
      case 'processing':
        return 'bg-primary text-white';
      case 'not_started':
        return 'bg-gray-300 text-gray-600';
      default:
        return 'bg-gray-300 text-gray-600';
    }
  };

  const getIcon = (name: string) => {
    switch (name) {
      case 'download':
        return 'download';
      case 'extraction':
        return 'folder_zip';
      case 'parsing':
        return 'description';
      case 'validation':
        return 'check_circle';
      case 'loading':
        return 'upload';
      default:
        return 'circle';
    }
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return null;
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  return (
    <div className="flex flex-col items-center gap-2 min-w-[100px]">
      <div
        className={`w-12 h-12 rounded-full flex items-center justify-center ${getStatusColor(
          status
        )} shadow-sm`}
        title={note}
      >
        <span className="material-symbols-rounded text-xl">{getIcon(name)}</span>
      </div>
      <div className="text-center">
        <p className="text-sm font-medium text-gray-900 capitalize">{name}</p>
        {date && (
          <p className="text-xs text-gray-500 mt-0.5">{formatDate(date)}</p>
        )}
      </div>
    </div>
  );
}