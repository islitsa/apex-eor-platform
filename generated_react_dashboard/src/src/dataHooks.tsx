import { useState, useEffect } from 'react';
import { PipelineResponse } from './types.ts';

const API_BASE_URL = 'http://localhost:8000';

export function usePipelines() {
  const [data, setData] = useState<PipelineResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPipelines = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${API_BASE_URL}/api/pipelines`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        setData(result);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch pipelines');
        setData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchPipelines();
  }, []);

  return { data, loading, error };
}