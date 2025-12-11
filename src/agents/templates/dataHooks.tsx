/**
 * CANONICAL DATA HOOKS - DO NOT REGENERATE
 *
 * This file is a battle-tested template that connects React components
 * to the APEX EOR backend API. The React Developer agent should NOT
 * regenerate this file - it should be copied as-is.
 *
 * API Contract:
 * - GET /api/pipelines - List all pipelines
 * - GET /api/pipelines/{id}/files/preview - Preview file contents
 */

import { useState, useEffect } from 'react';

const API_BASE = 'http://localhost:8000/api';

// ============================================================
// TYPE DEFINITIONS - Match exact API response shapes
// ============================================================

export interface Pipeline {
  id: string;
  display_name: string;
  status: string;
  stages?: PipelineStage[];
  files?: FileNode[];
  metrics?: PipelineMetrics;
}

export interface PipelineStage {
  name: string;
  status: string;
  file_count?: number;
}

export interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'directory';
  size?: number;
  file_count?: number;
  children?: FileNode[];
}

export interface PipelineMetrics {
  file_count?: number;
  record_count?: number;
  data_size?: number;
}

export interface PipelinesResponse {
  success: boolean;
  pipelines: Pipeline[];
}

// NOTE: API returns camelCase for file preview response
export interface FilePreviewResponse {
  columns: string[];
  rows: Record<string, unknown>[];
  totalRows: number;   // camelCase - matches API
  page: number;
  pageSize: number;    // camelCase - matches API
}

// ============================================================
// HOOKS
// ============================================================

/**
 * Fetch all pipelines from the API
 */
export function usePipelines() {
  const [data, setData] = useState<PipelinesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchPipelines() {
      try {
        setLoading(true);
        setError(null);
        const response = await fetch(`${API_BASE}/pipelines`);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        const json = await response.json();
        if (!cancelled) {
          setData(json);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err : new Error(String(err)));
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    fetchPipelines();

    return () => {
      cancelled = true;
    };
  }, []);

  return { data, loading, error };
}

/**
 * Fetch file preview with pagination
 *
 * CRITICAL: This hook uses the CORRECT endpoint and parameters:
 * - Endpoint: /api/pipelines/{id}/files/preview (NOT /preview, NOT /data)
 * - Parameter: page_size (NOT limit)
 * - Response: totalRows (camelCase, NOT total_rows)
 *
 * @param pipelineId - Pipeline ID (e.g., "fracfocus_chemical_data")
 * @param filePath - Relative file path within pipeline (e.g., "Extracted/file.csv")
 * @param page - Page number (1-indexed)
 * @param pageSize - Rows per page
 */
export function useFilePreview(
  pipelineId: string | null,
  filePath: string | null,
  page: number = 1,
  pageSize: number = 100
) {
  const [data, setData] = useState<FilePreviewResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    // Don't fetch if missing required params
    if (!pipelineId || !filePath) {
      setData(null);
      return;
    }

    let cancelled = false;

    async function fetchPreview() {
      try {
        setLoading(true);
        setError(null);

        // CRITICAL: Use correct endpoint and parameter names
        const params = new URLSearchParams({
          file_path: filePath!,
          page: String(page),
          page_size: String(pageSize),  // NOT "limit"
        });

        const response = await fetch(
          `${API_BASE}/pipelines/${encodeURIComponent(pipelineId!)}/files/preview?${params}`
        );

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const json = await response.json();
        if (!cancelled) {
          setData(json);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err : new Error(String(err)));
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    fetchPreview();

    return () => {
      cancelled = true;
    };
  }, [pipelineId, filePath, page, pageSize]);

  return { data, loading, error };
}

// ============================================================
// UTILITY FUNCTIONS
// ============================================================

/**
 * Normalize file node structure for consistent rendering
 */
export function normalizeFileNode(node: FileNode): FileNode {
  return {
    ...node,
    type: node.type || (node.children ? 'directory' : 'file'),
    children: node.children?.map(normalizeFileNode),
  };
}

/**
 * Format bytes to human-readable string
 */
export function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}
