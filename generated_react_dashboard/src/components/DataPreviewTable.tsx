import React from 'react';
import { useDataSource } from '../dataHooks';
import type { Pipeline } from '../types';

interface Props {
  pipeline: Pipeline;
  selectedFile: string | null;
  currentPage: number;
  rowsPerPage: number;
}

export default function DataPreviewTable({ pipeline, selectedFile, currentPage, rowsPerPage }: Props) {
  const offset = (currentPage - 1) * rowsPerPage;
  
  const { data, total, loading, error } = useDataSource(pipeline.id, {
    limit: Math.min(rowsPerPage, 100),
    offset: offset
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
          <p className="text-sm text-gray-600">Loading data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <span className="material-symbols-rounded text-red-600 text-4xl mb-2">error</span>
          <p className="text-sm text-red-600">{String(error)}</p>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <span className="material-symbols-rounded text-gray-300 text-5xl mb-2">table_chart</span>
          <p className="text-gray-500">No data available</p>
          {selectedFile && (
            <p className="text-sm text-gray-400 mt-1">Selected: {selectedFile}</p>
          )}
        </div>
      </div>
    );
  }

  const columns = Object.keys(data[0] || {});

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div className="p-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="material-symbols-rounded text-blue-600">science</span>
            <h3 className="font-semibold text-gray-900">Chemical Data Preview</h3>
          </div>
          <span className="text-sm text-gray-600">
            {Number(total || 0).toLocaleString()} total records
          </span>
        </div>
        {selectedFile && (
          <p className="text-xs text-gray-500 mt-1 truncate">
            File: {selectedFile}
          </p>
        )}
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 sticky top-0">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200">
                #
              </th>
              {columns.map(col => (
                <th
                  key={col}
                  className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200"
                >
                  {String(col).replace(/_/g, ' ')}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, idx) => (
              <tr
                key={idx}
                className={`hover:bg-blue-50 cursor-pointer transition-colors ${
                  idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'
                }`}
                style={{ height: '40px' }}
              >
                <td className="px-4 py-2 text-sm text-gray-500 border-b border-gray-100">
                  {offset + idx + 1}
                </td>
                {columns.map(col => (
                  <td
                    key={col}
                    className="px-4 py-2 text-sm text-gray-900 border-b border-gray-100 max-w-xs truncate"
                  >
                    {row[col] !== null && row[col] !== undefined ? String(row[col]) : '-'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}