import React, { useState } from 'react';
import { Pipeline, FileNode } from '../types';

interface Props {
  pipeline: Pipeline;
  selectedFile: string | null;
  onFileSelect: (path: string | null) => void;
}

export default function FileExplorerPanel({ pipeline, selectedFile, onFileSelect }: Props) {
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set());

  const normalizeNode = (node: any): FileNode => {
    let children: FileNode[] = [];

    // Handle NEW API format (children array already present)
    if (node.children && Array.isArray(node.children)) {
      children = node.children.map((child: any) => normalizeNode(child));
    }
    // Handle OLD format (files/subdirs)
    else {
      if (node.subdirs && typeof node.subdirs === 'object') {
        Object.values(node.subdirs).forEach((subdir: any) => {
          children.push(normalizeNode(subdir));
        });
      }
      if (node.files && Array.isArray(node.files)) {
        node.files.forEach((file: any) => {
          children.push(normalizeNode(file));
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

  const toggleFolder = (path: string) => {
    const newExpanded = new Set(expandedFolders);
    if (newExpanded.has(path)) {
      newExpanded.delete(path);
    } else {
      newExpanded.add(path);
    }
    setExpandedFolders(newExpanded);
  };

  const formatFileSize = (bytes: number | undefined) => {
    if (!bytes) return '';
    const mb = bytes / (1024 * 1024);
    if (mb < 1) return `${(bytes / 1024).toFixed(1)} KB`;
    if (mb < 1024) return `${mb.toFixed(1)} MB`;
    return `${(mb / 1024).toFixed(2)} GB`;
  };

  const renderNode = (node: FileNode, depth: number = 0) => {
    const isDirectory = node.type === 'directory' || node.type === 'folder';
    const isExpanded = expandedFolders.has(node.path);
    const isSelected = selectedFile === node.path;
    const hasChildren = node.children && node.children.length > 0;

    return (
      <div key={node.path}>
        <div
          className={`flex items-center gap-2 py-2 px-3 rounded cursor-pointer transition-colors ${
            isSelected ? 'bg-blue-100 text-blue-900' : 'hover:bg-gray-100'
          }`}
          style={{ 
            paddingLeft: `${depth * 24 + 12}px`,
            height: '48px'
          }}
          onClick={() => {
            if (isDirectory) {
              toggleFolder(node.path);
            } else {
              onFileSelect(node.path);
            }
          }}
        >
          {isDirectory && hasChildren && (
            <span className="material-symbols-rounded text-gray-400 text-sm">
              {isExpanded ? 'expand_more' : 'chevron_right'}
            </span>
          )}
          {isDirectory && !hasChildren && (
            <span className="w-5"></span>
          )}
          
          <span className="material-symbols-rounded text-gray-600">
            {isDirectory ? 'folder' : 'description'}
          </span>
          
          <span className="flex-1 text-sm font-medium text-gray-900">{node.name}</span>
          
          {node.file_count !== undefined && node.file_count > 0 && (
            <span className="text-xs text-gray-500">{node.file_count} files</span>
          )}
          
          {node.size && (
            <span className="text-xs text-gray-500 flex items-center gap-1">
              <span className="material-symbols-rounded text-xs">storage</span>
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

  const normalizedFiles = pipeline.files?.map(node => normalizeNode(node)) || [];

  return (
    <div className="bg-white rounded-lg border border-gray-200">
      <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
        <h3 className="font-bold text-gray-900 flex items-center gap-2">
          <span className="material-symbols-rounded text-blue-600">folder_open</span>
          File Explorer
        </h3>
      </div>
      
      <div className="max-h-96 overflow-y-auto">
        {normalizedFiles.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <span className="material-symbols-rounded text-4xl mb-2">folder_off</span>
            <p>No files available</p>
          </div>
        ) : (
          normalizedFiles.map(node => renderNode(node, 0))
        )}
      </div>
    </div>
  );
}