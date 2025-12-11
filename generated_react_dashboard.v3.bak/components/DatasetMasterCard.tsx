import React, { useState, useMemo } from 'react';
import { Pipeline, FileNode } from '../types.ts';
import { FileExplorerTree } from './FileExplorerTree.tsx';
import { useFilePreview } from '../dataHooks.tsx';
import { DataPreviewTable } from './DataPreviewTable.tsx';
import { PaginationControls } from './PaginationControls.tsx';

interface DatasetMasterCardProps {
  pipeline: Pipeline;
}

export function DatasetMasterCard({ pipeline }: DatasetMasterCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 20;

  const { data: previewData, loading: previewLoading } = useFilePreview(
    pipeline.id,
    selectedFile,
    currentPage,
    pageSize
  );

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

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const handleFileSelect = (filePath: string) => {
    setSelectedFile(filePath);
    setCurrentPage(1);
  };

  return (
    <div className="flex-1 min-w-0">
      <div
        className="bg-white rounded-2xl shadow-md cursor-pointer transition-all"
        onClick={() => !isExpanded && setIsExpanded(true)}
      >
        <div className="p-6">
          <div className="flex items-center gap-3 mb-2">
            <span className="material-symbols-rounded text-3xl text-blue-600">science</span>
            <h2 className="text-2xl font-bold text-gray-900">{pipeline.display_name}</h2>
          </div>
          <p className="text-sm text-gray-600">
            {Number(pipeline.metrics?.file_count || 0).toLocaleString()} files •{' '}
            {Number(pipeline.metrics?.record_count || 0).toLocaleString()} records
          </p>
        </div>

        {isExpanded && (
          <div className="px-6 pb-6 border-t border-gray-200">
            <FileExplorerTree
              nodes={normalizedFiles}
              onFileSelect={handleFileSelect}
              selectedFile={selectedFile}
            />
          </div>
        )}
      </div>
    </div>
  );
}