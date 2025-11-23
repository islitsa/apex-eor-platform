import React, { useState } from 'react';
import { ChemicalTableProps, ChemicalRecord } from '../types.ts';

export default function ChemicalTable({ data }: ChemicalTableProps) {
  const [sortColumn, setSortColumn] = useState<keyof ChemicalRecord | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  const handleSort = (column: keyof ChemicalRecord) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('asc');
    }
  };

  const sortedData = React.useMemo(() => {
    if (!sortColumn) return data;

    return [...data].sort((a, b) => {
      const aVal = a[sortColumn];
      const bVal = b[sortColumn];

      if (aVal === undefined || aVal === null) return 1;
      if (bVal === undefined || bVal === null) return -1;

      const comparison = aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
      return sortDirection === 'asc' ? comparison : -comparison;
    });
  }, [data, sortColumn, sortDirection]);

  const SortIcon = ({ column }: { column: keyof ChemicalRecord }) => {
    if (sortColumn !== column) {
      return <span className="material-symbols-rounded text-gray-400 text-sm">unfold_more</span>;
    }
    return (
      <span className="material-symbols-rounded text-blue-600 text-sm">
        {sortDirection === 'asc' ? 'arrow_upward' : 'arrow_downward'}
      </span>
    );
  };

  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
        <span className="material-symbols-rounded text-gray-400 text-6xl mb-4">science_off</span>
        <p className="text-gray-600 text-lg">No chemical data found</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th
                onClick={() => handleSort('ChemicalName')}
                className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center gap-2">
                  Chemical Name
                  <SortIcon column="ChemicalName" />
                </div>
              </th>
              <th
                onClick={() => handleSort('CASNumber')}
                className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center gap-2">
                  CAS Number
                  <SortIcon column="CASNumber" />
                </div>
              </th>
              <th
                onClick={() => handleSort('Supplier')}
                className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center gap-2">
                  Supplier
                  <SortIcon column="Supplier" />
                </div>
              </th>
              <th
                onClick={() => handleSort('Purpose')}
                className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center gap-2">
                  Purpose
                  <SortIcon column="Purpose" />
                </div>
              </th>
              <th
                onClick={() => handleSort('PercentHFJob')}
                className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center gap-2">
                  % of HF Job
                  <SortIcon column="PercentHFJob" />
                </div>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {sortedData.map((record, index) => (
              <tr key={index} className="hover:bg-gray-50 transition-colors">
                <td className="px-6 py-4 text-sm text-gray-900">
                  {record.ChemicalName || <span className="text-gray-400 italic">N/A</span>}
                </td>
                <td className="px-6 py-4 text-sm text-gray-600 font-mono">
                  {record.CASNumber || <span className="text-gray-400 italic">N/A</span>}
                </td>
                <td className="px-6 py-4 text-sm text-gray-900">
                  {record.Supplier || <span className="text-gray-400 italic">N/A</span>}
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  {record.Purpose || <span className="text-gray-400 italic">N/A</span>}
                </td>
                <td className="px-6 py-4 text-sm text-gray-900">
                  {record.PercentHFJob !== undefined && record.PercentHFJob !== null ? (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {typeof record.PercentHFJob === 'number'
                        ? `${record.PercentHFJob.toFixed(2)}%`
                        : `${record.PercentHFJob}%`}
                    </span>
                  ) : (
                    <span className="text-gray-400 italic">N/A</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}