import React, { useState, useMemo } from 'react';
import type { Pipeline, FileNode } from '../types';

interface Props {
  pipeline: Pipeline;
  onFileSelect: (pipeline: Pipeline, filePath: string) => void;
  selectedFile: string | null;
}

export default function FileExplorerTree({ pipeline, onFileSelect, selectedFile }: Props) {
  const [expandedPaths, setExpandedPaths] = useState<Set<string>>(new Set());

  const normalizeNode = (node: any): FileNode => {
    let children: FileNode[] = [];

    if (node.children && Array.isArray(node.children)) {
      children = node.children.map((child: any) => normalizeNode(child));
    } else {
      if (node.subdirs && typeof node.subdirs === 'object') {
        Object.values(node.subdirs).forEach((subdir: any) => {
          children.push(normalizeNode(subdir));
        });
      }
      if (node.files && Array.isArray(node.files)) {
        node.files.forEach((file: any) => {
          children.push({
            ...file,
            type: file.type || 'file',
            path: file.path || `${node.path}/${file.name}`,
            children: [],
          });
        });
      }
    }

    const normalizedType = node.type === 'folder' ? 'directory' : (node.type || 'directory');

    return {
      name: node.name,
      path: node.path,
      type: normalizedType as 'file' | 'directory',
      children,
      file_count: node.file_count,
      size: node.size_bytes || node.size,
    };
  };

  const normalizedFiles = useMemo(() => {
    if (!pipeline.files || !Array.isArray(pipeline.files)) return [];
    return pipeline.files.map(node => normalizeNode(node));
  }, [pipeline.files]);

  const toggleExpand = (path: string) => {
    const newExpanded = new Set(expandedPaths);
    if (newExpanded.has(path)) {
      newExpanded.delete(path);
    } else {
      newExpanded.add(path);
    }
    setExpandedPaths(newExpanded);
  };

  const formatFileSize = (bytes?: number): string => {
    if (!bytes) return '';
    const kb = bytes / 1024;
    const mb = kb / 1024;
    const gb = mb / 1024;

    if (gb >= 1) return `${Number(gb).toFixed(2)} GB`;
    if (mb >= 1) return `${Number(mb).toFixed(2)} MB`;
    if (kb >= 1) return `${Number(kb).toFixed(2)} KB`;
    return `${bytes} B`;
  };

  const renderNode = (node: FileNode, depth: number): React.ReactNode => {
    const isDirectory = node.type === 'directory' || node.type === 'folder';
    const isExpanded = expandedPaths.has(node.path);
    const isSelected = selectedFile === node.path;
    const hasChildren = node.children && node.children.length > 0;

    return (
      <div key={node.path}>
        <div
          className={`flex items-center gap-2 px-4 py-3 hover:bg-gray-100 cursor-pointer transition-colors ${
            isSelected ? 'bg-blue-50 border-l-4 border-blue-600' : ''
          }`}
          style={{ paddingLeft: `${depth * 24 + 16}px` }}
          onClick={() => {
            if (isDirectory && hasChildren) {
              toggleExpand(node.path);
            } else if (!isDirectory) {
              onFileSelect(pipeline, node.path);
            }
          }}
        >
          {isDirectory && hasChildren && (
            <span
              className={`material-symbols-rounded text-gray-600 text-xl transition-transform ${
                isExpanded ? 'rotate-90' : ''
              }`}
            >
              navigate_next
            </span>
          )}
          {isDirectory && !hasChildren && (
            <span className="material-symbols-rounded text-gray-400 text-xl">
              navigate_next
            </span>
          )}
          {!isDirectory && (
            <span className="w-5"></span>
          )}
          
          <span className={`material-symbols-rounded ${isDirectory ? 'text-blue-600' : 'text-gray-500'} text-xl`}>
            {isDirectory ? 'folder' : 'description'}
          </span>
          
          <span className={`flex-1 ${isSelected ? 'font-semibold text-blue-900' : 'text-gray-900'}`}>
            {node.name}
          </span>
          
          {node.file_count !== undefined && node.file_count > 0 && (
            <span className="text-sm text-gray-500">
              {node.file_count} file{node.file_count !== 1 ? 's' : ''}
            </span>
          )}
          
          {node.size !== undefined && node.size > 0 && (
            <span className="text-sm text-gray-500 ml-4">
              {formatFileSize(node.size)}
            </span>
          )}
        </div>
        
        {isDirectory && isExpanded && hasChildren && (
          <div>
            {node.children!.map(child => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  if (normalizedFiles.length === 0) {
    return (
      <div className="p-8 text-center text-gray-500">
        <span className="material-symbols-rounded text-4xl mb-2">folder_off</span>
        <p>No files available</p>
      </div>
    );
  }

  return (
    <div className="divide-y divide-gray-100">
      {normalizedFiles.map(node => renderNode(node, 0))}
    </div>
  );
}