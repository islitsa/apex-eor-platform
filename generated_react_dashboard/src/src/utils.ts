import type { Pipeline, StageInfo } from './types.ts';

export function formatNumber(num: number): string {
  return new Intl.NumberFormat('en-US').format(num);
}

export function getStatusColor(status: string): string {
  switch (status) {
    case 'complete':
    case 'processed':
      return 'bg-green-100 text-green-800';
    case 'processing':
      return 'bg-amber-100 text-amber-800';
    case 'failed':
      return 'bg-red-100 text-red-800';
    case 'not_started':
    case 'pending':
      return 'bg-gray-100 text-gray-600';
    default:
      return 'bg-gray-100 text-gray-600';
  }
}

export function extractStages(pipeline: Pipeline): StageInfo[] {
  const stageOrder = ['download', 'extraction', 'parsing', 'validation', 'loading'];
  const stages: StageInfo[] = [];

  stageOrder.forEach(stageName => {
    if (pipeline.stages[stageName]) {
      stages.push({
        name: stageName,
        status: pipeline.stages[stageName] as any,
        displayName: stageName.charAt(0).toUpperCase() + stageName.slice(1)
      });
    }
  });

  return stages;
}

export function getParsedFilesCount(pipeline: Pipeline): number {
  return parseInt(pipeline.stages.parsed_files || '0', 10);
}

export function getDataTypeFromId(id: string): string {
  const parts = id.split('_');
  if (parts.length > 1) {
    return parts.slice(1).map(p => p.charAt(0).toUpperCase() + p.slice(1)).join(' ');
  }
  return '';
}