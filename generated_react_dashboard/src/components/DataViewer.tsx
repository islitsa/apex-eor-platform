import React, { useState, useMemo } from 'react';
import { useDataSource } from '../dataHooks';
import type { Pipeline } from '../types';

interface DataViewerProps {
  pipeline: Pipeline | null;
  selectedFile: string | null;
}

export default function DataViewer({ pipeline, selectedFile }: DataViewerProps) {
  const [currentPage, setCurrentPage] = useState(0);
  const rowsPerPage = 100;

  const { data, total, loading, error } = useDataSource(
    pipeline?.id || '',
    {
      limit: rowsPerPage,
      offset: currentPage * rowsPerPage
    }
  );

  const columns = useMemo(() => {
    if (!data || data.length === 0) return [];
    return Object.keys(data[0]);
  }, [data]);

  const totalPages = Math.ceil(total / rowsPerPage);

  const handlePrevPage = () => {
    setCurrentPage(prev => Math.max(0, prev - 1));
  };

  const handleNextPage = () => {
    setCurrentPage(prev => Math.min(totalPages - 1, prev + 1));
  };

  if (!pipeline) {
    return (
      <div className="bg-white rounded-lg shadow-md p-12 text-center">
        <span className="material-symbols-rounded text-gray-300 text-6xl mb-4">table_chart</span>
        <h3 className="text-xl font-semibold text-gray-600 mb-2">No Data Source Selected</h3>
        <p className="text-gray-500">Select a data source from the left to view its contents</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-12 text-center">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
        <p className="text-gray-600">Loading data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-12 text-center">
        <span className="material-symbols-rounded text-red-500 text-6xl mb-4">error</span>
        <h3 className="text-xl font-semibold text-red-600 mb-2">Error Loading Data</h3>
        <p className="text-gray-600">{error}</p>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-12 text-center">
        <span className="material-symbols-rounded text-gray-300 text-6xl mb-4">inbox</span>
        <h3 className="text-xl font-semibold text-gray-600 mb-2">No Data Available</h3>
        <p className="text-gray-500">This data source contains no records</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md flex flex-col" style={{ height: 'calc(100vh - 200px)' }}>
      {/* Header */}
      <div className="bg-gray-800 text-white px-6 py-4 rounded-t-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="material-symbols-rounded">table_chart</span>
            <div>
              <h2 className="text-lg font-bold">{pipeline.display_name || pipeline.name}</h2>
              {selectedFile && (
                <p className="text-sm text-gray-300 mt-1">
                  <span className="material-symbols-rounded text-xs align-middle mr-1">description</span>
                  {selectedFile}
                </p>
              )}
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-300">Total Records</p>
            <p className="text-2xl font-bold">{total.toLocaleString()}</p>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="flex-1 overflow-auto">
        <table className="w-full">
          <thead className="bg-gray-100 sticky top-0 z-10">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b-2 border-gray-200">
                #
              </th>
              {columns.map(col => (
                <th
                  key={col}
                  className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b-2 border-gray-200"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {data.map((row, rowIndex) => (
              <tr key={rowIndex} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm text-gray-500 font-medium">
                  {currentPage * rowsPerPage + rowIndex + 1}
                </td>
                {columns.map(col => (
                  <td key={col} className="px-4 py-3 text-sm text-gray-900">
                    {String(row[col] ?? '')}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      <div className="bg-gray-50 px-6 py-4 border-t border-gray-200 flex items-center justify-between rounded-b-lg">
        <div className="text-sm text-gray-600">
          Showing {currentPage * rowsPerPage + 1} to {Math.min((currentPage + 1) * rowsPerPage, total)} of {total.toLocaleString()} records
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handlePrevPage}
            disabled={currentPage === 0}
            className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
          >
            <span className="material-symbols-rounded text-sm">chevron_left</span>
            Previous
          </button>
          <span className="text-sm text-gray-600">
            Page {currentPage + 1} of {totalPages}
          </span>
          <button
            onClick={handleNextPage}
            disabled={currentPage >= totalPages - 1}
            className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
          >
            Next
            <span className="material-symbols-rounded text-sm">chevron_right</span>
          </button>
        </div>
      </div>
    </div>
  );
}