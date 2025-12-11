export interface Pipeline {
  id: string;
  name: string;
  display_name: string;
  status: string;
  metrics: {
    file_count: number;
    record_count: number;
    data_size: number;
  };
  stages: PipelineStage[];
  files: FileNode[];
}

export interface PipelineStage {
  name: string;
  status: string;
}

export interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'directory';
  children: FileNode[];
  file_count?: number;
  size?: number;
  size_bytes?: number;
  subdirs?: Record<string, any>;
  files?: any[];
}

export interface PipelinesResponse {
  success: boolean;
  pipelines: Pipeline[];
  summary: {
    total_pipelines: number;
    total_files: number;
    total_records: number;
    total_size: number;
  };
}

export interface FilePreviewResponse {
  columns: string[];
  rows: Record<string, unknown>[];
  totalRows: number;
  page: number;
  pageSize: number;
}