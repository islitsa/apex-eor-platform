import React, { useState, useCallback, useMemo } from 'react';
import { Pipeline, FileNode } from '../types.ts';

interface FileNavigationTreeProps {
  pipeline: Pipeline;
  onFileSelect: (path: string) => void;
  selectedPath: string | null;
}

function FileNavigationTree({ pipeline, onFileSelect, selectedPath }: FileNavigationTreeProps) {
  const [expandedPaths, setExpandedPaths] = useState<Set<string>>(new Set());

  const normalizeNode = useCallback((node: any): FileNode => {
    let children: FileNode[] = [];
    if (node.children) {
      children = node.children.map(normalizeNode);
    } else {
      if (node.subdirs) {
        Object.values(node.subdirs).forEach((d: any) => {
          children.push(normalizeNode(d));
        });
      }
      if (node.files) {
        node.files.forEach((f: any) => {
          children.push({
            ...f,
            type: 'file',
            children: [],
          });
        });
      }
    }
    return {
      name: node.name,
      path: node.path,
      type: node.type === 'folder' ? 'directory' : (node.type || 'directory'),
      children,
      file_count: node.file_count,
      size: node.size_bytes || node.size,
    };
  }, []);

  const normalizedFiles = useMemo(() => {
    return (pipeline.files || []).map(normalizeNode);
  }, [pipeline.files, normalizeNode]);

  const toggleExpand = useCallback((path: string) => {
    setExpandedPaths(prev => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return next;
    });
  }, []);

  const handleNodeClick = useCallback((node: FileNode) => {
    if (node.type === 'directory') {
      toggleExpand(node.path);
    } else {
      onFileSelect(node.path);
    }
  }, [toggleExpand, onFileSelect]);

  const renderNode = (node: FileNode, level: number = 0) => {
    const isExpanded = expandedPaths.has(node.path);
    const isSelected = selectedPath === node.path;
    const isDirectory = node.type === 'directory';
    const hasChildren = node.children && node.children.length > 0;

    return (
      <div key={node.path}>
        <div
          onClick={() => handleNodeClick(node)}
          className={`flex items-center gap-2 px-4 py-2.5 cursor-pointer hover:bg-gray-100 transition-colors ${
            isSelected ? 'bg-blue-50 border-l-4 border-blue-600' : ''
          }`}
          style={{ paddingLeft: `${16 + level * 20}px` }}
        >
          {isDirectory && hasChildren && (
            <span className="material-symbols-rounded text-gray-500 text-lg transition-transform" style={{
              transform: isExpanded ? 'rotate(90deg)' : 'rotate(0deg)',
            }}>
              chevron_right
            </span>
          )}
          {isDirectory && !hasChildren && (
            <span className="w-5"></span>
          )}
          <span className={`material-symbols-rounded text-xl ${isDirectory ? 'text-blue-600' : 'text-gray-600'}`}>
            {isDirectory ? 'folder' : 'description'}
          </span>
          <span className={`text-sm flex-1 ${isSelected ? 'font-semibold text-blue-900' : 'text-gray-900'}`}>
            {node.name}
          </span>
          {isDirectory && node.file_count !== undefined && (
            <span className="text-xs text-gray-500">
              {node.file_count}
            </span>
          )}
        </div>
        {isDirectory && isExpanded && hasChildren && (
          <div>
            {node.children.map(child => renderNode(child, level + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="h-full overflow-y-auto">
      <div className="p-4 border-b border-gray-200 bg-white">
        <h3 className="font-semibold text-gray-900 flex items-center gap-2">
          <span className="material-symbols-rounded text-xl">folder_open</span>
          File Explorer
        </h3>
      </div>
      <div className="py-2">
        {normalizedFiles.length > 0 ? (
          normalizedFiles.map(node => renderNode(node))
        ) : (
          <div className="p-4 text-center text-gray-500 text-sm">
            No files available
          </div>
        )}
      </div>
    </div>
  );
}

export default FileNavigationTree;