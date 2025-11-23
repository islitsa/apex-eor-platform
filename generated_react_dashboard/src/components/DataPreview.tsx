import React, { useState, useEffect } from 'react';
import { useDataSource } from '../dataHooks';
import type { DataRecord } from '../types';

interface DataPreviewProps {
  pipelineName: string;
  selectedFile: string | null;
}

export default function DataPreview({ pipelineName, selectedFile }: DataPreviewProps) {
  const [page, setPage] = useState(0);
  const pageSize = 100;
  const offset = page * pageSize;

  const { data, total, loading, error } = useDataSource(pipelineName, {
    limit: pageSize,
    offset: offset
  });

  useEffect(() => {
    setPage(0);
  }, [pipelineName, selectedFile]);

  const totalPages = Math.ceil((total || 0) / pageSize);
  const columns = data && data.length > 0 ? Object.keys(data[0]) : [];

  const handlePrevious = () => {
    if (page > 0) setPage(page - 1);
  };

  const handleNext = () => {
    if (page < totalPages - 1) setPage(page + 1);
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 h-full flex flex-col">
      <div className="p-4 border-b border-gray-200">
        <h4 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
          <span className="material-symbols-rounded text-base">table_chart</span>
          Data Preview
          {total !== undefined && (
            <span className="text-gray-500 font-normal">
              ({total.toLocaleString()} total records)
            </span>
          )}
        </h4>
      </div>

      <div className="flex-1 overflow-auto">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-2"></div>
              <p className="text-sm text-gray-600">Loading data...</p>
            </div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center text-red-600">
              <span className="material-symbols-rounded text-4xl mb-2">error</span>
              <p className="text-sm">{error}</p>
            </div>
          </div>
        ) : data && data.length > 0 ? (
          <table className="w-full text-xs">
            <thead className="bg-gray-100 sticky top-0">
              <tr>
                {columns.map((col) => (
                  <th
                    key={col}
                    className="px-3 py-2 text-left font-semibold text-gray-700 border-b border-gray-200"
                  >
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((row: DataRecord, rowIndex: number) => (
                <tr
                  key={rowIndex}
                  className={rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
                >
                  {columns.map((col) => (
                    <td
                      key={col}
                      className="px-3 py-2 border-b border-gray-200 text-gray-900"
                    >
                      {String(row[col] ?? '')}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="flex items-center justify-center h-64">
            <div className="text-center text-gray-500">
              <span className="material-symbols-rounded text-4xl mb-2">inbox</span>
              <p className="text-sm">No data available</p>
            </div>
          </div>
        )}
      </div>

      {/* Pagination */}
      {data && data.length > 0 && (
        <div className="p-4 border-t border-gray-200 flex items-center justify-between">
          <div className="text-sm text-gray-600">
            Showing {offset + 1} - {Math.min(offset + pageSize, total || 0)} of {(total || 0).toLocaleString()}
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handlePrevious}
              disabled={page === 0 || loading}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Previous
            </button>
            <span className="text-sm text-gray-600">
              Page {page + 1} of {totalPages}
            </span>
            <button
              onClick={handleNext}
              disabled={page >= totalPages - 1 || loading}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}