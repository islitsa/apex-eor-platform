import React, { useState } from 'react';
import type { Pipeline, FileNode } from '../types';

interface Props {
  pipeline: Pipeline;
  onSelectFile: (filePath: string | null) => void;
}

export default function FileBrowserList({ pipeline, onSelectFile }: Props) {
  const [expandedPaths, setExpandedPaths] = useState<Set<string>>(new Set());
  const [selectedPath, setSelectedPath] = useState<string | null>(null);

  const normalizeNode = (node: any): FileNode => {
    let children: FileNode[] = [];

    if (node.files && Array.isArray(node.files)) {
      children = node.files.map((child: any) => normalizeNode(child));
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

  const handleFileClick = (node: FileNode) => {
    if (node.type === 'file') {
      setSelectedPath(node.path);
      onSelectFile(node.path);
    } else {
      toggleExpand(node.path);
    }
  };

  const formatSize = (bytes: number | undefined): string => {
    if (!bytes) return '';
    const mb = bytes / (1024 * 1024);
    if (mb < 1) return `${(bytes / 1024).toFixed(1)} KB`;
    if (mb < 1024) return `${mb.toFixed(1)} MB`;
    return `${(mb / 1024).toFixed(2)} GB`;
  };

  const renderNode = (node: FileNode, depth: number = 0) => {
    const isExpanded = expandedPaths.has(node.path);
    const isSelected = selectedPath === node.path;
    const isDirectory = node.type === 'directory' || node.type === 'folder';
    const hasChildren = node.files && node.files.length > 0;

    return (
      <div key={node.path}>
        <div
          className={`flex items-center gap-2 h-10 px-4 cursor-pointer hover:bg-gray-100 transition-colors ${
            isSelected ? 'bg-blue-50 border-l-4 border-blue-500' : ''
          }`}
          style={{ paddingLeft: `${depth * 16 + 16}px` }}
          onClick={() => handleFileClick(node)}
        >
          {isDirectory && hasChildren && (
            <span className="material-symbols-rounded text-gray-400 text-xl">
              {isExpanded ? 'expand_more' : 'chevron_right'}
            </span>
          )}
          {isDirectory && !hasChildren && (
            <span className="w-5"></span>
          )}
          <span className="material-symbols-rounded text-gray-500 text-xl">
            {isDirectory ? 'folder' : 'description'}
          </span>
          <span className="text-sm font-medium text-gray-900 flex-1">
            {String(node.name || '')}
          </span>
          {node.file_count !== undefined && node.file_count > 0 && (
            <span className="text-xs text-gray-500">
              {Number(node.file_count || 0).toLocaleString()} files
            </span>
          )}
          {node.size && (
            <span className="text-xs text-gray-500">
              {formatSize(node.size)}
            </span>
          )}
        </div>
        {isDirectory && isExpanded && hasChildren && (
          <div>
            {node.files!.map(child => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  if (!pipeline.files || pipeline.files.length === 0) {
    return (
      <div className="p-6 text-center text-gray-500">
        <span className="material-symbols-rounded text-4xl mb-2">folder_off</span>
        <p>No files available</p>
      </div>
    );
  }

  const normalizedFiles = pipeline.files.map(node => normalizeNode(node));

  return (
    <div className="max-h-96 overflow-y-auto">
      {normalizedFiles.map(node => renderNode(node, 0))}
    </div>
  );
}