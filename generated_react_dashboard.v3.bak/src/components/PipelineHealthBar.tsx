import { Stage } from '../types.ts';

interface PipelineHealthBarProps {
  stages: Stage[];
}

export function PipelineHealthBar({ stages }: PipelineHealthBarProps) {
  const getStageColor = (status: string): string => {
    const statusLower = String(status || '').toLowerCase();
    if (statusLower === 'completed' || statusLower === 'success') return 'bg-green-500';
    if (statusLower === 'processing' || statusLower === 'running') return 'bg-blue-500';
    if (statusLower === 'failed' || statusLower === 'error') return 'bg-red-500';
    return 'bg-gray-400';
  };

  const getStageIcon = (status: string): string => {
    const statusLower = String(status || '').toLowerCase();
    if (statusLower === 'completed' || statusLower === 'success') return 'check_circle';
    if (statusLower === 'processing' || statusLower === 'running') return 'pending';
    if (statusLower === 'failed' || statusLower === 'error') return 'error';
    return 'radio_button_unchecked';
  };

  const stagesList = stages ?? [];

  if (stagesList.length === 0) {
    return null;
  }

  return (
    <div className="bg-white rounded-2xl shadow-md p-6">
      <h3 className="text-lg font-bold text-gray-900 mb-4">Pipeline Health</h3>
      <div className="space-y-3">
        {stagesList.map((stage, index) => (
          <div key={index} className="flex items-center gap-3">
            <span className={`material-symbols-rounded text-2xl ${
              getStageColor(stage.status).replace('bg-', 'text-')
            }`}>
              {getStageIcon(stage.status)}
            </span>
            <div className="flex-1">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-900">
                  {String(stage.name || 'Unknown Stage')}
                </span>
                <span className={`text-xs font-medium px-2 py-1 rounded ${
                  getStageColor(stage.status)
                } text-white`}>
                  {String(stage.status || 'unknown').toUpperCase()}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}