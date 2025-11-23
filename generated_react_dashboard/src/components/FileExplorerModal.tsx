import React, { useState } from 'react';
import type { Pipeline, SubDirectory, FileInfo } from '../types.ts';

interface FileExplorerModalProps {
  pipeline: Pipeline;
  onClose: () => void;
}

export function FileExplorerModal({ pipeline, onClose }: FileExplorerModalProps) {
  const [expandedDirs, setExpandedDirs] = useState<Set<string>>(new Set(['root']));

  const toggleDir = (path: string) => {
    setExpandedDirs(prev => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return next;
    });
  };

  const renderFiles = (files: FileInfo[], indent: number = 0) => {
    return files.map((file, idx) => (
      <div 
        key={`${file.name}-${idx}`}
        className="flex items-center gap-2 py-2 px-3 hover:bg-gray-50 rounded"
        style={{ paddingLeft: `${indent * 24 + 12}px` }}
      >
        <span className="material-symbols-rounded text-gray-400 text-[18px]">description</span>
        <span className="text-sm text-gray-700 flex-1">{file.name}</span>
        <span className="text-xs text-gray-500">{file.size_human}</span>
      </div>
    ));
  };

  const renderSubdirs = (subdirs: Record<string, SubDirectory>, parentPath: string = '', indent: number = 0) => {
    return Object.entries(subdirs).map(([name, subdir]) => {
      const path = parentPath ? `${parentPath}/${name}` : name;
      const isExpanded = expandedDirs.has(path);

      return (
        <div key={path}>
          <button
            onClick={() => toggleDir(path)}
            className="w-full flex items-center gap-2 py-2 px-3 hover:bg-gray-100 rounded transition-colors"
            style={{ paddingLeft: `${indent * 24 + 12}px` }}
          >
            <span className="material-symbols-rounded text-blue-600 text-[18px]">
              {isExpanded ? 'folder_open' : 'folder'}
            </span>
            <span className="text-sm font-medium text-gray-900 flex-1 text-left">{name}</span>
            <span className="text-xs text-gray-500">{subdir.file_count} files</span>
            <span className="material-symbols-rounded text-gray-400 text-[16px]">
              {isExpanded ? 'expand_more' : 'chevron_right'}
            </span>
          </button>
          
          {isExpanded && (
            <div>
              {subdir.subdirs && Object.keys(subdir.subdirs).length > 0 && (
                renderSubdirs(subdir.subdirs, path, indent + 1)
              )}
              {subdir.files && subdir.files.length > 0 && (
                renderFiles(subdir.files, indent + 1)
              )}
            </div>
          )}
        </div>
      );
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <span className="material-symbols-rounded text-blue-600 text-[28px]">folder_open</span>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">File Explorer</h2>
              <p className="text-sm text-gray-600">{pipeline.name}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-10 h-10 rounded-full hover:bg-gray-100 flex items-center justify-center transition-colors"
          >
            <span className="material-symbols-rounded text-gray-600 text-[24px]">close</span>
          </button>
        </div>

        {/* File Tree */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="bg-gray-50 rounded-lg p-4">
            {pipeline.files.subdirs && Object.keys(pipeline.files.subdirs).length > 0 ? (
              renderSubdirs(pipeline.files.subdirs)
            ) : (
              <div className="text-center py-8">
                <span className="material-symbols-rounded text-gray-300 text-[48px] block mb-2">
                  folder_off
                </span>
                <p className="text-gray-500">No files found</p>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200 bg-gray-50 rounded-b-2xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4 text-sm text-gray-600">
              <span>Total Size: <strong className="text-gray-900">{pipeline.data_size}</strong></span>
            </div>
            <button
              onClick={onClose}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}