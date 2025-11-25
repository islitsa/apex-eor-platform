import React, { useState } from 'react';
import type { Pipeline, FileNode } from '../types';

interface Props {
  pipeline: Pipeline;
  onFileSelect: (filePath: string) => void;
}

export default function FileExplorerTree({ pipeline, onFileSelect }: Props) {
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

  const renderNode = (node: FileNode, depth: number = 0): React.ReactNode => {
    const isExpanded = expandedPaths.has(node.path);
    const isDirectory = node.type === 'directory' || node.type === 'folder';
    const hasChildren = node.children && node.children.length > 0;

    return (
      <div key={node.path}>
        <div
          className="flex items-center gap-2 py-2 px-3 hover:bg-gray-100 rounded cursor-pointer transition-colors"
          style={{ paddingLeft: `${depth * 24 + 12}px` }}
          onClick={() => {
            if (isDirectory && hasChildren) {
              toggleExpand(node.path);
            } else if (!isDirectory) {
              onFileSelect(node.path);
            }
          }}
        >
          {isDirectory && hasChildren && (
            <span className="material-symbols-rounded text-gray-600 text-sm">
              {isExpanded ? 'expand_more' : 'chevron_right'}
            </span>
          )}
          {!isDirectory && (
            <span className="material-symbols-rounded text-blue-600 text-sm ml-5">
              description
            </span>
          )}
          {isDirectory && (
            <span className="material-symbols-rounded text-yellow-600 text-sm">
              folder
            </span>
          )}
          <span className="text-sm text-gray-900 flex-1">{node.name}</span>
          {node.file_count !== undefined && (
            <span className="text-xs text-gray-500">{node.file_count} files</span>
          )}
        </div>

        {isExpanded && hasChildren && (
          <div>
            {node.children?.map(child => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  if (!pipeline.files) {
    return (
      <div className="text-center py-8 text-gray-500">
        <span className="material-symbols-rounded text-4xl mb-2">folder_off</span>
        <p>No files available</p>
      </div>
    );
  }

  const normalizedFiles = Array.isArray(pipeline.files)
    ? pipeline.files.map(node => normalizeNode(node))
    : [];

  return (
    <div className="space-y-1">
      {normalizedFiles.map(node => renderNode(node, 0))}
    </div>
  );
}