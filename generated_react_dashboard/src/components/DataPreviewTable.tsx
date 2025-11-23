import React, { useState, useMemo } from 'react';
import { useDataSource } from '../dataHooks';
import type { Pipeline } from '../types';

interface Props {
  pipeline: Pipeline;
  filePath: string;
}

export default function DataPreviewTable({ pipeline, filePath }: Props) {
  const [currentPage, setCurrentPage] = useState(1);
  const rowsPerPage = 10;

  const { data, total, loading, error } = useDataSource(pipeline.id, {
    limit: 100,
  });

  const paginatedData = useMemo(() => {
    if (!data || !Array.isArray(data)) return [];
    const startIndex = (currentPage - 1) * rowsPerPage;
    const endIndex = startIndex + rowsPerPage;
    return data.slice(startIndex, endIndex);
  }, [data, currentPage]);

  const totalPages = useMemo(() => {
    if (!data || !Array.isArray(data)) return 0;
    return Math.ceil(Math.min(data.length, 100) / rowsPerPage);
  }, [data]);

  const columns = useMemo(() => {
    if (!paginatedData || paginatedData.length === 0) return [];
    const firstRow = paginatedData[0];
    return Object.keys(firstRow);
  }, [paginatedData]);

  const handlePrevPage = () => {
    setCurrentPage(prev => Math.max(1, prev - 1));
  };

  const handleNextPage = () => {
    setCurrentPage(prev => Math.min(totalPages, prev + 1));
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-md p-8">
        <div className="flex items-center justify-center gap-3">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="text-gray-600">Loading data preview...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-md p-8">
        <div className="flex items-center gap-3 text-red-600">
          <span className="material-symbols-rounded">error</span>
          <span>Error loading data: {error}</span>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-md p-8 text-center">
        <span className="material-symbols-rounded text-gray-400 text-5xl mb-3">table_view</span>
        <p className="text-gray-600 text-lg">No data available for preview</p>
        <p className="text-gray-500 text-sm mt-2">{filePath}</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {pipeline.display_name || pipeline.name}
            </h3>
            <p className="text-sm text-gray-600 mt-1">{filePath}</p>
          </div>
          <div className="text-sm text-gray-600">
            Showing first 100 rows of {total?.toLocaleString() || 0} total records
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-100 sticky top-0">
            <tr>
              <th className="px-4 py-3 text-left text-sm font-bold text-gray-900 border-b border-gray-200">
                #
              </th>
              {columns.map(col => (
                <th
                  key={col}
                  className="px-4 py-3 text-left text-sm font-bold text-gray-900 border-b border-gray-200"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paginatedData.map((row, rowIndex) => (
              <tr
                key={rowIndex}
                className={rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
              >
                <td className="px-4 py-3 text-sm text-gray-600 border-b border-gray-100">
                  {(currentPage - 1) * rowsPerPage + rowIndex + 1}
                </td>
                {columns.map(col => (
                  <td
                    key={col}
                    className="px-4 py-3 text-sm text-gray-900 border-b border-gray-100"
                  >
                    {String(row[col] ?? '')}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex items-center justify-between">
        <div className="text-sm text-gray-600">
          Page {currentPage} of {totalPages} • Rows {(currentPage - 1) * rowsPerPage + 1}-
          {Math.min(currentPage * rowsPerPage, data.length)} of {Math.min(data.length, 100)}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handlePrevPage}
            disabled={currentPage === 1}
            className={`px-4 py-2 rounded-lg flex items-center gap-1 transition-colors ${
              currentPage === 1
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            <span className="material-symbols-rounded text-lg">chevron_left</span>
            Previous
          </button>
          <button
            onClick={handleNextPage}
            disabled={currentPage === totalPages}
            className={`px-4 py-2 rounded-lg flex items-center gap-1 transition-colors ${
              currentPage === totalPages
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            Next
            <span className="material-symbols-rounded text-lg">chevron_right</span>
          </button>
        </div>
      </div>
    </div>
  );
}