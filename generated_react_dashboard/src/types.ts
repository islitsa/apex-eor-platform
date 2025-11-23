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
  stages: { name: string; status: string }[];
  files: FileNode[];
}

export interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'directory' | 'folder';
  subdirs?: Record<string, FileNode>;
  files?: FileNode[];
  children?: FileNode[];
  size?: number;
  size_bytes?: number;
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

export interface StageStatus {
  name: string;
  status: string;
  count: number;
}