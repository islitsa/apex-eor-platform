import React, { useState } from 'react';
import { useDataSource } from '../dataHooks';

interface DataTableProps {
  pipelineId: string;
}

export default function DataTable({ pipelineId }: DataTableProps) {
  const [page, setPage] = useState(0);
  const limit = 100;
  const offset = page * limit;

  const { data, total, loading, error } = useDataSource(pipelineId, {
    limit,
    offset
  });

  if (loading) {
    return (
      <div className="border border-gray-200 rounded-lg p-8 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="mt-2 text-sm text-gray-600">Loading data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="border border-gray-200 rounded-lg p-8 text-center">
        <span className="material-symbols-rounded text-red-500 text-4xl">error</span>
        <p className="mt-2 text-sm text-gray-600">{String(error)}</p>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="border border-gray-200 rounded-lg p-8 text-center">
        <span className="material-symbols-rounded text-gray-400 text-4xl">table</span>
        <p className="mt-2 text-sm text-gray-600">No data available</p>
      </div>
    );
  }

  const columns = Object.keys(data[0] || {});
  const totalPages = Math.ceil((total || 0) / limit);
  const startRow = offset + 1;
  const endRow = Math.min(offset + limit, total || 0);

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              {columns.map((column) => (
                <th 
                  key={column}
                  className="px-4 py-3 text-left text-sm font-bold text-gray-900 border-b border-gray-200"
                  style={{ height: '48px' }}
                >
                  {String(column)}
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
                {columns.map((column) => (
                  <td 
                    key={column}
                    className="px-4 py-3 text-sm text-gray-900 border-b border-gray-100"
                    style={{ height: '48px' }}
                  >
                    {String(row[column] ?? '')}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination Controls */}
      <div className="bg-gray-50 px-4 py-3 flex items-center justify-between border-t border-gray-200">
        <div className="text-sm text-gray-700">
          Showing {Number(startRow).toLocaleString()}-{Number(endRow).toLocaleString()} of {Number(total || 0).toLocaleString()} rows
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setPage(Math.max(0, page - 1))}
            disabled={page === 0}
            className="inline-flex items-center px-4 py-2 rounded-full bg-white border border-gray-300 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            style={{ height: '36px' }}
          >
            <span className="material-symbols-rounded mr-1" style={{ fontSize: '16px' }}>
              arrow_back
            </span>
            Previous
          </button>
          <span className="text-sm text-gray-700">
            Page {page + 1} of {totalPages}
          </span>
          <button
            onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
            disabled={page >= totalPages - 1}
            className="inline-flex items-center px-4 py-2 rounded-full bg-white border border-gray-300 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            style={{ height: '36px' }}
          >
            Next
            <span className="material-symbols-rounded ml-1" style={{ fontSize: '16px' }}>
              arrow_forward
            </span>
          </button>
        </div>
      </div>
    </div>
  );
}