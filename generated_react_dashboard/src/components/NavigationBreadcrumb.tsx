import React from 'react';
import type { Pipeline, FileNode } from '../types';

interface NavigationBreadcrumbProps {
  selectedPipeline: Pipeline | null;
  selectedFile: FileNode | null;
}

export default function NavigationBreadcrumb({ selectedPipeline, selectedFile }: NavigationBreadcrumbProps) {
  return (
    <div className="flex items-center gap-2 text-sm text-gray-600">
      <span className="material-symbols-rounded text-base">home</span>
      <span>Dashboard</span>
      {selectedPipeline && (
        <>
          <span className="material-symbols-rounded text-base">chevron_right</span>
          <span className="text-gray-900 font-medium">{String(selectedPipeline.name || 'Unknown')}</span>
        </>
      )}
      {selectedFile && (
        <>
          <span className="material-symbols-rounded text-base">chevron_right</span>
          <span className="text-gray-900 font-medium">{String(selectedFile.name || 'Unknown')}</span>
        </>
      )}
    </div>
  );
}