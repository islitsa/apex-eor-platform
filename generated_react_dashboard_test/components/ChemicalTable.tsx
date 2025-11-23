import React, { useState } from 'react';
import { ChemicalTableProps, ChemicalRecord } from '../types.ts';

export default function ChemicalTable({ data }: ChemicalTableProps) {
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  const handleSort = (column: string) => {
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

      if (aVal == null) return 1;
      if (bVal == null) return -1;

      const comparison = aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
      return sortDirection === 'asc' ? comparison : -comparison;
    });
  }, [data, sortColumn, sortDirection]);

  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md border border-gray-200 p-12 text-center">
        <span className="material-symbols-rounded text-gray-400 text-6xl mb-4 block">
          search_off
        </span>
        <p className="text-gray-600 text-lg">No chemical records found</p>
      </div>
    );
  }

  const SortIcon = ({ column }: { column: string }) => {
    if (sortColumn !== column) {
      return <span className="material-symbols-rounded text-gray-400 text-sm">unfold_more</span>;
    }
    return (
      <span className="material-symbols-rounded text-blue-600 text-sm">
        {sortDirection === 'asc' ? 'arrow_upward' : 'arrow_downward'}
      </span>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th
                onClick={() => handleSort('DisclosureId')}
                className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center gap-2">
                  Disclosure ID
                  <SortIcon column="DisclosureId" />
                </div>
              </th>
              <th
                onClick={() => handleSort('JobStartDate')}
                className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center gap-2">
                  Job Start Date
                  <SortIcon column="JobStartDate" />
                </div>
              </th>
              <th
                onClick={() => handleSort('JobEndDate')}
                className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center gap-2">
                  Job End Date
                  <SortIcon column="JobEndDate" />
                </div>
              </th>
              <th
                onClick={() => handleSort('APINumber')}
                className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center gap-2">
                  API Number
                  <SortIcon column="APINumber" />
                </div>
              </th>
              <th
                onClick={() => handleSort('StateName')}
                className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center gap-2">
                  State
                  <SortIcon column="StateName" />
                </div>
              </th>
              <th
                onClick={() => handleSort('CountyName')}
                className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center gap-2">
                  County
                  <SortIcon column="CountyName" />
                </div>
              </th>
              <th
                onClick={() => handleSort('OperatorName')}
                className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center gap-2">
                  Operator
                  <SortIcon column="OperatorName" />
                </div>
              </th>
              <th
                onClick={() => handleSort('WellName')}
                className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center gap-2">
                  Well Name
                  <SortIcon column="WellName" />
                </div>
              </th>
              <th
                onClick={() => handleSort('Latitude')}
                className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center gap-2">
                  Latitude
                  <SortIcon column="Latitude" />
                </div>
              </th>
              <th
                onClick={() => handleSort('Longitude')}
                className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center gap-2">
                  Longitude
                  <SortIcon column="Longitude" />
                </div>
              </th>
              <th
                onClick={() => handleSort('Projection')}
                className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center gap-2">
                  Projection
                  <SortIcon column="Projection" />
                </div>
              </th>
              <th
                onClick={() => handleSort('TVD')}
                className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center gap-2">
                  TVD
                  <SortIcon column="TVD" />
                </div>
              </th>
              <th
                onClick={() => handleSort('TotalBaseWaterVolume')}
                className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center gap-2">
                  Water Volume
                  <SortIcon column="TotalBaseWaterVolume" />
                </div>
              </th>
              <th
                onClick={() => handleSort('TotalBaseNonWaterVolume')}
                className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center gap-2">
                  Non-Water Volume
                  <SortIcon column="TotalBaseNonWaterVolume" />
                </div>
              </th>
              <th
                onClick={() => handleSort('FFVersion')}
                className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center gap-2">
                  FF Version
                  <SortIcon column="FFVersion" />
                </div>
              </th>
              <th
                onClick={() => handleSort('FederalWell')}
                className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center gap-2">
                  Federal Well
                  <SortIcon column="FederalWell" />
                </div>
              </th>
              <th
                onClick={() => handleSort('IndianWell')}
                className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center gap-2">
                  Indian Well
                  <SortIcon column="IndianWell" />
                </div>
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {sortedData.map((record: any, index: number) => (
              <tr key={index} className="hover:bg-gray-50 transition-colors">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {record.DisclosureId || '—'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {record.JobStartDate || '—'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {record.JobEndDate || '—'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {record.APINumber || '—'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {record.StateName || '—'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {record.CountyName || '—'}
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  {record.OperatorName || '—'}
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  {record.WellName || '—'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {record.Latitude || '—'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {record.Longitude || '—'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {record.Projection || '—'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {record.TVD || '—'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {record.TotalBaseWaterVolume || '—'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {record.TotalBaseNonWaterVolume || '—'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {record.FFVersion || '—'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {record.FederalWell || '—'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {record.IndianWell || '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}