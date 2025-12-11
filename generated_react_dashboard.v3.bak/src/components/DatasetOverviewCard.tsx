import React, { useState, useMemo } from 'react';
import { Pipeline, FileNode } from '../types.ts';
import FileExplorerTree from './FileExplorerTree.tsx';
import DataPreviewTable from './DataPreviewTable.tsx';
import { useFilePreview } from '../dataHooks.tsx';

interface DatasetOverviewCardProps {
  pipeline: Pipeline;
}

function DatasetOverviewCard({ pipeline }: DatasetOverviewCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 20;

  const { data: previewData, loading: previewLoading, error: previewError } = useFilePreview(
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
        Object.values(node.subdirs).forEach(d => children.push(normalizeNode(d)));
      }
      if (node.files) {
        node.files.forEach((f: any) => children.push({
          ...f,
          type: 'file',
          children: []
        }));
      }
    }
    return {
      name: node.name,
      path: node.path,
      type: node.type === 'folder' ? 'directory' : (node.type || 'directory'),
      children,
      file_count: node.file_count,
      size: node.size_bytes || node.size
    };
  };

  const normalizedFiles = useMemo(() => {
    return pipeline.files?.map(normalizeNode) ?? [];
  }, [pipeline.files]);

  const handleFileSelect = (filePath: string) => {
    setSelectedFile(filePath);
    setCurrentPage(1);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const formatNumber = (num: number | undefined | null): string => {
    if (num === undefined || num === null) return '0';
    return Number(num).toLocaleString();
  };

  const formatBytes = (bytes: number | undefined | null): string => {
    if (!bytes) return '0 B';
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${sizes[i]}`;
  };

  return (
    <div
      className="bg-white rounded-3xl shadow-lg overflow-hidden transition-all duration-300"
      style={{ width: '800px', margin: '0 auto' }}
    >
      {/* Card Header */}
      <div
        className="p-6 cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="material-symbols-rounded text-primary text-4xl">science</span>
            <div>
              <h2 className="text-3xl font-bold text-gray-900">{pipeline.display_name}</h2>
              <p className="text-sm text-gray-500 mt-1">{pipeline.id}</p>
            </div>
          </div>
          <span className={`material-symbols-rounded text-gray-400 transition-transform duration-300 ${isExpanded ? 'rotate-180' : ''}`}>
            expand_more
          </span>
        </div>

        {/* Metrics Summary */}
        <div className="grid grid-cols-3 gap-4 mt-6">
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="text-sm text-gray-600">Files</div>
            <div className="text-2xl font-semibold text-gray-900 mt-1">
              {formatNumber(pipeline.metrics?.file_count)}
            </div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="text-sm text-gray-600">Records</div>
            <div className="text-2xl font-semibold text-gray-900 mt-1">
              {formatNumber(pipeline.metrics?.record_count)}
            </div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="text-sm text-gray-600">Size</div>
            <div className="text-2xl font-semibold text-gray-900 mt-1">
              {formatBytes(pipeline.metrics?.data_size)}
            </div>
          </div>
        </div>

        {/* Status Badge */}
        <div className="mt-4">
          <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium ${
            pipeline.status === 'processed' ? 'bg-green-100 text-green-800' :
            pipeline.status === 'processing' ? 'bg-blue-100 text-blue-800' :
            'bg-gray-100 text-gray-800'
          }`}>
            <span className="material-symbols-rounded text-base">
              {pipeline.status === 'processed' ? 'check_circle' : 'pending'}
            </span>
            {String(pipeline.status || 'unknown').toUpperCase()}
          </span>
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="border-t border-gray-200">
          <div className="grid grid-cols-2 divide-x divide-gray-200">
            {/* File Explorer */}
            <div className="p-6 overflow-y-auto" style={{ maxHeight: '600px' }}>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Files</h3>
              {normalizedFiles.length > 0 ? (
                <FileExplorerTree
                  nodes={normalizedFiles}
                  onFileSelect={handleFileSelect}
                  selectedFile={selectedFile}
                />
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <span className="material-symbols-rounded text-4xl">folder_off</span>
                  <p className="mt-2">No files available</p>
                </div>
              )}
            </div>

            {/* Data Preview */}
            <div className="p-6 overflow-y-auto" style={{ maxHeight: '600px' }}>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Preview</h3>
              {!selectedFile && (
                <div className="text-center py-12 text-gray-500">
                  <span className="material-symbols-rounded text-4xl">description</span>
                  <p className="mt-2">Select a file to preview</p>
                </div>
              )}
              {selectedFile && (
                <DataPreviewTable
                  data={previewData}
                  loading={previewLoading}
                  error={previewError}
                  currentPage={currentPage}
                  pageSize={pageSize}
                  onPageChange={handlePageChange}
                />
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default DatasetOverviewCard;