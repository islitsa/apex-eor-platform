import React, { useState } from 'react';
import { Pipeline } from '../types.ts';
import { useFilePreview } from '../dataHooks.tsx';
import { DataPreviewTable } from './DataPreviewTable.tsx';
import { PaginationControls } from './PaginationControls.tsx';

interface DataPreviewPanelProps {
  pipeline: Pipeline | null;
  selectedFile: string | null;
}

export function DataPreviewPanel({ pipeline, selectedFile }: DataPreviewPanelProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 20;

  const { data, loading, error } = useFilePreview(
    pipeline?.id ?? null,
    selectedFile,
    currentPage,
    pageSize
  );

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  return (
    <div className="w-[500px] flex-shrink-0 bg-white rounded-2xl shadow-md p-6">
      <h3 className="text-lg font-bold text-gray-900 mb-4">Data Preview</h3>
      {!selectedFile && (
        <div className="flex items-center justify-center h-64 text-gray-500">
          Select a file to preview
        </div>
      )}
      {selectedFile && error && (
        <div className="flex items-center justify-center h-64 text-red-600">
          Error loading preview: {error.message}
        </div>
      )}
      {selectedFile && !error && (
        <>
          <DataPreviewTable
            columns={data?.columns ?? []}
            rows={data?.rows ?? []}
            loading={loading}
          />
          {data && data.totalRows > 0 && (
            <PaginationControls
              currentPage={currentPage}
              totalRows={data.totalRows}
              pageSize={pageSize}
              onPageChange={handlePageChange}
            />
          )}
        </>
      )}
    </div>
  );
}