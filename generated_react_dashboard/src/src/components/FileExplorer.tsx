import React, { useState } from 'react';
import { DirectoryNode, FileInfo } from '../types.ts';

interface FileExplorerProps {
  files: DirectoryNode;
  path?: string[];
}

export default function FileExplorer({ files, path = [] }: FileExplorerProps) {
  const [expandedDirs, setExpandedDirs] = useState<Set<string>>(new Set());

  const toggleDir = (dirName: string) => {
    const newExpanded = new Set(expandedDirs);
    if (newExpanded.has(dirName)) {
      newExpanded.delete(dirName);
    } else {
      newExpanded.add(dirName);
    }
    setExpandedDirs(newExpanded);
  };

  const renderFiles = (fileList: FileInfo[], indent: number = 0) => {
    return fileList.map((file, index) => (
      <div
        key={`${file.name}-${index}`}
        className="flex items-center gap-3 py-2 px-4 hover:bg-gray-100 rounded-lg transition-colors"
        style={{ paddingLeft: `${indent * 24 + 16}px` }}
      >
        <span className="material-symbols-rounded text-gray-400 text-lg">description</span>
        <span className="flex-1 text-sm text-gray-700">{file.name}</span>
        <span className="text-xs font-mono text-gray-500">{file.size_human}</span>
      </div>
    ));
  };

  const renderDirectory = (node: DirectoryNode, dirName: string, indent: number = 0) => {
    const isExpanded = expandedDirs.has(dirName);
    const hasSubdirs = Object.keys(node.subdirs || {}).length > 0;
    const hasFiles = (node.files || []).length > 0;

    return (
      <div key={dirName}>
        <div
          className="flex items-center gap-3 py-2 px-4 hover:bg-gray-100 rounded-lg cursor-pointer transition-colors"
          style={{ paddingLeft: `${indent * 24 + 16}px` }}
          onClick={() => toggleDir(dirName)}
        >
          <span
            className={`material-symbols-rounded text-gray-600 text-lg transition-transform ${
              isExpanded ? 'rotate-90' : ''
            }`}
          >
            arrow_right
          </span>
          <span className="material-symbols-rounded text-primary text-lg">folder</span>
          <span className="flex-1 text-sm font-medium text-gray-900">{dirName}</span>
          <span className="text-xs text-gray-500">
            {node.file_count} {node.file_count === 1 ? 'file' : 'files'}
          </span>
        </div>

        {isExpanded && (
          <div>
            {hasFiles && renderFiles(node.files, indent + 1)}
            {hasSubdirs &&
              Object.entries(node.subdirs).map(([subDirName, subNode]) =>
                renderDirectory(subNode, subDirName, indent + 1)
              )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <span className="material-symbols-rounded text-gray-600">folder_open</span>
          <span className="font-medium text-gray-900">File Structure</span>
        </div>
      </div>
      <div className="max-h-96 overflow-y-auto p-2">
        {files.files && files.files.length > 0 && renderFiles(files.files, 0)}
        {files.subdirs &&
          Object.entries(files.subdirs).map(([dirName, node]) =>
            renderDirectory(node, dirName, 0)
          )}
        {!files.files?.length && !Object.keys(files.subdirs || {}).length && (
          <div className="text-center py-8 text-gray-500">
            <span className="material-symbols-rounded text-4xl mb-2">folder_off</span>
            <p>No files found</p>
          </div>
        )}
      </div>
    </div>
  );
}