import React from 'react';

interface MetricsDashboardHeaderProps {
  dataSourceCount: number;
  totalFiles: number;
  totalRecords: number;
}

export default function MetricsDashboardHeader({
  dataSourceCount,
  totalFiles,
  totalRecords
}: MetricsDashboardHeaderProps) {
  return (
    <header className="bg-white border-b border-gray-200 h-[120px] flex items-center px-8">
      <div className="max-w-[1600px] mx-auto w-full">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="material-symbols-rounded text-blue-600 text-5xl">database</span>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Chemical Data Dashboard</h1>
              <p className="text-gray-600 text-lg mt-1">FracFocus Data Repository</p>
            </div>
          </div>

          <div className="flex gap-8">
            <div className="text-right">
              <div className="text-3xl font-bold text-blue-600">
                {Number(dataSourceCount || 0).toLocaleString()}
              </div>
              <div className="text-sm text-gray-600 uppercase tracking-wide">Data Sources</div>
            </div>

            <div className="text-right">
              <div className="text-3xl font-bold text-green-600">
                {Number(totalFiles || 0).toLocaleString()}
              </div>
              <div className="text-sm text-gray-600 uppercase tracking-wide">Total Files</div>
            </div>

            <div className="text-right">
              <div className="text-3xl font-bold text-purple-600">
                {Number(totalRecords || 0).toLocaleString()}
              </div>
              <div className="text-sm text-gray-600 uppercase tracking-wide">Total Records</div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}