import React, { useState, useMemo } from 'react';
import type { Pipeline, FileNode } from '../types';

interface Props {
  pipeline: Pipeline;
  onFileSelect: (filePath: string) => void;
  selectedFilePath: string | null;
}

export default function FileTreeNavigation({ pipeline, onFileSelect, selectedFilePath }: Props) {
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set());

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

  const toggleFolder = (path: string) => {
    setExpandedFolders(prev => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return next;
    });
  };

  const renderNode = (node: FileNode, depth: number = 0): React.ReactNode => {
    const isDirectory = node.type === 'directory' || node.type === 'folder';
    const isExpanded = expandedFolders.has(node.path);
    const isSelected = selectedFilePath === node.path;
    const hasChildren = node.children && node.children.length > 0;

    return (
      <div key={node.path}>
        <div
          className={`flex items-center gap-2 py-2 px-3 rounded cursor-pointer hover:bg-gray-100 transition-colors ${
            isSelected ? 'bg-blue-50 text-blue-700' : 'text-gray-700'
          }`}
          style={{ paddingLeft: `${depth * 24 + 12}px` }}
          onClick={() => {
            if (isDirectory) {
              toggleFolder(node.path);
            } else {
              onFileSelect(node.path);
            }
          }}
        >
          {isDirectory && (
            <span
              className={`material-symbols-rounded text-gray-400 transition-transform duration-200 ${
                isExpanded ? 'rotate-90' : ''
              }`}
              style={{ fontSize: '18px' }}
            >
              chevron_right
            </span>
          )}
          {!isDirectory && <div style={{ width: '18px' }} />}
          
          <span className="material-symbols-rounded text-gray-500" style={{ fontSize: '20px' }}>
            {isDirectory ? (isExpanded ? 'folder_open' : 'folder') : 'description'}
          </span>
          
          <span className="text-sm flex-1">{node.name}</span>
          
          {isDirectory && node.file_count !== undefined && (
            <span className="text-xs text-gray-500">
              {Number(node.file_count || 0).toLocaleString()} files
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
      <div className="text-center py-8 text-gray-500">
        <span className="material-symbols-rounded text-gray-300" style={{ fontSize: '48px' }}>
          folder_off
        </span>
        <p className="mt-2">No files found</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <div className="max-h-96 overflow-y-auto">
        {normalizedFiles.map(node => renderNode(node, 0))}
      </div>
    </div>
  );
}