export interface PipelineMetrics {
  file_count: number;
  record_count: number;
  data_size: string;
}

export interface PipelineStage {
  name: string;
  status: string;
  file_count?: number;
  record_count?: number;
}

export interface Pipeline {
  id: string;
  name: string;
  display_name: string;
  status: string;
  metrics: PipelineMetrics;
  stages: PipelineStage[];
  files: Record<string, any>;
}

export interface PipelineResponse {
  pipelines: Pipeline[];
  summary: {
    total_pipelines: number;
    total_records: number;
    total_size: string;
  };
}