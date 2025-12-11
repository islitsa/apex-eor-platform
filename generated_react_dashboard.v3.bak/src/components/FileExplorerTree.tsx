import React, { useState } from 'react';
import { FileNode } from '../types.ts';

interface FileExplorerTreeProps {
  nodes: FileNode[];
  onFileSelect?: (filePath: string) => void;
  selectedFile?: string | null;
  level?: number;
}

function FileExplorerTree({ nodes, onFileSelect, selectedFile, level = 0 }: FileExplorerTreeProps) {
  const [expandedDirs, setExpandedDirs] = useState<Set<string>>(new Set());

  const toggleDirectory = (path: string) => {
    setExpandedDirs(prev => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return next;
    });
  };

  const handleFileClick = (node: FileNode) => {
    if (node.type === 'file' && onFileSelect) {
      onFileSelect(node.path);
    } else if (node.type === 'directory') {
      toggleDirectory(node.path);
    }
  };

  return (
    <div>
      {nodes.map((node, index) => {
        const isExpanded = expandedDirs.has(node.path);
        const isSelected = selectedFile === node.path;
        const isDirectory = node.type === 'directory';

        return (
          <div key={`${node.path}-${index}`}>
            <div
              className={`flex items-center gap-2 py-3 px-3 cursor-pointer hover:bg-gray-50 rounded transition-colors ${
                isSelected ? 'bg-blue-50 border-l-4 border-primary' : ''
              }`}
              style={{ paddingLeft: `${level * 24 + 12}px`, height: '48px' }}
              onClick={() => handleFileClick(node)}
            >
              <span className="material-symbols-rounded text-gray-600 text-xl">
                {isDirectory ? (isExpanded ? 'folder_open' : 'folder') : 'description'}
              </span>
              <span className={`text-sm ${isSelected ? 'font-semibold text-primary' : 'text-gray-700'}`}>
                {node.name}
              </span>
              {isDirectory && node.file_count !== undefined && (
                <span className="text-xs text-gray-500 ml-auto">
                  {node.file_count} {node.file_count === 1 ? 'file' : 'files'}
                </span>
              )}
            </div>
            {isDirectory && isExpanded && node.children && node.children.length > 0 && (
              <FileExplorerTree
                nodes={node.children}
                onFileSelect={onFileSelect}
                selectedFile={selectedFile}
                level={level + 1}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}

export default FileExplorerTree;