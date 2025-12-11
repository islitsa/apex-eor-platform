import { Pipeline } from '../types.ts';

interface PipelineHealthPanelProps {
  pipeline: Pipeline;
}

export function PipelineHealthPanel({ pipeline }: PipelineHealthPanelProps) {
  const stages = pipeline.stages ?? [];

  const getStageIcon = (stageName: string): string => {
    const name = String(stageName || '').toLowerCase();
    if (name.includes('download')) return 'download';
    if (name.includes('transform')) return 'transform';
    if (name.includes('code')) return 'code';
    return 'check_circle';
  };

  const getStageColor = (status: string): string => {
    const statusStr = String(status || '').toLowerCase();
    if (statusStr === 'completed' || statusStr === 'success') return 'text-green-600';
    if (statusStr === 'running' || statusStr === 'processing') return 'text-blue-600';
    if (statusStr === 'failed' || statusStr === 'error') return 'text-red-600';
    return 'text-gray-400';
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Pipeline Health</h3>
      <div className="space-y-4">
        {stages.map((stage, index) => (
          <div key={index} className="flex items-center gap-3">
            <span className={`material-symbols-rounded ${getStageColor(stage.status)}`}>
              {stage.status === 'completed' || stage.status === 'success' 
                ? 'check_circle' 
                : getStageIcon(stage.name)}
            </span>
            <div className="flex-1">
              <div className="text-sm font-medium text-gray-900">{stage.name}</div>
              <div className="text-xs text-gray-500 capitalize">{stage.status}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}