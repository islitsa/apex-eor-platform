import React, { useState, useCallback } from 'react';
import { FileNode } from '../types.ts';

interface FileTreeNavigatorProps {
  nodes: FileNode[];
  onFileSelect?: (filePath: string) => void;
  selectedFile?: string | null;
}

export function FileTreeNavigator({ nodes, onFileSelect, selectedFile }: FileTreeNavigatorProps) {
  const [expandedPaths, setExpandedPaths] = useState<Set<string>>(new Set());

  const toggleExpand = useCallback((path: string) => {
    setExpandedPaths((prev) => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return next;
    });
  }, []);

  const handleFileClick = useCallback(
    (node: FileNode) => {
      if (node.type === 'file' && onFileSelect) {
        onFileSelect(node.path);
      } else if (node.type === 'directory') {
        toggleExpand(node.path);
      }
    },
    [onFileSelect, toggleExpand]
  );

  const renderNode = (node: FileNode, depth: number = 0): React.ReactNode => {
    const isExpanded = expandedPaths.has(node.path);
    const isDirectory = node.type === 'directory';
    const isSelected = selectedFile === node.path;
    const hasChildren = (node.children ?? []).length > 0;

    return (
      <div key={node.path}>
        <div
          className={`flex items-center h-10 px-3 cursor-pointer hover:bg-gray-50 ${
            isSelected ? 'bg-blue-50' : ''
          }`}
          style={{ paddingLeft: `${depth * 16 + 12}px` }}
          onClick={() => handleFileClick(node)}
        >
          <span className="material-symbols-rounded text-gray-600 text-[20px] mr-2">
            {isDirectory ? 'folder' : 'description'}
          </span>
          <span className={`text-sm ${isSelected ? 'font-medium text-blue-600' : 'text-gray-900'}`}>
            {node.name}
          </span>
        </div>
        {isDirectory && isExpanded && hasChildren && (
          <div>
            {node.children.map((child) => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      {nodes.map((node) => renderNode(node, 0))}
    </div>
  );
}