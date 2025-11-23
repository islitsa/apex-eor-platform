import React from 'react';

interface Props {
  currentPage: number;
  rowsPerPage: number;
  totalRecords: number;
  onPageChange: (page: number) => void;
}

export default function PaginationControls({
  currentPage,
  rowsPerPage,
  totalRecords,
  onPageChange,
}: Props) {
  const startRow = (currentPage - 1) * rowsPerPage + 1;
  const endRow = Math.min(currentPage * rowsPerPage, totalRecords);
  const totalPages = Math.ceil(totalRecords / rowsPerPage);

  const canGoPrevious = currentPage > 1;
  const canGoNext = currentPage < totalPages;

  return (
    <div className="flex items-center justify-between">
      <div className="text-sm text-gray-600">
        Rows {startRow.toLocaleString()}-{endRow.toLocaleString()} of{' '}
        {totalRecords.toLocaleString()}
      </div>
      <div className="flex items-center gap-2">
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={!canGoPrevious}
          className={`flex items-center gap-1 px-4 h-9 rounded-lg border transition-colors ${
            canGoPrevious
              ? 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
              : 'bg-gray-100 border-gray-200 text-gray-400 cursor-not-allowed'
          }`}
        >
          <span className="material-symbols-rounded text-lg">arrow_back</span>
          <span className="text-sm font-medium">Previous</span>
        </button>
        <div className="px-4 text-sm font-medium text-gray-700">
          Page {currentPage} of {totalPages.toLocaleString()}
        </div>
        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={!canGoNext}
          className={`flex items-center gap-1 px-4 h-9 rounded-lg border transition-colors ${
            canGoNext
              ? 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
              : 'bg-gray-100 border-gray-200 text-gray-400 cursor-not-allowed'
          }`}
        >
          <span className="text-sm font-medium">Next</span>
          <span className="material-symbols-rounded text-lg">arrow_forward</span>
        </button>
      </div>
    </div>
  );
}