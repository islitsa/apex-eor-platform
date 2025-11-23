import React from 'react';

interface ActionButtonBarProps {
  onExplore: () => void;
  onDownload: () => void;
  isExpanded: boolean;
}

export default function ActionButtonBar({ onExplore, onDownload, isExpanded }: ActionButtonBarProps) {
  return (
    <div className="flex items-center gap-3">
      <button
        onClick={onDownload}
        className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-all active:translate-y-0.5"
      >
        <span className="material-symbols-rounded text-xl">cloud_download</span>
        Download
      </button>
      <button
        onClick={onExplore}
        className="flex items-center gap-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-bold transition-all active:translate-y-0.5 h-[40px]"
      >
        <span className="material-symbols-rounded text-xl">
          {isExpanded ? 'expand_less' : 'expand_more'}
        </span>
        {isExpanded ? 'Collapse' : 'Explore Data'}
      </button>
    </div>
  );
}