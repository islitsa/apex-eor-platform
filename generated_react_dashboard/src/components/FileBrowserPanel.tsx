import React, { useState } from 'react';
import { Pipeline, FileNode } from '../types';

interface Props {
  pipeline: Pipeline;
}

export default function FileBrowserPanel({ pipeline }: Props) {
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
    const newExpanded = new Set(expandedPaths);
    if (newExpanded.has(path)) {
      newExpanded.delete(path);
    } else {
      newExpanded.add(path);
    }
    setExpandedPaths(newExpanded);
  };

  const formatSize = (bytes: number | undefined): string => {
    if (!bytes) return '';
    const mb = bytes / (1024 * 1024);
    if (mb < 1) return `${(bytes / 1024).toFixed(1)} KB`;
    if (mb < 1024) return `${mb.toFixed(1)} MB`;
    return `${(mb / 1024).toFixed(2)} GB`;
  };

  const renderNode = (node: FileNode, depth: number = 0): React.ReactNode => {
    const isExpanded = expandedPaths.has(node.path);
    const hasChildren = node.children && node.children.length > 0;
    const isDirectory = node.type === 'directory' || node.type === 'folder';

    return (
      <div key={node.path}>
        <div
          className="flex items-center gap-2 py-2 px-2 hover:bg-gray-50 rounded cursor-pointer transition-colors"
          style={{ paddingLeft: `${depth * 20 + 8}px` }}
          onClick={() => isDirectory && hasChildren && toggleExpand(node.path)}
        >
          {isDirectory && hasChildren && (
            <span className="material-symbols-rounded text-gray-400 text-base">
              {isExpanded ? 'expand_more' : 'chevron_right'}
            </span>
          )}
          {isDirectory && !hasChildren && (
            <span className="material-symbols-rounded text-gray-400 text-base">folder</span>
          )}
          {!isDirectory && (
            <span className="material-symbols-rounded text-blue-600 text-base">description</span>
          )}
          <span className="text-sm text-gray-900 flex-1 truncate">{node.name}</span>
          {node.size && (
            <span className="text-xs text-gray-500">{formatSize(node.size)}</span>
          )}
          {isDirectory && node.file_count !== undefined && (
            <span className="text-xs text-gray-500">{node.file_count} files</span>
          )}
        </div>
        {isDirectory && hasChildren && isExpanded && (
          <div>
            {node.children?.map(child => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  if (!pipeline.files || pipeline.files.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <span className="material-symbols-rounded text-4xl block mb-2">folder_off</span>
        <p className="text-sm">No files available</p>
      </div>
    );
  }

  const normalizedFiles = pipeline.files.map(node => normalizeNode(node));

  return (
    <div className="max-h-96 overflow-y-auto">
      <div className="flex items-center gap-2 mb-3 text-sm text-gray-600">
        <span className="material-symbols-rounded text-base">folder</span>
        <span className="font-semibold">File Browser</span>
      </div>
      <div className="border border-gray-200 rounded-lg overflow-hidden">
        {normalizedFiles.map(node => renderNode(node, 0))}
      </div>
    </div>
  );
}