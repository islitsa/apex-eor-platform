import { useMemo, useCallback } from 'react';

interface PaginationControlsProps {
  currentPage: number;
  totalRows: number;
  pageSize: number;
  onPageChange: (page: number) => void;
}

function PaginationControls({
  currentPage,
  totalRows,
  pageSize,
  onPageChange,
}: PaginationControlsProps) {
  const totalPages = useMemo(() => {
    return Math.ceil(Number(totalRows || 0) / Number(pageSize || 1));
  }, [totalRows, pageSize]);

  const canGoPrevious = useMemo(() => {
    return currentPage > 1;
  }, [currentPage]);

  const canGoNext = useMemo(() => {
    return currentPage < totalPages;
  }, [currentPage, totalPages]);

  const handlePrevious = useCallback(() => {
    if (canGoPrevious) {
      onPageChange(currentPage - 1);
    }
  }, [canGoPrevious, currentPage, onPageChange]);

  const handleNext = useCallback(() => {
    if (canGoNext) {
      onPageChange(currentPage + 1);
    }
  }, [canGoNext, currentPage, onPageChange]);

  const pageNumbers = useMemo(() => {
    const pages: number[] = [];
    const maxVisible = 5;
    let start = Math.max(1, currentPage - Math.floor(maxVisible / 2));
    let end = Math.min(totalPages, start + maxVisible - 1);
    
    if (end - start < maxVisible - 1) {
      start = Math.max(1, end - maxVisible + 1);
    }

    for (let i = start; i <= end; i++) {
      pages.push(i);
    }
    return pages;
  }, [currentPage, totalPages]);

  if (totalPages <= 1) {
    return null;
  }

  return (
    <div className="flex items-center justify-center gap-2 mt-6">
      <button
        onClick={handlePrevious}
        disabled={!canGoPrevious}
        className={`h-9 px-4 rounded-lg flex items-center gap-1 ${
          canGoPrevious
            ? 'bg-blue-600 text-white hover:bg-blue-700'
            : 'bg-gray-200 text-gray-400 cursor-not-allowed'
        }`}
      >
        <span className="material-symbols-rounded text-lg">arrow_back</span>
        Previous
      </button>

      <div className="flex items-center gap-1">
        {pageNumbers.map((page: number) => (
          <button
            key={page}
            onClick={() => onPageChange(page)}
            className={`h-9 w-9 rounded-lg ${
              page === currentPage
                ? 'bg-blue-600 text-white font-bold'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {page}
          </button>
        ))}
      </div>

      <button
        onClick={handleNext}
        disabled={!canGoNext}
        className={`h-9 px-4 rounded-lg flex items-center gap-1 ${
          canGoNext
            ? 'bg-blue-600 text-white hover:bg-blue-700'
            : 'bg-gray-200 text-gray-400 cursor-not-allowed'
        }`}
      >
        Next
        <span className="material-symbols-rounded text-lg">arrow_forward</span>
      </button>
    </div>
  );
}

export { PaginationControls };
export default PaginationControls;