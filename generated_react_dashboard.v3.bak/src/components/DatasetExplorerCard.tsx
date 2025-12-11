import React from 'react';
import { FileNode } from '../types.ts';
import { FileTreeRow } from './FileTreeRow.tsx';

interface DatasetExplorerCardProps {
  title: string;
  files: FileNode[];
  onFileSelect?: (filePath: string) => void;
  selectedFile?: string | null;
}

export function DatasetExplorerCard({
  title,
  files,
  onFileSelect,
  selectedFile,
}: DatasetExplorerCardProps) {
  const [isExpanded, setIsExpanded] = React.useState(true);

  const normalizeNode = (node: any): FileNode => {
    let children: FileNode[] = [];
    if (node.children) {
      children = node.children.map(normalizeNode);
    } else {
      if (node.subdirs) {
        Object.values(node.subdirs).forEach((d: any) => children.push(normalizeNode(d)));
      }
      if (node.files) {
        node.files.forEach((f: any) =>
          children.push({ ...f, type: 'file', children: [] })
        );
      }
    }
    return {
      name: node.name,
      path: node.path,
      type: node.type === 'folder' ? 'directory' : node.type || 'directory',
      children,
      file_count: node.file_count,
      size: node.size_bytes || node.size,
    };
  };

  const normalizedFiles = React.useMemo(() => {
    return files.map(normalizeNode);
  }, [files]);

  return (
    <div className="bg-white rounded-lg shadow-sm overflow-hidden">
      <div
        className="flex items-center gap-3 p-6 cursor-pointer hover:bg-gray-50"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <span className="material-symbols-rounded text-blue-600 text-2xl">science</span>
        <h2 className="text-xl font-bold text-gray-900 flex-1">{title}</h2>
        <span className="material-symbols-rounded text-gray-600">
          {isExpanded ? 'expand_less' : 'expand_more'}
        </span>
      </div>
      {isExpanded && (
        <div className="border-t border-gray-200">
          {normalizedFiles.map((file, idx) => (
            <FileTreeRow
              key={`${file.path}-${idx}`}
              node={file}
              level={0}
              onFileSelect={onFileSelect}
              selectedFile={selectedFile}
            />
          ))}
        </div>
      )}
    </div>
  );
}