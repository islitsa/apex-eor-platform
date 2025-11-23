import React, { useState, useMemo } from 'react';
import { useDataSource } from '../dataHooks';
import PaginationControls from './PaginationControls.tsx';
import type { Pipeline } from '../types';

interface DataTableContainerProps {
  pipeline: Pipeline;
  filePath: string;
}

export default function DataTableContainer({ pipeline, filePath }: DataTableContainerProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const rowsPerPage = 10;

  const { data, total, loading, error } = useDataSource(pipeline.id, {
    limit: 100
  });

  const paginatedData = useMemo(() => {
    if (!data || !Array.isArray(data)) return [];
    const startIndex = (currentPage - 1) * rowsPerPage;
    const endIndex = startIndex + rowsPerPage;
    return data.slice(startIndex, endIndex);
  }, [data, currentPage]);

  const totalPages = Math.ceil((data?.length || 0) / rowsPerPage);

  const columns = useMemo(() => {
    if (!data || data.length === 0) return [];
    return Object.keys(data[0]);
  }, [data]);

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <div className="flex items-center gap-3 mb-2">
            <span className="material-symbols-rounded text-red-600">error</span>
            <h3 className="text-lg font-semibold text-red-900">Error Loading Data</h3>
          </div>
          <p className="text-red-700">{error}</p>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <span className="material-symbols-rounded text-gray-300 text-6xl mb-4">table_chart</span>
          <h3 className="text-xl font-semibold text-gray-700 mb-2">No Data Available</h3>
          <p className="text-gray-500">This file contains no records</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="flex-1 overflow-auto">
        <table className="w-full">
          <thead className="bg-gray-100 sticky top-0 z-10">
            <tr>
              {columns.map((column, index) => (
                <th
                  key={index}
                  className="px-6 py-4 text-left text-sm font-bold text-gray-900 border-b border-gray-200"
                >
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paginatedData.map((row, rowIndex) => (
              <tr
                key={rowIndex}
                className={`transition-colors ${
                  rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'
                } hover:bg-blue-50`}
              >
                {columns.map((column, colIndex) => (
                  <td
                    key={colIndex}
                    className="px-6 py-4 text-sm text-gray-700 border-b border-gray-200"
                  >
                    {String(row[column] ?? '')}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <PaginationControls
        currentPage={currentPage}
        totalPages={totalPages}
        onPageChange={setCurrentPage}
        totalRecords={data.length}
        displayedRecords={paginatedData.length}
      />
    </div>
  );
}