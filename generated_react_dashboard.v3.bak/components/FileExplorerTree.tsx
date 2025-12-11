import { useState, useMemo, useCallback } from 'react';
import { FileNode } from '../types.ts';

interface FileExplorerTreeProps {
  nodes: FileNode[];
  onFileSelect?: (filePath: string) => void;
  selectedFile?: string | null;
}

interface TreeNodeProps {
  node: FileNode;
  level: number;
  onFileSelect?: (filePath: string) => void;
  selectedFile?: string | null;
}

function TreeNode({ node, level, onFileSelect, selectedFile }: TreeNodeProps) {
  const [isExpanded, setIsExpanded] = useState(level === 0);

  const isDirectory = useMemo(() => {
    return node.type === 'directory';
  }, [node.type]);

  const hasChildren = useMemo(() => {
    return node.children && node.children.length > 0;
  }, [node.children]);

  const isSelected = useMemo(() => {
    return selectedFile === node.path;
  }, [selectedFile, node.path]);

  const handleClick = useCallback(() => {
    if (isDirectory) {
      setIsExpanded((prev: boolean) => !prev);
    } else {
      if (onFileSelect) {
        onFileSelect(node.path);
      }
    }
  }, [isDirectory, node.path, onFileSelect]);

  return (
    <div>
      <div
        className={`flex items-center gap-2 py-1.5 px-3 cursor-pointer hover:bg-gray-100 rounded ${
          isSelected ? 'bg-blue-50' : ''
        }`}
        style={{ paddingLeft: `${level * 20 + 12}px` }}
        onClick={handleClick}
      >
        {isDirectory && hasChildren && (
          <span className="material-symbols-rounded text-lg text-gray-600">
            {isExpanded ? 'expand_more' : 'chevron_right'}
          </span>
        )}
        {isDirectory && !hasChildren && (
          <span className="material-symbols-rounded text-lg text-gray-400">folder</span>
        )}
        {!isDirectory && (
          <span className="material-symbols-rounded text-lg text-gray-400">description</span>
        )}
        <span className={`text-sm ${isSelected ? 'font-semibold text-blue-700' : 'text-gray-700'}`}>
          {node.name}
        </span>
      </div>
      {isDirectory && isExpanded && hasChildren && (
        <div>
          {node.children.map((child: FileNode, idx: number) => (
            <TreeNode
              key={`${child.path}-${idx}`}
              node={child}
              level={level + 1}
              onFileSelect={onFileSelect}
              selectedFile={selectedFile}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function FileExplorerTree({ nodes, onFileSelect, selectedFile }: FileExplorerTreeProps) {
  if (!nodes || nodes.length === 0) {
    return (
      <div className="bg-white rounded-2xl shadow-lg p-6">
        <p className="text-gray-500 text-center">No files available</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl shadow-lg p-4 max-h-96 overflow-y-auto">
      {nodes.map((node: FileNode, idx: number) => (
        <TreeNode
          key={`${node.path}-${idx}`}
          node={node}
          level={0}
          onFileSelect={onFileSelect}
          selectedFile={selectedFile}
        />
      ))}
    </div>
  );
}

export { FileExplorerTree };
export default FileExplorerTree;