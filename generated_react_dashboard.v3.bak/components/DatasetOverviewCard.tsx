import { useState, useMemo, useCallback } from 'react';
import { Pipeline, FileNode } from '../types.ts';
import { useFilePreview } from '../dataHooks.tsx';
import DatasetOverviewPanel from './DatasetOverviewPanel.tsx';
import FileExplorerTree from './FileExplorerTree.tsx';
import DataPreviewTable from './DataPreviewTable.tsx';
import PaginationControls from './PaginationControls.tsx';

interface DatasetOverviewCardProps {
  pipeline: Pipeline;
}

function DatasetOverviewCard({ pipeline }: DatasetOverviewCardProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 20;

  const normalizeNode = useCallback((node: any): FileNode => {
    let children: FileNode[] = [];
    if (node.children) {
      children = node.children.map(normalizeNode);
    } else {
      if (node.subdirs) {
        Object.values(node.subdirs).forEach((d: any) => {
          children.push(normalizeNode(d));
        });
      }
      if (node.files) {
        node.files.forEach((f: any) => {
          children.push({
            ...f,
            type: 'file',
            children: [],
          });
        });
      }
    }
    return {
      name: node.name,
      path: node.path,
      type: node.type === 'folder' ? 'directory' : (node.type || 'directory'),
      children,
      file_count: node.file_count,
      size: node.size_bytes || node.size,
    };
  }, []);

  const normalizedFiles = useMemo(() => {
    if (!pipeline?.files) return [];
    return pipeline.files.map(normalizeNode);
  }, [pipeline, normalizeNode]);

  const { data: previewData, loading: previewLoading, error: previewError } = useFilePreview(
    pipeline.id,
    selectedFile,
    currentPage,
    pageSize
  );

  const handleToggle = useCallback(() => {
    setIsExpanded((prev: boolean) => !prev);
  }, []);

  const handleFileSelect = useCallback((filePath: string) => {
    setSelectedFile(filePath);
    setCurrentPage(1);
  }, []);

  const handlePageChange = useCallback((page: number) => {
    setCurrentPage(page);
  }, []);

  return (
    <div className="space-y-6">
      <DatasetOverviewPanel
        pipeline={pipeline}
        isExpanded={isExpanded}
        onToggle={handleToggle}
      />

      {isExpanded && (
        <>
          <FileExplorerTree
            nodes={normalizedFiles}
            onFileSelect={handleFileSelect}
            selectedFile={selectedFile}
          />

          {selectedFile && (
            <>
              {previewError && (
                <div className="bg-red-50 border border-red-200 rounded-2xl p-6">
                  <p className="text-red-700">Error loading preview: {previewError.message}</p>
                </div>
              )}

              {!previewError && previewData && (
                <>
                  <DataPreviewTable
                    columns={previewData.columns}
                    rows={previewData.rows}
                    loading={previewLoading}
                  />
                  <PaginationControls
                    currentPage={currentPage}
                    totalRows={previewData.totalRows}
                    pageSize={pageSize}
                    onPageChange={handlePageChange}
                  />
                </>
              )}

              {!previewError && !previewData && previewLoading && (
                <DataPreviewTable columns={[]} rows={[]} loading={true} />
              )}
            </>
          )}
        </>
      )}
    </div>
  );
}

export { DatasetOverviewCard };
export default DatasetOverviewCard;