import React, { useState, useMemo } from 'react';
import type { Pipeline, FileNode } from '../types';

interface Props {
  pipeline: Pipeline;
  selectedFile: string | null;
  onFileSelect: (path: string) => void;
}

export default function FileExplorerPanel({ pipeline, selectedFile, onFileSelect }: Props) {
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

  const renderNode = (node: FileNode, depth: number = 0): React.ReactNode => {
    const isDirectory = node.type === 'directory' || node.type === 'folder';
    const isExpanded = expandedPaths.has(node.path);
    const isSelected = selectedFile === node.path;
    const hasChildren = node.children && node.children.length > 0;

    return (
      <div key={node.path}>
        <div
          className={`flex items-center gap-2 px-3 py-2 cursor-pointer hover:bg-gray-100 ${
            isSelected ? 'bg-blue-50 text-blue-700' : 'text-gray-700'
          }`}
          style={{ paddingLeft: `${depth * 20 + 12}px` }}
          onClick={() => {
            if (isDirectory) {
              toggleExpand(node.path);
            } else {
              onFileSelect(node.path);
            }
          }}
        >
          {isDirectory && hasChildren && (
            <span className="material-symbols-rounded text-sm">
              {isExpanded ? 'expand_more' : 'chevron_right'}
            </span>
          )}
          {isDirectory && !hasChildren && (
            <span className="material-symbols-rounded text-sm text-gray-400">
              chevron_right
            </span>
          )}
          <span className={`material-symbols-rounded text-lg ${isSelected ? 'text-blue-600' : 'text-gray-500'}`}>
            {isDirectory ? 'folder' : 'description'}
          </span>
          <span className="text-sm flex-1 truncate">{node.name}</span>
          {node.file_count !== undefined && node.file_count > 0 && (
            <span className="text-xs text-gray-500">
              {Number(node.file_count || 0).toLocaleString()}
            </span>
          )}
        </div>
        {isDirectory && isExpanded && hasChildren && (
          <div>
            {node.children?.map(child => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="h-full">
      <div className="p-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center gap-2">
          <span className="material-symbols-rounded text-gray-600">folder_open</span>
          <h3 className="font-semibold text-gray-900">File Explorer</h3>
        </div>
        <p className="text-xs text-gray-600 mt-1">
          {Number(pipeline.metrics?.file_count || 0).toLocaleString()} files
        </p>
      </div>
      <div className="overflow-y-auto">
        {normalizedFiles.length > 0 ? (
          normalizedFiles.map(node => renderNode(node, 0))
        ) : (
          <div className="p-4 text-center text-gray-500 text-sm">
            No files available
          </div>
        )}
      </div>
    </div>
  );
}