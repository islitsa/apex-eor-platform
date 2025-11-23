import React, { useState, useMemo } from 'react';
import type { Pipeline, FileNode } from '../types';

interface ExpandableFileExplorerProps {
  pipeline: Pipeline;
}

interface TreeNodeProps {
  node: FileNode;
  level: number;
  index: number;
}

function TreeNode({ node, level, index }: TreeNodeProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const hasChildren = node.children && node.children.length > 0;

  const formatSize = (bytes?: number): string => {
    if (!bytes) return '';
    const mb = bytes / (1024 ** 2);
    if (mb < 1) return `${(bytes / 1024).toFixed(1)} KB`;
    if (mb < 1024) return `${mb.toFixed(1)} MB`;
    return `${(mb / 1024).toFixed(2)} GB`;
  };

  return (
    <>
      <div
        className={`flex items-center h-12 px-4 hover:bg-blue-50 cursor-pointer transition-colors ${
          level % 2 === 0 ? 'bg-gray-50' : 'bg-white'
        }`}
        style={{ paddingLeft: `${level * 24 + 16}px` }}
        onClick={() => hasChildren && setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2 flex-1">
          {hasChildren ? (
            <span className="material-symbols-rounded text-gray-600 text-xl">
              {isExpanded ? 'expand_more' : 'chevron_right'}
            </span>
          ) : (
            <span className="material-symbols-rounded text-gray-400 text-xl">description</span>
          )}
          <span className="font-medium text-gray-900">{String(node.name || '')}</span>
        </div>
        {node.size && (
          <span className="text-sm text-gray-500">{formatSize(node.size)}</span>
        )}
      </div>
      {isExpanded && hasChildren && (
        <div className="transition-all duration-200">
          {node.children?.map((child, idx) => (
            <TreeNode key={`${level}-${index}-${idx}`} node={child} level={level + 1} index={idx} />
          ))}
        </div>
      )}
    </>
  );
}

export default function ExpandableFileExplorer({ pipeline }: ExpandableFileExplorerProps) {
  const fileTree = useMemo(() => {
    if (!pipeline.files || !Array.isArray(pipeline.files)) {
      return [];
    }
    return pipeline.files;
  }, [pipeline.files]);

  if (fileTree.length === 0) {
    return (
      <div className="text-center py-12">
        <span className="material-symbols-rounded text-gray-300 text-5xl mb-3">folder_open</span>
        <p className="text-gray-500">No files available</p>
      </div>
    );
  }

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <div className="bg-gray-100 px-4 py-3 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <span className="material-symbols-rounded text-gray-700">folder</span>
          <span className="font-semibold text-gray-900">File Structure</span>
        </div>
      </div>
      <div className="max-h-[500px] overflow-y-auto">
        {fileTree.map((node, idx) => (
          <TreeNode key={`root-${idx}`} node={node} level={0} index={idx} />
        ))}
      </div>
    </div>
  );
}