import React, { useState, useMemo } from 'react';

interface FileExplorerProps {
  files: Record<string, any>;
  pipelineName: string;
}

interface FileNode {
  name: string;
  type: 'file' | 'folder';
  size?: string;
  children?: FileNode[];
  path: string;
}

export default function FileExplorer({ files, pipelineName }: FileExplorerProps) {
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set());

  const fileTree = useMemo(() => {
    const buildTree = (obj: any, currentPath: string = ''): FileNode[] => {
      if (!obj || typeof obj !== 'object') return [];

      return Object.entries(obj).map(([key, value]) => {
        const path = currentPath ? `${currentPath}/${key}` : key;
        
        if (value && typeof value === 'object' && !Array.isArray(value)) {
          // It's a folder
          return {
            name: key,
            type: 'folder' as const,
            path,
            children: buildTree(value, path)
          };
        } else {
          // It's a file
          return {
            name: key,
            type: 'file' as const,
            path,
            size: typeof value === 'string' ? value : undefined
          };
        }
      });
    };

    return buildTree(files);
  }, [files]);

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

  const renderNode = (node: FileNode, depth: number = 0) => {
    const isExpanded = expandedFolders.has(node.path);
    const paddingLeft = depth * 24;

    if (node.type === 'folder') {
      return (
        <div key={node.path}>
          <div
            className="flex items-center gap-2 py-2 px-3 hover:bg-gray-100 cursor-pointer rounded-lg transition-colors"
            style={{ paddingLeft: `${paddingLeft + 12}px` }}
            onClick={() => toggleFolder(node.path)}
          >
            <span className={`material-symbols-rounded text-gray-600 transition-transform ${isExpanded ? 'rotate-90' : ''}`}>
              chevron_right
            </span>
            <span className="material-symbols-rounded text-blue-600">folder</span>
            <span className="font-medium text-gray-900">{node.name}</span>
            {node.children && (
              <span className="text-sm text-gray-500 ml-2">
                ({node.children.length} items)
              </span>
            )}
          </div>
          {isExpanded && node.children && (
            <div>
              {node.children.map(child => renderNode(child, depth + 1))}
            </div>
          )}
        </div>
      );
    } else {
      return (
        <div
          key={node.path}
          className="flex items-center gap-2 py-2 px-3 hover:bg-gray-50 rounded-lg transition-colors"
          style={{ paddingLeft: `${paddingLeft + 12}px` }}
        >
          <span className="material-symbols-rounded text-gray-400 ml-6">description</span>
          <span className="text-gray-700">{node.name}</span>
          {node.size && (
            <span className="text-sm text-gray-500 ml-auto">{node.size}</span>
          )}
        </div>
      );
    }
  };

  if (!fileTree || fileTree.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <span className="material-symbols-rounded text-4xl mb-2">folder_off</span>
        <p>No files found</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
      {fileTree.map(node => renderNode(node, 0))}
    </div>
  );
}