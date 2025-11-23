import React, { useState } from 'react';
import type { FileNode } from '../types.ts';

interface FileExplorerSectionProps {
  files: FileNode[];
  onFileSelect: (file: FileNode) => void;
  selectedFile: FileNode | null;
}

export default function FileExplorerSection({
  files,
  onFileSelect,
  selectedFile
}: FileExplorerSectionProps) {
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set());

  const toggleFolder = (path: string) => {
    setExpandedFolders(prev => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return next;
    });
  };

  const formatBytes = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 ** 2) return `${(bytes / 1024).toFixed(1)} KB`;
    if (bytes < 1024 ** 3) return `${(bytes / (1024 ** 2)).toFixed(1)} MB`;
    return `${(bytes / (1024 ** 3)).toFixed(2)} GB`;
  };

  const renderFileNode = (node: FileNode, level: number = 0) => {
    const isExpanded = expandedFolders.has(node.path);
    const isSelected = selectedFile?.path === node.path;

    return (
      <div key={node.path}>
        <button
          onClick={() => {
            if (node.type === 'folder') {
              toggleFolder(node.path);
            } else {
              onFileSelect(node);
            }
          }}
          className={`w-full h-11 px-3 flex items-center gap-3 hover:bg-blue-50 transition-colors duration-200 ${
            isSelected ? 'bg-blue-100' : ''
          }`}
          style={{ paddingLeft: `${level * 20 + 12}px` }}
        >
          <span className="material-symbols-rounded text-gray-600 text-xl">
            {node.type === 'folder' ? (isExpanded ? 'folder_open' : 'folder') : 'description'}
          </span>

          <span className="flex-1 text-left text-sm text-gray-900 truncate">
            {node.name}
          </span>

          {node.type === 'folder' && node.file_count !== undefined && (
            <span className="text-xs text-gray-500 font-mono">
              {Number(node.file_count || 0).toLocaleString()} files
            </span>
          )}

          {node.type === 'file' && node.size !== undefined && (
            <span className="text-xs text-gray-500 font-mono">
              {formatBytes(Number(node.size || 0))}
            </span>
          )}

          {node.type === 'folder' && (
            <span
              className={`material-symbols-rounded text-gray-400 text-lg transition-transform duration-200 ${
                isExpanded ? 'rotate-180' : ''
              }`}
            >
              expand_more
            </span>
          )}
        </button>

        {node.type === 'folder' && isExpanded && node.children && (
          <div>
            {node.children.map(child => renderFileNode(child, level + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <span className="material-symbols-rounded text-gray-700">folder</span>
        <h3 className="text-xl font-semibold text-gray-900">File Explorer</h3>
      </div>

      <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
        <div className="h-[400px] overflow-y-auto">
          {files.length > 0 ? (
            files.map(file => renderFileNode(file))
          ) : (
            <div className="h-full flex items-center justify-center text-gray-500">
              <div className="text-center">
                <span className="material-symbols-rounded text-5xl text-gray-400 mb-2">
                  folder_off
                </span>
                <p>No files available</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}