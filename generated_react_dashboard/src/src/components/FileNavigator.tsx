import React, { useState, useMemo } from 'react';
import type { Pipeline } from '../types.ts';

interface FileNavigatorProps {
  pipeline: Pipeline;
}

interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'folder';
  size?: string;
  children?: FileNode[];
}

export default function FileNavigator({ pipeline }: FileNavigatorProps) {
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set());
  const [searchTerm, setSearchTerm] = useState('');

  const fileTree = useMemo(() => {
    const buildTree = (obj: any, basePath = ''): FileNode[] => {
      if (!obj || typeof obj !== 'object') return [];

      return Object.entries(obj).map(([key, value]) => {
        const path = basePath ? `${basePath}/${key}` : key;
        
        if (value && typeof value === 'object' && !Array.isArray(value)) {
          // It's a folder
          return {
            name: key,
            path,
            type: 'folder' as const,
            children: buildTree(value, path)
          };
        } else {
          // It's a file
          return {
            name: key,
            path,
            type: 'file' as const,
            size: typeof value === 'string' ? value : undefined
          };
        }
      });
    };

    return buildTree(pipeline.files || {});
  }, [pipeline.files]);

  const filteredTree = useMemo(() => {
    if (!searchTerm) return fileTree;

    const filterNodes = (nodes: FileNode[]): FileNode[] => {
      return nodes.reduce((acc, node) => {
        if (node.name.toLowerCase().includes(searchTerm.toLowerCase())) {
          acc.push(node);
        } else if (node.children) {
          const filteredChildren = filterNodes(node.children);
          if (filteredChildren.length > 0) {
            acc.push({ ...node, children: filteredChildren });
          }
        }
        return acc;
      }, [] as FileNode[]);
    };

    return filterNodes(fileTree);
  }, [fileTree, searchTerm]);

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

  const renderNode = (node: FileNode, depth = 0) => {
    const isExpanded = expandedFolders.has(node.path);
    const hasChildren = node.children && node.children.length > 0;

    return (
      <div key={node.path}>
        <div
          className={`flex items-center py-2 px-3 hover:bg-gray-50 cursor-pointer rounded ${
            depth > 0 ? 'ml-' + (depth * 4) : ''
          }`}
          style={{ paddingLeft: `${depth * 1.5 + 0.75}rem` }}
          onClick={() => node.type === 'folder' && toggleFolder(node.path)}
        >
          {node.type === 'folder' ? (
            <>
              <span className="material-symbols-rounded text-gray-600 mr-2">
                {isExpanded ? 'folder_open' : 'folder'}
              </span>
              <span className="font-medium text-gray-900">{node.name}</span>
              {hasChildren && (
                <span className="ml-auto text-xs text-gray-500">
                  {node.children?.length} items
                </span>
              )}
            </>
          ) : (
            <>
              <span className="material-symbols-rounded text-gray-400 mr-2">description</span>
              <span className="text-gray-700">{node.name}</span>
              {node.size && (
                <span className="ml-auto text-xs text-gray-500">{node.size}</span>
              )}
            </>
          )}
        </div>
        
        {node.type === 'folder' && isExpanded && hasChildren && (
          <div>
            {node.children?.map(child => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  const totalFiles = useMemo(() => {
    const countFiles = (nodes: FileNode[]): number => {
      return nodes.reduce((count, node) => {
        if (node.type === 'file') return count + 1;
        if (node.children) return count + countFiles(node.children);
        return count;
      }, 0);
    };
    return countFiles(fileTree);
  }, [fileTree]);

  return (
    <div className="bg-white rounded-lg shadow-md">
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">File Navigator</h2>
            <p className="text-sm text-gray-500 mt-1">
              {pipeline.display_name || pipeline.name} • {totalFiles} files
            </p>
          </div>
          <button
            onClick={() => setExpandedFolders(new Set(fileTree.map(n => n.path)))}
            className="px-4 py-2 text-sm font-medium text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
          >
            Expand All
          </button>
        </div>
        
        <div className="relative">
          <span className="material-symbols-rounded absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
            search
          </span>
          <input
            type="text"
            placeholder="Search files and folders..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
      </div>

      <div className="p-4 max-h-[600px] overflow-y-auto">
        {filteredTree.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <span className="material-symbols-rounded text-4xl mb-2">folder_off</span>
            <p>No files found</p>
          </div>
        ) : (
          filteredTree.map(node => renderNode(node))
        )}
      </div>
    </div>
  );
}