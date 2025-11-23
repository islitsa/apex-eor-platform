import React, { useState } from 'react';
import { Pipeline, DirectoryInfo } from '../types.ts';

interface FileTreeProps {
  pipeline: Pipeline;
  onFileSelect: (filePath: string) => void;
  selectedFile: string | null;
}

interface TreeNodeProps {
  name: string;
  directory: DirectoryInfo;
  path: string;
  level: number;
  onFileSelect: (filePath: string) => void;
  selectedFile: string | null;
}

function TreeNode({ name, directory, path, level, onFileSelect, selectedFile }: TreeNodeProps) {
  const [isOpen, setIsOpen] = useState(true);
  const hasSubdirs = directory.subdirs && Object.keys(directory.subdirs).length > 0;
  const hasFiles = directory.files && directory.files.length > 0;

  return (
    <div>
      <div
        className="flex items-center gap-2 h-10 hover:bg-surface-container rounded cursor-pointer"
        style={{ paddingLeft: `${level * 16}px` }}
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className="material-symbols-rounded text-primary text-xl">
          {isOpen ? 'folder_open' : 'folder'}
        </span>
        <span className="text-sm font-medium text-on-surface">{name}</span>
        <span className="text-xs text-on-surface-variant ml-auto mr-2">
          {directory.file_count} files
        </span>
      </div>

      {isOpen && hasSubdirs && (
        <div>
          {Object.entries(directory.subdirs!).map(([subdirName, subdir]) => (
            <TreeNode
              key={subdirName}
              name={subdirName}
              directory={subdir}
              path={`${path}/${subdirName}`}
              level={level + 1}
              onFileSelect={onFileSelect}
              selectedFile={selectedFile}
            />
          ))}
        </div>
      )}

      {isOpen && hasFiles && (
        <div>
          {directory.files.map((file, idx) => {
            const filePath = `${path}/${file.name}`;
            const isSelected = selectedFile === filePath;
            
            return (
              <div
                key={idx}
                className={`flex items-center gap-2 h-10 hover:bg-surface-container rounded cursor-pointer ${
                  isSelected ? 'bg-primary-container' : ''
                }`}
                style={{ paddingLeft: `${(level + 1) * 16}px` }}
                onClick={() => onFileSelect(filePath)}
              >
                <span className="material-symbols-rounded text-primary text-xl">
                  check_circle
                </span>
                <span className="text-sm text-on-surface flex-1">{file.name}</span>
                <span className="text-xs text-on-surface-variant mr-2">
                  {file.size_human}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default function FileTree({ pipeline, onFileSelect, selectedFile }: FileTreeProps) {
  if (!pipeline.files.subdirs) {
    return (
      <div className="text-sm text-on-surface-variant p-4">
        No file structure available
      </div>
    );
  }

  return (
    <div className="border border-outline-variant rounded-lg p-4">
      <div className="flex items-center gap-2 mb-4">
        <span className="material-symbols-rounded text-primary">folder_open</span>
        <h4 className="text-base font-bold text-on-surface">File Structure</h4>
      </div>
      
      <div className="space-y-1">
        {Object.entries(pipeline.files.subdirs).map(([dirName, directory]) => (
          <TreeNode
            key={dirName}
            name={dirName}
            directory={directory}
            path={dirName}
            level={0}
            onFileSelect={onFileSelect}
            selectedFile={selectedFile}
          />
        ))}
      </div>
    </div>
  );
}