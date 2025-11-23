import React, { useMemo } from 'react';
import { useDataSource } from '../dataHooks';
import { Pipeline } from '../types';

interface Props {
  pipeline: Pipeline | undefined;
  currentPage: number;
  rowsPerPage: number;
}

export default function DataTableGrid({ pipeline, currentPage, rowsPerPage }: Props) {
  const offset = (currentPage - 1) * rowsPerPage;

  const { data, total, loading, error } = useDataSource(
    pipeline?.id || 'fracfocus',
    { limit: rowsPerPage, offset }
  );

  const columns = useMemo(() => {
    if (!data || data.length === 0) return [];
    return Object.keys(data[0]);
  }, [data]);

  const startRow = offset + 1;
  const endRow = Math.min(offset + rowsPerPage, total);

  if (!pipeline) {
    return (
      <div className="bg-white rounded-lg border-2 border-gray-200 shadow-sm p-8 text-center">
        <span className="material-symbols-rounded text-gray-400 text-5xl block mb-4">table_chart</span>
        <p className="text-gray-600">Select a pipeline to view data</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg border-2 border-gray-200 shadow-sm p-8">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mr-3"></div>
          <span className="text-gray-600">Loading data...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg border-2 border-gray-200 shadow-sm p-8">
        <div className="text-center">
          <span className="material-symbols-rounded text-red-600 text-5xl block mb-4">error</span>
          <h3 className="text-lg font-bold text-gray-900 mb-2">Error Loading Data</h3>
          <p className="text-gray-600">{String(error)}</p>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-lg border-2 border-gray-200 shadow-sm p-8 text-center">
        <span className="material-symbols-rounded text-gray-400 text-5xl block mb-4">inbox</span>
        <p className="text-gray-600">No data available</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border-2 border-gray-200 shadow-sm">
      <div className="p-4 border-b border-gray-200 flex items-center justify-between">
        <h2 className="text-lg font-bold text-gray-900">Data Preview</h2>
        <span className="text-sm text-gray-600">
          Rows {startRow.toLocaleString()}-{endRow.toLocaleString()} of {total.toLocaleString()}
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200 sticky top-0">
            <tr>
              {columns.map((column, index) => (
                <th
                  key={index}
                  className="px-4 py-3 text-left text-xs font-bold text-gray-900 uppercase tracking-wider whitespace-nowrap"
                >
                  {String(column)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {data.map((row, rowIndex) => (
              <tr
                key={rowIndex}
                className={`hover:bg-gray-50 transition-colors ${rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}
              >
                {columns.map((column, colIndex) => (
                  <td key={colIndex} className="px-4 py-3 text-sm text-gray-900 whitespace-nowrap">
                    {row[column] !== null && row[column] !== undefined ? String(row[column]) : '-'}
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