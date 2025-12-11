import React from 'react';
import { FilePreviewResponse } from '../types.ts';
import PaginationControls from './PaginationControls.tsx';

interface DataPreviewTableProps {
  data: FilePreviewResponse | null;
  loading: boolean;
  error: string | null;
  currentPage: number;
  pageSize: number;
  onPageChange: (page: number) => void;
}

function DataPreviewTable({ data, loading, error, currentPage, pageSize, onPageChange }: DataPreviewTableProps) {
  if (loading) {
    return (
      <div className="space-y-2">
        {/* Skeleton loader */}
        <div className="animate-pulse">
          <div className="h-11 bg-gray-200 rounded mb-2"></div>
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-11 bg-gray-100 rounded mb-1"></div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-start gap-2">
          <span className="material-symbols-rounded text-red-600 text-sm">error</span>
          <div>
            <h4 className="font-semibold text-red-900 text-sm">Error Loading Preview</h4>
            <p className="text-red-700 text-xs mt-1">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!data || !data.columns || data.columns.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <span className="material-symbols-rounded text-4xl">table</span>
        <p className="mt-2 text-sm">No preview data available</p>
      </div>
    );
  }

  const totalPages = Math.ceil(data.totalRows / pageSize);

  const formatCellValue = (value: unknown): string => {
    if (value === null || value === undefined) return '';
    if (typeof value === 'number') return String(value);
    return String(value);
  };

  const isNumeric = (value: unknown): boolean => {
    return typeof value === 'number' || (typeof value === 'string' && !isNaN(Number(value)) && value.trim() !== '');
  };

  return (
    <div className="space-y-4">
      <div className="overflow-x-auto border border-gray-200 rounded-lg">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              {data.columns.map((column, index) => (
                <th
                  key={`${column}-${index}`}
                  className="px-4 py-3 text-left font-bold text-gray-900"
                  style={{ fontSize: '14px' }}
                >
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.rows.map((row, rowIndex) => (
              <tr
                key={rowIndex}
                className={rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
                style={{ height: '44px' }}
              >
                {data.columns.map((column, colIndex) => {
                  const value = row[column];
                  const isNum = isNumeric(value);
                  return (
                    <td
                      key={`${rowIndex}-${colIndex}`}
                      className={`px-4 py-2 text-gray-700 ${isNum ? 'font-mono' : ''}`}
                      style={{ fontSize: '13px' }}
                    >
                      {formatCellValue(value)}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <PaginationControls
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={onPageChange}
        />
      )}

      <div className="text-xs text-gray-500 text-center">
        Showing {((currentPage - 1) * pageSize) + 1} - {Math.min(currentPage * pageSize, data.totalRows)} of {data.totalRows.toLocaleString()} rows
      </div>
    </div>
  );
}

export default DataPreviewTable;