import { useMemo } from 'react';

interface DataPreviewTableProps {
  columns: string[];
  rows: Record<string, unknown>[];
  loading?: boolean;
}

function DataPreviewTable({ columns, rows, loading }: DataPreviewTableProps) {
  const displayColumns = useMemo(() => {
    return columns || [];
  }, [columns]);

  const displayRows = useMemo(() => {
    return rows || [];
  }, [rows]);

  if (loading) {
    return (
      <div className="bg-white rounded-2xl shadow-lg p-8 flex items-center justify-center">
        <p className="text-gray-500">Loading preview...</p>
      </div>
    );
  }

  if (displayColumns.length === 0 || displayRows.length === 0) {
    return (
      <div className="bg-white rounded-2xl shadow-lg p-8 flex items-center justify-center">
        <p className="text-gray-500">No data to preview</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
      <div className="overflow-x-auto max-h-96 overflow-y-auto">
        <table className="w-full">
          <thead className="sticky top-0 bg-gray-50 z-10">
            <tr>
              {displayColumns.map((col: string, idx: number) => (
                <th
                  key={`col-${idx}`}
                  className="h-10 px-4 text-left text-sm font-bold text-gray-900 border-b border-gray-200"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {displayRows.map((row: Record<string, unknown>, rowIdx: number) => (
              <tr
                key={`row-${rowIdx}`}
                className={rowIdx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
              >
                {displayColumns.map((col: string, colIdx: number) => (
                  <td
                    key={`cell-${rowIdx}-${colIdx}`}
                    className="px-4 py-2 text-sm text-gray-700 border-b border-gray-100"
                  >
                    {String(row[col] ?? '')}
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

export { DataPreviewTable };
export default DataPreviewTable;