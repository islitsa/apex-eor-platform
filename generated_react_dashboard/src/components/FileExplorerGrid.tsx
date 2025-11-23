import React from 'react';
import type { FileInfo } from '../types';

interface FileExplorerGridProps {
  files: FileInfo[];
}

export default function FileExplorerGrid({ files }: FileExplorerGridProps) {
  if (!files || files.length === 0) {
    return (
      <div className="text-center py-8">
        <span className="material-symbols-rounded text-gray-400 text-5xl">folder_off</span>
        <p className="mt-3 text-gray-600">No files available</p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center gap-2 mb-4">
        <span className="material-symbols-rounded text-gray-700">folder</span>
        <h3 className="text-lg font-semibold text-gray-900">
          Files ({files.length})
        </h3>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {files.map((file, index) => (
          <FileItem key={`${file.path}-${index}`} file={file} />
        ))}
      </div>
    </div>
  );
}

interface FileItemProps {
  file: FileInfo;
}

function FileItem({ file }: FileItemProps) {
  const sizeInMB = file.size_bytes / (1024 * 1024);
  const displaySize = sizeInMB >= 1
    ? `${Number(sizeInMB || 0).toFixed(2)} MB`
    : `${Number((file.size_bytes / 1024) || 0).toFixed(2)} KB`;

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 hover:bg-gray-50 hover:border-[#FF6B35] transition-all duration-200 cursor-pointer">
      <div className="flex items-start gap-3">
        <span className="material-symbols-rounded text-[#FF6B35] text-2xl flex-shrink-0">
          description
        </span>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900 truncate" title={file.name}>
            {file.name}
          </p>
          <div className="flex items-center gap-2 mt-1">
            <span className="material-symbols-rounded text-gray-400 text-xs">storage</span>
            <p className="text-xs text-gray-500">{displaySize}</p>
          </div>
          {file.stage && (
            <div className="mt-1">
              <span className="inline-block px-2 py-0.5 bg-gray-100 text-gray-700 text-xs rounded">
                {String(file.stage || '').replace(/_/g, ' ')}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}