export interface Pipeline {
  id: string;
  name: string;
  display_name: string;
  status: string;
  metrics: {
    file_count: number;
    record_count: number;
    data_size: string;
  };
  stages: Stage[];
  files: FileNode[];
}

export interface Stage {
  name: string;
  status: string;
  file_count?: number;
  record_count?: number;
  last_updated?: string;
}

export interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'directory' | 'folder';
  subdirs?: Record<string, FileNode>;
  files?: FileNode[];
  children?: FileNode[];
  size?: number;
  file_count?: number;
}

export interface PipelinesResponse {
  pipelines: Pipeline[];
  summary: {
    total_files: number;
    total_records: number;
    total_size_mb: number;
  };
}

export interface DataRecord {
  [key: string]: any;
}