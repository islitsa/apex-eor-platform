import React, { useState } from 'react';
import { Pipeline, FileNode } from '../types';

interface InlineFileExplorerProps {
  pipeline: Pipeline;
}

export default function InlineFileExplorer({ pipeline }: InlineFileExplorerProps) {
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set());

  const toggleFolder = (path: string) => {
    const newExpanded = new Set(expandedFolders);
    if (newExpanded.has(path)) {
      newExpanded.delete(path);
    } else {
      newExpanded.add(path);
    }
    setExpandedFolders(newExpanded);
  };

  const buildFileTree = (): FileNode[] => {
    const tree: FileNode[] = [];
    
    // Add stages as folders
    const stages = pipeline.stages || [];
    stages.forEach((stage: any) => {
      const stageName = String(stage.name || 'unknown');
      const stageStatus = String(stage.status || 'unknown');
      
      // Skip metadata entries
      if (stageName.includes('_at') || stageName.includes('_count')) return;

      tree.push({
        name: stageName,
        type: 'folder',
        path: stageName,
        size: Number(stage.size_bytes || 0),
        modified: String(stage.last_modified || ''),
        children: []
      });
    });

    return tree;
  };

  const formatBytes = (bytes: number): string => {
    const mb = Number(bytes || 0) / (1024 * 1024);
    if (mb < 1) return `${(mb * 1024).toFixed(0)} KB`;
    if (mb < 1024) return `${mb.toFixed(1)} MB`;
    return `${(mb / 1024).toFixed(2)} GB`;
  };

  const formatDate = (dateStr: string): string => {
    if (!dateStr) return 'N/A';
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        year: 'numeric' 
      });
    } catch {
      return 'N/A';
    }
  };

  const fileTree = buildFileTree();

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <div className="bg-gray-50 px-4 py-2 border-b border-gray-200">
        <div className="flex items-center gap-2 text-sm font-medium text-gray-700">
          <span className="material-symbols-rounded text-lg">folder_open</span>
          <span>File Structure</span>
        </div>
      </div>
      
      <div className="max-h-64 overflow-y-auto">
        {fileTree.length === 0 ? (
          <div className="p-4 text-center text-gray-500 text-sm">
            No files available
          </div>
        ) : (
          <div>
            {fileTree.map((node, index) => (
              <div key={index}>
                <div 
                  className="flex items-center justify-between px-4 py-2 hover:bg-gray-50 cursor-pointer border-b border-gray-100"
                  style={{ height: '40px', paddingLeft: '24px' }}
                  onClick={() => toggleFolder(node.path)}
                >
                  <div className="flex items-center gap-3 flex-1">
                    <span className="material-symbols-rounded text-gray-600 text-xl">
                      {node.type === 'folder' ? 'folder' : 'description'}
                    </span>
                    <span className="text-sm text-gray-900 font-medium">
                      {node.name}
                    </span>
                  </div>
                  <div className="flex items-center gap-6 text-xs text-gray-500">
                    <span className="w-20 text-right">{formatBytes(node.size)}</span>
                    <span className="w-24 text-right">{formatDate(node.modified)}</span>
                    {node.type === 'folder' && (
                      <span className="material-symbols-rounded text-lg">
                        {expandedFolders.has(node.path) ? 'expand_less' : 'expand_more'}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}