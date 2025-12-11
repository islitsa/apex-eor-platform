import React, { useState } from 'react';
import type { Pipeline, FileNode } from '../types';

interface Props {
  pipeline: Pipeline;
}

export default function FileExplorerPanel({ pipeline }: Props) {
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

  const toggleExpand = (path: string) => {
    setExpandedPaths(prev => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return next;
    });
  };

  const formatFileSize = (bytes?: number): string => {
    if (!bytes) return '';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
  };

  const renderNode = (node: FileNode, depth: number): React.ReactNode => {
    const isExpanded = expandedPaths.has(node.path);
    const isDirectory = node.type === 'directory' || node.type === 'folder';
    const hasChildren = node.children && node.children.length > 0;

    return (
      <div key={node.path}>
        <div
          className={`
            flex items-center gap-2 px-3 py-2 hover:bg-gray-50 cursor-pointer rounded-lg
            transition-colors duration-150
          `}
          style={{ paddingLeft: `${depth * 20 + 12}px` }}
          onClick={() => isDirectory && toggleExpand(node.path)}
        >
          {isDirectory && (
            <span className="material-symbols-rounded text-gray-400 text-sm">
              {isExpanded ? 'expand_more' : 'chevron_right'}
            </span>
          )}
          <span className={`material-symbols-rounded ${isDirectory ? 'text-blue-600' : 'text-gray-500'} text-lg`}>
            {isDirectory ? 'folder' : 'description'}
          </span>
          <span className="text-sm text-gray-900 flex-1">{node.name}</span>
          {node.size && (
            <span className="text-xs text-gray-500">{formatFileSize(node.size)}</span>
          )}
          {isDirectory && node.file_count !== undefined && (
            <span className="text-xs text-gray-500">{node.file_count} files</span>
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

  const normalizedFiles = (pipeline.files || []).map(node => normalizeNode(node));

  return (
    <div className="bg-white rounded-2xl shadow-md border border-gray-200 overflow-hidden">
      <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <span className="material-symbols-rounded text-gray-700">folder_open</span>
          <h2 className="text-lg font-bold text-gray-900">File Explorer</h2>
        </div>
        <p className="text-sm text-gray-600 mt-1">
          {pipeline.metrics?.file_count || 0} files • {pipeline.metrics?.data_size || '0 B'}
        </p>
      </div>
      <div className="overflow-y-auto max-h-[600px] p-2">
        {normalizedFiles.length > 0 ? (
          normalizedFiles.map(node => renderNode(node, 0))
        ) : (
          <div className="text-center py-8 text-gray-500">
            <span className="material-symbols-rounded text-4xl mb-2">folder_off</span>
            <p>No files available</p>
          </div>
        )}
      </div>
    </div>
  );
}