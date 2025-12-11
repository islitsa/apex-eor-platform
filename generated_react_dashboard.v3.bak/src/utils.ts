import { FileNode } from './types.ts';

export function formatBytes(bytes: number | null | undefined): string {
  if (!bytes || bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
}

export function formatNumber(num: number | null | undefined): string {
  if (!num && num !== 0) return '0';
  return num.toLocaleString();
}

export function normalizeFileNode(node: any): FileNode {
  let children: FileNode[] = [];
  
  if (node.children) {
    children = node.children.map(normalizeFileNode);
  } else {
    if (node.subdirs) {
      Object.values(node.subdirs).forEach((d: any) => {
        children.push(normalizeFileNode(d));
      });
    }
    if (node.files) {
      node.files.forEach((f: any) => {
        children.push({
          name: f.name || f,
          path: f.path || f,
          type: 'file',
          children: [],
          size: f.size_bytes || f.size
        });
      });
    }
  }

  return {
    name: node.name,
    path: node.path,
    type: node.type === 'folder' ? 'directory' : (node.type || 'directory'),
    children,
    file_count: node.file_count,
    size: node.size_bytes || node.size
  };
}