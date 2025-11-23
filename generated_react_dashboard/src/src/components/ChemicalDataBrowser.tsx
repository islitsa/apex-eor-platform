import React, { useState, useMemo } from 'react';
import { useDataSource } from '../dataHooks.tsx';

interface Props {
  pipelineId: string;
}

export default function ChemicalDataBrowser({ pipelineId }: Props) {
  const [page, setPage] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const pageSize = 50;

  const { data, total, loading, error } = useDataSource('fracfocus', {
    limit: pageSize,
    offset: page * pageSize
  });

  // Get column names from first record
  const columns = useMemo(() => {
    if (!data || data.length === 0) return [];
    return Object.keys(data[0]);
  }, [data]);

  // Filter data based on search
  const filteredData = useMemo(() => {
    if (!searchTerm) return data;
    return data.filter(row =>
      Object.values(row).some(val =>
        String(val).toLowerCase().includes(searchTerm.toLowerCase())
      )
    );
  }, [data, searchTerm]);

  const totalPages = Math.ceil(total / pageSize);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          <p className="mt-2 text-on-surface-variant">Loading chemical data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center gap-2 text-red-800">
          <span className="material-symbols-rounded">error</span>
          <span>Error loading data: {error}</span>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="text-center py-12">
        <span className="material-symbols-rounded text-6xl text-on-surface-variant">database</span>
        <p className="mt-4 text-on-surface-variant">No chemical data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Search and Stats */}
      <div className="flex items-center justify-between gap-4">
        <div className="flex-1 relative">
          <span className="material-symbols-rounded absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant">
            search
          </span>
          <input
            type="text"
            placeholder="Search chemical data..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
          />
        </div>
        <div className="text-sm text-on-surface-variant">
          Showing {page * pageSize + 1}-{Math.min((page + 1) * pageSize, total)} of {total.toLocaleString()} records
        </div>
      </div>

      {/* Data Table */}
      <div className="overflow-x-auto border border-gray-200 rounded-lg">
        <table className="w-full text-sm">
          <thead className="bg-surface-variant">
            <tr>
              {columns.map(col => (
                <th key={col} className="px-4 py-3 text-left font-medium text-on-surface border-b border-gray-200">
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filteredData.map((row, idx) => (
              <tr key={idx} className="hover:bg-surface-variant/50 transition-colors">
                {columns.map(col => (
                  <td key={col} className="px-4 py-3 border-b border-gray-100 text-on-surface-variant">
                    {String(row[col] ?? '')}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => setPage(p => Math.max(0, p - 1))}
          disabled={page === 0}
          className="flex items-center gap-1 px-4 py-2 text-sm font-medium text-primary disabled:text-gray-400 disabled:cursor-not-allowed hover:bg-primary/10 rounded-lg transition-colors"
        >
          <span className="material-symbols-rounded">chevron_left</span>
          Previous
        </button>
        
        <div className="flex items-center gap-2">
          {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
            const pageNum = page < 3 ? i : page - 2 + i;
            if (pageNum >= totalPages) return null;
            return (
              <button
                key={pageNum}
                onClick={() => setPage(pageNum)}
                className={`w-8 h-8 rounded-lg text-sm font-medium transition-colors ${
                  page === pageNum
                    ? 'bg-primary text-white'
                    : 'text-on-surface hover:bg-surface-variant'
                }`}
              >
                {pageNum + 1}
              </button>
            );
          })}
        </div>

        <button
          onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
          disabled={page >= totalPages - 1}
          className="flex items-center gap-1 px-4 py-2 text-sm font-medium text-primary disabled:text-gray-400 disabled:cursor-not-allowed hover:bg-primary/10 rounded-lg transition-colors"
        >
          Next
          <span className="material-symbols-rounded">chevron_right</span>
        </button>
      </div>
    </div>
  );
}