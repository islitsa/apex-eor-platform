import React, { useState, useMemo } from 'react';
import { useDataSource } from '../dataHooks.tsx';
import type { Pipeline } from '../types.ts';

interface DataViewerProps {
  pipeline: Pipeline;
}

export default function DataViewer({ pipeline }: DataViewerProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const rowsPerPage = 100;
  const offset = (currentPage - 1) * rowsPerPage;

  const { data, total, loading, error } = useDataSource(pipeline.id, {
    limit: rowsPerPage,
    offset
  });

  const columns = useMemo(() => {
    if (!data || data.length === 0) return [];
    return Object.keys(data[0]);
  }, [data]);

  const totalPages = Math.ceil(total / rowsPerPage);

  const handlePrevPage = () => {
    setCurrentPage(prev => Math.max(1, prev - 1));
  };

  const handleNextPage = () => {
    setCurrentPage(prev => Math.min(totalPages, prev + 1));
  };

  const handleFirstPage = () => {
    setCurrentPage(1);
  };

  const handleLastPage = () => {
    setCurrentPage(totalPages);
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-12">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mb-4"></div>
          <p className="text-gray-600">Loading data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-12">
        <div className="text-center text-red-600">
          <span className="material-symbols-rounded text-5xl mb-4">error</span>
          <p className="font-semibold">Error loading data</p>
          <p className="text-sm text-gray-600 mt-2">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md">
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Data Viewer</h2>
            <p className="text-sm text-gray-500 mt-1">
              {pipeline.display_name || pipeline.name} • Showing {data.length.toLocaleString()} of {total.toLocaleString()} records
            </p>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={handleFirstPage}
              disabled={currentPage === 1}
              className="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
              title="First page"
            >
              <span className="material-symbols-rounded">first_page</span>
            </button>
            <button
              onClick={handlePrevPage}
              disabled={currentPage === 1}
              className="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
              title="Previous page"
            >
              <span className="material-symbols-rounded">chevron_left</span>
            </button>
            
            <span className="px-4 py-2 text-sm font-medium text-gray-700">
              Page {currentPage} of {totalPages}
            </span>
            
            <button
              onClick={handleNextPage}
              disabled={currentPage === totalPages}
              className="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
              title="Next page"
            >
              <span className="material-symbols-rounded">chevron_right</span>
            </button>
            <button
              onClick={handleLastPage}
              disabled={currentPage === totalPages}
              className="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
              title="Last page"
            >
              <span className="material-symbols-rounded">last_page</span>
            </button>
          </div>
        </div>
      </div>

      {data.length === 0 ? (
        <div className="p-12 text-center text-gray-500">
          <span className="material-symbols-rounded text-5xl mb-4">table_view</span>
          <p>No data available</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider sticky left-0 bg-gray-50">
                  #
                </th>
                {columns.map((col) => (
                  <th
                    key={col}
                    className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap"
                  >
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {data.map((row, rowIndex) => (
                <tr key={rowIndex} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm text-gray-500 sticky left-0 bg-white">
                    {offset + rowIndex + 1}
                  </td>
                  {columns.map((col) => (
                    <td
                      key={col}
                      className="px-4 py-3 text-sm text-gray-900 whitespace-nowrap"
                    >
                      {row[col] !== null && row[col] !== undefined
                        ? String(row[col])
                        : '-'}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <span>
            Showing rows {offset + 1} - {Math.min(offset + rowsPerPage, total)} of {total.toLocaleString()}
          </span>
          <span>
            {columns.length} columns
          </span>
        </div>
      </div>
    </div>
  );
}