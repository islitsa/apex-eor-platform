import React from 'react';
import type { FilePreviewData } from '../types';

interface Props {
  data: FilePreviewData;
}

export default function DataTablePreview({ data }: Props) {
  if (!data || !data.columns || data.columns.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p className="text-sm">No data to display</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-xs">
        <thead className="bg-gray-100 sticky top-0">
          <tr>
            {data.columns.map((col, idx) => (
              <th
                key={idx}
                className="px-3 py-2 text-left font-semibold text-gray-700 border-b border-gray-200"
              >
                <div className="truncate" title={String(col)}>
                  {String(col)}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="font-mono">
          {data.rows.map((row, rowIdx) => (
            <tr
              key={rowIdx}
              className={rowIdx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
              style={{ height: '40px' }}
            >
              {row.map((cell, cellIdx) => (
                <td
                  key={cellIdx}
                  className="px-3 py-2 border-b border-gray-100 text-gray-800"
                >
                  <div className="truncate" title={String(cell ?? '')}>
                    {cell !== null && cell !== undefined ? String(cell) : '—'}
                  </div>
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}