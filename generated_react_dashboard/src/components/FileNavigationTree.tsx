import React, { useState, useMemo } from 'react';
import type { Pipeline, FileNode } from '../types';

interface Props {
  pipeline: Pipeline;
  selectedFile: string | null;
  onFileSelect: (filePath: string) => void;
}

export default function FileNavigationTree({ pipeline, selectedFile, onFileSelect }: Props) {
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
    if (!pipeline.files) return [];
    if (Array.isArray(pipeline.files)) {
      return pipeline.files.map(node => normalizeNode(node));
    }
    return [normalizeNode(pipeline.files)];
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

  const renderNode = (node: FileNode, depth: number = 0): React.ReactNode => {
    const isDirectory = node.type === 'directory' || node.type === 'folder';
    const isExpanded = expandedPaths.has(node.path);
    const hasChildren = node.children && node.children.length > 0;
    const isSelected = selectedFile === node.path;

    return (
      <div key={node.path}>
        <div
          className={`flex items-center gap-2 py-2 px-3 rounded cursor-pointer transition-colors ${
            isSelected ? 'bg-blue-100 text-blue-900' : 'hover:bg-gray-100'
          }`}
          style={{ paddingLeft: `${depth * 20 + 12}px` }}
          onClick={() => {
            if (isDirectory && hasChildren) {
              toggleExpand(node.path);
            } else if (!isDirectory) {
              onFileSelect(node.path);
            }
          }}
        >
          {isDirectory && hasChildren && (
            <span className="material-symbols-rounded text-base text-gray-500">
              {isExpanded ? 'expand_more' : 'chevron_right'}
            </span>
          )}
          {isDirectory && !hasChildren && (
            <span className="w-5"></span>
          )}
          <span className={`material-symbols-rounded text-lg ${isDirectory ? 'text-blue-600' : 'text-gray-600'}`}>
            {isDirectory ? 'folder' : 'description'}
          </span>
          <span className="text-sm font-medium text-gray-900 flex-1 truncate">
            {node.name}
          </span>
          {node.file_count !== undefined && node.file_count > 0 && (
            <span className="text-xs text-gray-500">
              {Number(node.file_count || 0).toLocaleString()}
            </span>
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

  if (!normalizedFiles || normalizedFiles.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <span className="material-symbols-rounded text-4xl mb-2 opacity-30">folder_off</span>
        <p className="text-sm">No files available</p>
      </div>
    );
  }

  return (
    <div className="max-h-[600px] overflow-y-auto">
      {normalizedFiles.map(node => renderNode(node, 0))}
    </div>
  );
}