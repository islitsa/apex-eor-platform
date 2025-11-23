import React from 'react';
import PaginationControls from './PaginationControls.tsx';
import type { DataSourceRecord } from '../types.ts';

interface ChemicalDataTableProps {
  data: DataSourceRecord[];
  loading: boolean;
  error: string | null;
  currentPage: number;
  rowsPerPage: number;
  totalRecords: number;
  onPageChange: (page: number) => void;
}

export default function ChemicalDataTable({
  data,
  loading,
  error,
  currentPage,
  rowsPerPage,
  totalRecords,
  onPageChange
}: ChemicalDataTableProps) {
  if (loading) {
    return (
      <div className="p-12 text-center">
        <div className="inline-block animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
        <p className="mt-4 text-gray-600">Loading data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-12">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <span className="material-symbols-rounded text-red-600 text-4xl">error</span>
          <p className="mt-2 text-red-700">{String(error)}</p>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="p-12 text-center">
        <span className="material-symbols-rounded text-gray-300 text-6xl">table_chart</span>
        <p className="mt-4 text-gray-600">No data available</p>
      </div>
    );
  }

  const columns = Object.keys(data[0] || {});
  const totalPages = Math.ceil(totalRecords / rowsPerPage);

  return (
    <div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              {columns.map(column => (
                <th 
                  key={column}
                  className="px-6 py-3 text-left text-sm font-bold text-gray-900"
                >
                  {String(column).replace(/_/g, ' ')}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, rowIndex) => (
              <tr 
                key={rowIndex}
                className={rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
              >
                {columns.map(column => (
                  <td 
                    key={`${rowIndex}-${column}`}
                    className="px-6 py-4 text-sm text-gray-700 border-b border-gray-100"
                  >
                    {row[column] !== null && row[column] !== undefined 
                      ? String(row[column]) 
                      : '-'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="border-t border-gray-200 px-6 py-4">
        <PaginationControls
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={onPageChange}
        />
      </div>
    </div>
  );
}