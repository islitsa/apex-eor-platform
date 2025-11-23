import React, { useState, useMemo } from 'react';
import type { Pipeline } from '../types';

interface ProductionFilesTreeProps {
  pipeline: Pipeline;
}

interface TreeNode {
  name: string;
  type: 'folder' | 'file';
  children?: TreeNode[];
  file?: {
    path: string;
    size_bytes?: number;
    record_count?: number;
  };
}

export default function ProductionFilesTree({ pipeline }: ProductionFilesTreeProps) {
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set());

  const fileTree = useMemo(() => {
    const root: TreeNode = { name: 'root', type: 'folder', children: [] };

    // Build tree from stages
    if (pipeline.stages && Array.isArray(pipeline.stages)) {
      pipeline.stages.forEach(stage => {
        if (stage && typeof stage === 'object' && stage.name) {
          const stageName = String(stage.name || '');
          const stageNode: TreeNode = {
            name: stageName,
            type: 'folder',
            children: []
          };
          root.children?.push(stageNode);
        }
      });
    }

    // Add files to tree
    if (pipeline.files && Array.isArray(pipeline.files)) {
      pipeline.files.forEach(file => {
        if (file && typeof file === 'object' && file.path) {
          const pathParts = String(file.path).split('/');
          let currentNode = root;

          pathParts.forEach((part, index) => {
            if (!part) return;

            const isLastPart = index === pathParts.length - 1;
            const existingChild = currentNode.children?.find(child => child.name === part);

            if (existingChild) {
              currentNode = existingChild;
            } else {
              const newNode: TreeNode = {
                name: part,
                type: isLastPart ? 'file' : 'folder',
                children: isLastPart ? undefined : [],
                file: isLastPart ? file : undefined
              };
              currentNode.children?.push(newNode);
              currentNode = newNode;
            }
          });
        }
      });
    }

    return root.children || [];
  }, [pipeline]);

  const toggleFolder = (path: string, e: React.MouseEvent) => {
    e.stopPropagation();
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

  const formatSize = (bytes: number | undefined): string => {
    const num = Number(bytes || 0);
    if (num === 0) return '';
    const mb = num / (1024 * 1024);
    if (mb >= 1) {
      return `${mb.toFixed(2)} MB`;
    }
    const kb = num / 1024;
    return `${kb.toFixed(2)} KB`;
  };

  const formatRecords = (count: number | undefined): string => {
    const num = Number(count || 0);
    if (num === 0) return '';
    return `${num.toLocaleString()} records`;
  };

  const renderNode = (node: TreeNode, depth: number, path: string) => {
    const isExpanded = expandedFolders.has(path);
    const hasChildren = node.children && node.children.length > 0;

    return (
      <div key={path}>
        <div
          className="flex items-center gap-2 py-2 px-3 hover:bg-blue-50 hover:border-l-4 hover:border-blue-600 transition-all duration-150 cursor-pointer group"
          style={{ paddingLeft: `${depth * 20 + 12}px` }}
          onClick={(e) => node.type === 'folder' ? toggleFolder(path, e) : undefined}
        >
          {node.type === 'folder' && hasChildren && (
            <span className="material-symbols-rounded text-gray-600 text-sm transition-transform duration-200">
              {isExpanded ? 'expand_more' : 'chevron_right'}
            </span>
          )}
          {node.type === 'folder' && !hasChildren && (
            <span className="material-symbols-rounded text-gray-400 text-sm">folder</span>
          )}
          {node.type === 'file' && (
            <span className="material-symbols-rounded text-blue-600 text-sm">description</span>
          )}
          
          <span className="text-sm text-gray-900 font-medium flex-1">{node.name}</span>
          
          {node.file && (
            <div className="flex items-center gap-3 text-xs text-gray-500">
              {formatRecords(node.file.record_count) && (
                <span>{formatRecords(node.file.record_count)}</span>
              )}
              {formatSize(node.file.size_bytes) && (
                <span>{formatSize(node.file.size_bytes)}</span>
              )}
            </div>
          )}
        </div>

        {node.type === 'folder' && isExpanded && hasChildren && (
          <div>
            {node.children?.map((child, index) =>
              renderNode(child, depth + 1, `${path}/${child.name}`)
            )}
          </div>
        )}
      </div>
    );
  };

  if (fileTree.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <span className="material-symbols-rounded text-4xl mb-2">folder_off</span>
        <p className="text-sm">No files available</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 rounded-lg border border-gray-200 overflow-hidden">
      <div className="bg-gray-100 px-4 py-2 border-b border-gray-200">
        <h4 className="text-sm font-bold text-gray-700 flex items-center gap-2">
          <span className="material-symbols-rounded text-sm">folder_open</span>
          File Structure
        </h4>
      </div>
      <div className="max-h-[400px] overflow-y-auto">
        {fileTree.map((node, index) => renderNode(node, 0, node.name))}
      </div>
    </div>
  );
}