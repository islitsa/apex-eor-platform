import React, { useState, useMemo } from 'react';
import type { Pipeline } from '../types';
import PaginationControls from './PaginationControls';

interface Props {
  pipeline: Pipeline;
}

export default function ChemicalDataTable({ pipeline }: Props) {
  const [currentPage, setCurrentPage] = useState(1);
  const rowsPerPage = 100;

  // Generate sample data structure based on pipeline
  const sampleData = useMemo(() => {
    const data = [];
    const totalRows = Math.min(pipeline.metrics?.record_count || 0, 1000);
    
    for (let i = 0; i < totalRows; i++) {
      data.push({
        id: i + 1,
        name: `Record ${i + 1}`,
        type: ['Chemical', 'Compound', 'Element'][i % 3],
        value: (Math.random() * 1000).toFixed(2),
        status: ['Active', 'Inactive', 'Pending'][i % 3]
      });
    }
    
    return data;
  }, [pipeline.metrics?.record_count]);

  const totalPages = Math.ceil(sampleData.length / rowsPerPage);
  const startIdx = (currentPage - 1) * rowsPerPage;
  const endIdx = Math.min(startIdx + rowsPerPage, sampleData.length);
  const currentData = sampleData.slice(startIdx, endIdx);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  if (sampleData.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500">
        <div className="text-center">
          <span className="material-symbols-rounded text-4xl mb-2">table_chart</span>
          <p>No data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-auto">
        <table className="w-full">
          <thead className="bg-gray-100 sticky top-0">
            <tr>
              <th className="px-3 py-2 text-left text-xs font-bold text-gray-700 border-b border-gray-200">ID</th>
              <th className="px-3 py-2 text-left text-xs font-bold text-gray-700 border-b border-gray-200">Name</th>
              <th className="px-3 py-2 text-left text-xs font-bold text-gray-700 border-b border-gray-200">Type</th>
              <th className="px-3 py-2 text-left text-xs font-bold text-gray-700 border-b border-gray-200">Value</th>
              <th className="px-3 py-2 text-left text-xs font-bold text-gray-700 border-b border-gray-200">Status</th>
            </tr>
          </thead>
          <tbody>
            {currentData.map((row, idx) => (
              <tr key={row.id} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                <td className="px-3 py-2.5 text-sm text-gray-900 border-b border-gray-100">{row.id}</td>
                <td className="px-3 py-2.5 text-sm text-gray-900 border-b border-gray-100">{row.name}</td>
                <td className="px-3 py-2.5 text-sm text-gray-600 border-b border-gray-100">{row.type}</td>
                <td className="px-3 py-2.5 text-sm text-gray-600 border-b border-gray-100">{row.value}</td>
                <td className="px-3 py-2.5 text-sm border-b border-gray-100">
                  <span className={`px-2 py-0.5 rounded text-xs font-semibold ${
                    row.status === 'Active' ? 'bg-green-100 text-green-800' :
                    row.status === 'Inactive' ? 'bg-gray-100 text-gray-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {row.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="border-t border-gray-200 bg-white">
        <div className="flex items-center justify-between px-4 py-2">
          <span className="text-sm text-gray-600">
            Showing {startIdx + 1}-{endIdx} of {sampleData.length} rows
          </span>
          <PaginationControls
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={handlePageChange}
          />
        </div>
      </div>
    </div>
  );
}