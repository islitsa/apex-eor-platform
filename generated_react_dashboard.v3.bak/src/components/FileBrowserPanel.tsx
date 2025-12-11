import React, { useMemo } from 'react';
import type { Pipeline, FileNode } from '../types';

interface Props {
  pipeline: Pipeline;
  selectedFile: FileNode | null;
  onFileClick: (file: FileNode) => void;
}

export default function FileBrowserPanel({ pipeline, selectedFile, onFileClick }: Props) {
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

  const formatSize = (bytes?: number): string => {
    if (!bytes) return '';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
  };

  const renderNode = (node: FileNode, depth: number = 0): React.ReactNode => {
    const isDirectory = node.type === 'directory' || node.type === 'folder';
    const hasChildren = node.children && node.children.length > 0;
    const isSelected = selectedFile?.path === node.path;

    return (
      <div key={node.path}>
        <div
          onClick={() => onFileClick(node)}
          className={`flex items-center gap-3 h-12 px-4 cursor-pointer transition-all duration-150 hover:bg-blue-50 ${
            isSelected ? 'bg-blue-100' : ''
          }`}
          style={{ paddingLeft: `${depth * 24 + 16}px` }}
        >
          <span className="material-symbols-rounded text-gray-600 text-xl">
            {isDirectory ? 'folder' : 'description'}
          </span>
          <span className="flex-1 text-base font-medium text-gray-900">{node.name}</span>
          {node.size && (
            <span className="text-sm text-gray-500">{formatSize(node.size)}</span>
          )}
          {isDirectory && node.file_count !== undefined && (
            <span className="text-sm text-gray-500">{node.file_count} files</span>
          )}
        </div>
        {hasChildren && (
          <div>
            {node.children!.map(child => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Files</h3>
      </div>
      <div className="max-h-[600px] overflow-y-auto">
        {normalizedFiles.length > 0 ? (
          normalizedFiles.map(node => renderNode(node, 0))
        ) : (
          <div className="px-4 py-8 text-center text-gray-500">
            No files available
          </div>
        )}
      </div>
    </div>
  );
}