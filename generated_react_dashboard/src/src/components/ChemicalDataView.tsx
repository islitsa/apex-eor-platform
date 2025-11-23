import React, { useState } from 'react';
import { useDataSource } from '../dataHooks.tsx';

interface ChemicalDataViewProps {
  pipelineId: string;
}

export default function ChemicalDataView({ pipelineId }: ChemicalDataViewProps) {
  const [limit, setLimit] = useState(50);
  const { data, total, loading, error } = useDataSource(pipelineId, { limit });

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <p className="mt-4 text-gray-600">Loading chemical data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8">
        <div className="flex items-center gap-3 text-red-600">
          <span className="material-symbols-rounded text-3xl">error</span>
          <div>
            <h3 className="font-semibold">Error Loading Data</h3>
            <p className="text-sm mt-1">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <span className="material-symbols-rounded text-5xl text-gray-300">database</span>
        <p className="mt-4 text-gray-500">No chemical data available for this pipeline</p>
      </div>
    );
  }

  const columns = Object.keys(data[0]);

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      {/* Header */}
      <div className="bg-primary-600 text-white px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="material-symbols-rounded text-3xl">science</span>
          <div>
            <h2 className="text-xl font-bold">Chemical Data Records</h2>
            <p className="text-sm text-primary-100">{total.toLocaleString()} total records</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <label className="text-sm">Show:</label>
          <select
            value={limit}
            onChange={e => setLimit(Number(e.target.value))}
            className="bg-white text-gray-900 rounded px-3 py-1 text-sm"
          >
            <option value={25}>25</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
            <option value={250}>250</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              {columns.map(col => (
                <th key={col} className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {data.map((row, index) => (
              <tr key={index} className="hover:bg-gray-50">
                {columns.map(col => (
                  <td key={col} className="px-4 py-3 text-sm text-gray-700 whitespace-nowrap">
                    {row[col] !== null && row[col] !== undefined ? String(row[col]) : '-'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Footer */}
      <div className="bg-gray-50 px-6 py-3 border-t border-gray-200 text-sm text-gray-600">
        Showing {data.length} of {total.toLocaleString()} records
      </div>
    </div>
  );
}