import { useState } from 'react';
import { useFilePreview } from '../dataHooks';
import DataTablePreview from './DataTablePreview';
import PaginationControls from './PaginationControls';

interface Props {
  pipelineId: string | null;
  filePath: string | null;
}

export default function FilePreviewPanel({ pipelineId, filePath }: Props) {
  const [currentPage, setCurrentPage] = useState(1);
  const rowsPerPage = 10;

  const { data, loading, error } = useFilePreview(pipelineId, filePath, currentPage, rowsPerPage);

  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage);
  };

  if (!filePath) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 sticky top-8" style={{ width: '400px' }}>
        <div className="flex flex-col items-center justify-center text-center py-12">
          <span className="material-symbols-rounded text-gray-300" style={{ fontSize: '64px' }}>
            preview
          </span>
          <p className="mt-4 text-gray-500 text-sm">
            Select a file to preview its contents
          </p>
        </div>
      </div>
    );
  }

  const fileName = filePath.split('/').pop() || 'Unknown';
  const totalPages = data ? Math.ceil(data.totalRows / rowsPerPage) : 0;

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden sticky top-8" style={{ width: '400px' }}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center gap-2 mb-2">
          <span className="material-symbols-rounded text-blue-600" style={{ fontSize: '20px' }}>
            description
          </span>
          <h3 className="font-semibold text-gray-900 text-sm truncate" title={fileName}>
            {fileName}
          </h3>
        </div>
        {data && (
          <p className="text-xs text-gray-600">
            {Number(data.totalRows || 0).toLocaleString()} total rows
          </p>
        )}
      </div>

      {/* Content */}
      <div className="p-4">
        {loading && (
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              </div>
            ))}
          </div>
        )}

        {error && (
          <div className="text-center py-8">
            <span className="material-symbols-rounded text-red-400" style={{ fontSize: '48px' }}>
              error
            </span>
            <p className="mt-2 text-red-600 text-sm">Error loading preview</p>
            <p className="text-xs text-gray-500 mt-1">{error.message}</p>
          </div>
        )}

        {!loading && !error && data && (
          <>
            <DataTablePreview data={data} />
            {totalPages > 1 && (
              <div className="mt-4">
                <PaginationControls
                  currentPage={currentPage}
                  totalPages={totalPages}
                  onPageChange={handlePageChange}
                />
              </div>
            )}
          </>
        )}

        {!loading && !error && !data && (
          <div className="text-center py-8 text-gray-500">
            <span className="material-symbols-rounded text-gray-300" style={{ fontSize: '48px' }}>
              inbox
            </span>
            <p className="mt-2 text-sm">No preview available</p>
          </div>
        )}
      </div>
    </div>
  );
}