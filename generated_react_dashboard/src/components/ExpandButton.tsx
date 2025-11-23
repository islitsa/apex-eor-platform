import React from 'react';

interface ExpandButtonProps {
  isExpanded: boolean;
  onClick: () => void;
}

export default function ExpandButton({ isExpanded, onClick }: ExpandButtonProps) {
  return (
    <button
      onClick={onClick}
      className="w-full flex items-center justify-center gap-2 px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors duration-200"
      style={{ height: '36px' }}
    >
      <span className="text-sm font-medium">
        {isExpanded ? 'Hide Files & Data' : 'View Files & Data'}
      </span>
      <span className="material-symbols-rounded" style={{ fontSize: '16px' }}>
        {isExpanded ? 'expand_less' : 'expand_more'}
      </span>
    </button>
  );
}