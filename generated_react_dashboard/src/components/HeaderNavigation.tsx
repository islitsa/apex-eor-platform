import React from 'react';

interface Props {
  sourceCount: number;
  totalFiles: number;
  totalRecords: number;
}

export default function HeaderNavigation({ sourceCount, totalFiles, totalRecords }: Props) {
  return (
    <header className="bg-white border-b border-gray-200 h-16 flex items-center px-8">
      <div className="flex items-center gap-3">
        <span className="material-symbols-rounded text-blue-600 text-3xl">database</span>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Chemical Data Dashboard</h1>
        </div>
      </div>
      <div className="ml-auto flex items-center gap-6 text-sm">
        <div className="flex items-center gap-2">
          <span className="material-symbols-rounded text-gray-500 text-xl">science</span>
          <span className="text-gray-600">{sourceCount} {sourceCount === 1 ? 'Source' : 'Sources'}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="material-symbols-rounded text-gray-500 text-xl">folder</span>
          <span className="text-gray-600">{Number(totalFiles || 0).toLocaleString()} Files</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="material-symbols-rounded text-gray-500 text-xl">description</span>
          <span className="text-gray-600">{Number(totalRecords || 0).toLocaleString()} Records</span>
        </div>
      </div>
    </header>
  );
}