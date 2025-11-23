import React, { useState, useMemo } from 'react';
import { Pipeline, FileNode } from '../types.ts';

interface FileNavigatorProps {
  pipeline: Pipeline;
  selectedPath: string;
  onPathChange: (path: string) => void;
}

export default function FileNavigator({ pipeline, selectedPath, onPathChange }: FileNavigatorProps) {
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set(['/']));

  const toggleFolder = (path: string) => {
    const newExpanded = new Set(expandedFolders);
    if (newExpanded.has(path)) {
      newExpanded.delete(path);
    } else {
      newExpanded.add(path);
    }
    setExpandedFolders(newExpanded);
  };

  const renderFileTree = (node: FileNode, path: string = '', level: number = 0): React.ReactNode => {
    if (!node || typeof node !== 'object') return null;

    const entries = Object.entries(node);
    
    return entries.map(([key, value]) => {
      const currentPath = path ? `${path}/${key}` : key;
      const isFolder = value && typeof value === 'object' && !Array.isArray(value);
      const isExpanded = expandedFolders.has(currentPath);

      if (isFolder) {
        const folderEntries = Object.entries(value as FileNode);
        const fileCount = folderEntries.filter(([_, v]) => typeof v !== 'object').length;
        const subfolderCount = folderEntries.filter(([_, v]) => typeof v === 'object').length;

        return (
          <div key={currentPath}>
            <div
              onClick={() => toggleFolder(currentPath)}
              className="flex items-center gap-2 px-3 py-2 hover:bg-gray-50 cursor-pointer rounded-lg transition-colors"
              style={{ paddingLeft: `${level * 20 + 12}px` }}
            >
              <span className="material-symbols-rounded text-gray-600 text-xl">
                {isExpanded ? 'folder_open' : 'folder'}
              </span>
              <span className="flex-1 font-medium text-gray-900">{key}</span>
              <span className="text-xs text-gray-500">
                {fileCount > 0 && `${fileCount} files`}
                {fileCount > 0 && subfolderCount > 0 && ', '}
                {subfolderCount > 0 && `${subfolderCount} folders`}
              </span>
              <span className="material-symbols-rounded text-gray-400 text-sm">
                {isExpanded ? 'expand_more' : 'chevron_right'}
              </span>
            </div>
            {isExpanded && (
              <div>
                {renderFileTree(value as FileNode, currentPath, level + 1)}
              </div>
            )}
          </div>
        );
      } else {
        return (
          <div
            key={currentPath}
            onClick={() => onPathChange(currentPath)}
            className={`flex items-center gap-2 px-3 py-2 hover:bg-blue-50 cursor-pointer rounded-lg transition-colors ${
              selectedPath === currentPath ? 'bg-blue-50 border-l-2 border-blue-600' : ''
            }`}
            style={{ paddingLeft: `${level * 20 + 12}px` }}
          >
            <span className="material-symbols-rounded text-gray-400 text-xl">description</span>
            <span className="flex-1 text-gray-700">{key}</span>
            {typeof value === 'number' && (
              <span className="text-xs text-gray-500">{value.toLocaleString()} bytes</span>
            )}
          </div>
        );
      }
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="border-b border-gray-200 px-6 py-4">
        <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
          <span className="material-symbols-rounded">folder_open</span>
          File Navigator
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          Browse pipeline files and folders
        </p>
      </div>
      <div className="p-4 max-h-[600px] overflow-y-auto">
        {pipeline.files && Object.keys(pipeline.files).length > 0 ? (
          renderFileTree(pipeline.files)
        ) : (
          <div className="text-center py-12 text-gray-500">
            <span className="material-symbols-rounded text-4xl mb-2">folder_off</span>
            <p>No files found</p>
          </div>
        )}
      </div>
    </div>
  );
}