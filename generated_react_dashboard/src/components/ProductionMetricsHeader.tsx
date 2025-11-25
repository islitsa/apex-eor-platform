import React from 'react';

interface Props {
  totalFiles: number;
  totalRecords: number;
  totalSize: number;
  sourceCount: number;
}

export default function ProductionMetricsHeader({
  totalFiles,
  totalRecords,
  totalSize,
  sourceCount
}: Props) {
  return (
    <div className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-[1440px] mx-auto px-6 py-6">
        <div className="flex items-center gap-3 mb-6">
          <span className="material-symbols-rounded text-blue-600 text-3xl">database</span>
          <h1 className="text-2xl font-bold text-gray-900">RRC Production Data</h1>
          <span className="flex items-center gap-2 ml-4 px-3 py-1 bg-blue-50 rounded-full">
            <span className="material-symbols-rounded text-blue-600 text-sm">oil_barrel</span>
            <span className="text-sm font-medium text-blue-900">petroleum_energy</span>
          </span>
        </div>

        <div className="grid grid-cols-4 gap-6">
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="material-symbols-rounded text-gray-600 text-xl">folder</span>
              <span className="text-sm font-medium text-gray-600">Data Sources</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">{sourceCount}</p>
          </div>

          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="material-symbols-rounded text-gray-600 text-xl">description</span>
              <span className="text-sm font-medium text-gray-600">Total Files</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">{totalFiles.toLocaleString()}</p>
          </div>

          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="material-symbols-rounded text-gray-600 text-xl">table_rows</span>
              <span className="text-sm font-medium text-gray-600">Total Records</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">{totalRecords.toLocaleString()}</p>
          </div>

          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="material-symbols-rounded text-gray-600 text-xl">storage</span>
              <span className="text-sm font-medium text-gray-600">Total Size</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">{Number(totalSize || 0).toFixed(2)} GB</p>
          </div>
        </div>
      </div>
    </div>
  );
}