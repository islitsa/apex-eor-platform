import { useState, useEffect } from 'react';
import { PipelinesResponse, FilePreviewResponse } from './types.ts';

const API_BASE_URL = 'http://localhost:8000/api';

export function usePipelines() {
  const [data, setData] = useState<PipelinesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPipelines = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`${API_BASE_URL}/pipelines`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch pipelines');
      } finally {
        setLoading(false);
      }
    };

    fetchPipelines();
  }, []);

  return { data, loading, error };
}

export function useFilePreview(
  pipelineId: string | null,
  filePath: string | null,
  page: number = 1,
  pageSize: number = 100
) {
  const [data, setData] = useState<FilePreviewResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!pipelineId || !filePath) {
      setData(null);
      setLoading(false);
      return;
    }

    const fetchPreview = async () => {
      setLoading(true);
      setError(null);
      try {
        const params = new URLSearchParams({
          file_path: filePath,
          page: String(page),
          page_size: String(pageSize),
        });
        const response = await fetch(
          `${API_BASE_URL}/pipelines/${encodeURIComponent(pipelineId)}/files/preview?${params}`
        );
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch file preview');
      } finally {
        setLoading(false);
      }
    };

    fetchPreview();
  }, [pipelineId, filePath, page, pageSize]);

  return { data, loading, error };
}