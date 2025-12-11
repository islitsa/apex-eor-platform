import React from 'react';
import { FileNode } from '../types.ts';

interface FileTreeRowProps {
  node: FileNode;
  level: number;
  onFileSelect?: (filePath: string) => void;
  selectedFile?: string | null;
}

export function FileTreeRow({ node, level, onFileSelect, selectedFile }: FileTreeRowProps) {
  const [isExpanded, setIsExpanded] = React.useState(false);
  const isDirectory = node.type === 'directory';
  const hasChildren = node.children && node.children.length > 0;
  const isSelected = selectedFile === node.path;

  const handleClick = () => {
    if (isDirectory) {
      setIsExpanded(!isExpanded);
    } else {
      onFileSelect?.(node.path);
    }
  };

  const formatSize = (bytes: number | undefined) => {
    if (!bytes) return '';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
  };

  return (
    <>
      <div
        className={`flex items-center h-11 cursor-pointer hover:bg-gray-50 ${
          isSelected ? 'bg-blue-50' : ''
        }`}
        style={{ paddingLeft: `${16 + level * 16}px` }}
        onClick={handleClick}
      >
        <span className="material-symbols-rounded text-gray-600 text-xl mr-2">
          {isDirectory ? (isExpanded ? 'folder_open' : 'folder') : 'insert_drive_file'}
        </span>
        <span className="text-sm font-medium text-gray-900 flex-1">{node.name}</span>
        {node.size !== undefined && (
          <span className="text-xs text-gray-500 mr-4">{formatSize(node.size)}</span>
        )}
        {node.file_count !== undefined && isDirectory && (
          <span className="text-xs text-gray-500 mr-4">{node.file_count} files</span>
        )}
      </div>
      {isDirectory && isExpanded && hasChildren && (
        <>
          {node.children.map((child, idx) => (
            <FileTreeRow
              key={`${child.path}-${idx}`}
              node={child}
              level={level + 1}
              onFileSelect={onFileSelect}
              selectedFile={selectedFile}
            />
          ))}
        </>
      )}
    </>
  );
}