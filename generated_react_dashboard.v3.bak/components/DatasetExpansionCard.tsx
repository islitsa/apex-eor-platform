import React, { useState, useMemo } from 'react';
import { Pipeline, FileNode } from '../types.ts';
import { FileTreeNavigator } from './FileTreeNavigator.tsx';

interface DatasetExpansionCardProps {
  pipeline: Pipeline;
  onFileSelect?: (pipelineId: string, filePath: string) => void;
  selectedFile?: string | null;
}

export function DatasetExpansionCard({ pipeline, onFileSelect, selectedFile }: DatasetExpansionCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const normalizeNode = (node: any): FileNode => {
    let children: FileNode[] = [];
    if (node.children) {
      children = node.children.map(normalizeNode);
    } else {
      if (node.subdirs) {
        Object.values(node.subdirs).forEach((d) => children.push(normalizeNode(d)));
      }
      if (node.files) {
        node.files.forEach((f: any) =>
          children.push({ ...f, type: 'file', children: [] })
        );
      }
    }
    return {
      name: node.name,
      path: node.path,
      type: node.type === 'folder' ? 'directory' : node.type || 'directory',
      children,
      file_count: node.file_count,
      size: node.size_bytes || node.size,
    };
  };

  const normalizedFiles = useMemo(() => {
    return (pipeline.files ?? []).map(normalizeNode);
  }, [pipeline.files]);

  const handleFileSelect = (filePath: string) => {
    if (onFileSelect) {
      onFileSelect(pipeline.id, filePath);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div
        className="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-3">
          <span className="material-symbols-rounded text-blue-600 text-[24px]">
            science
          </span>
          <h3 className="text-xl font-bold text-gray-900">
            {pipeline.display_name || pipeline.name}
          </h3>
          <span className="material-symbols-rounded text-gray-400 ml-auto text-[24px]">
            {isExpanded ? 'expand_less' : 'expand_more'}
          </span>
        </div>
      </div>

      {isExpanded && (
        <div className="border-t border-gray-200 p-4">
          <FileTreeNavigator
            nodes={normalizedFiles}
            onFileSelect={handleFileSelect}
            selectedFile={selectedFile}
          />
        </div>
      )}
    </div>
  );
}