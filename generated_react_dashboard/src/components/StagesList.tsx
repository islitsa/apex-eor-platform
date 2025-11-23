import React from 'react';

interface Stage {
  name: string;
  status: string;
}

interface StagesListProps {
  stages: Stage[];
}

export default function StagesList({ stages }: StagesListProps) {
  const getStageIcon = (name: string): string => {
    const nameLower = String(name || '').toLowerCase();
    if (nameLower.includes('download')) return 'download';
    if (nameLower.includes('extract')) return 'folder_zip';
    if (nameLower.includes('pars')) return 'code';
    if (nameLower.includes('validat')) return 'check_circle';
    if (nameLower.includes('load')) return 'upload';
    return 'settings';
  };

  const getStatusColor = (status: string): string => {
    const statusLower = String(status || '').toLowerCase();
    if (statusLower === 'complete') return 'text-green-600 bg-green-50';
    if (statusLower === 'processing' || statusLower === 'in_progress') return 'text-blue-600 bg-blue-50';
    if (statusLower === 'error' || statusLower === 'failed') return 'text-red-600 bg-red-50';
    if (statusLower === 'not_started' || statusLower === 'pending') return 'text-neutral-400 bg-neutral-50';
    if (statusLower === 'not_applicable') return 'text-neutral-300 bg-neutral-50';
    return 'text-neutral-500 bg-neutral-50';
  };

  const getStatusIcon = (status: string): string => {
    const statusLower = String(status || '').toLowerCase();
    if (statusLower === 'complete') return 'check_circle';
    if (statusLower === 'processing' || statusLower === 'in_progress') return 'pending';
    if (statusLower === 'error' || statusLower === 'failed') return 'error';
    if (statusLower === 'not_applicable') return 'remove_circle';
    return 'radio_button_unchecked';
  };

  const formatStageName = (name: string): string => {
    return String(name || 'Unknown')
      .replace(/_/g, ' ')
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const formatStatusName = (status: string): string => {
    return String(status || 'Unknown')
      .replace(/_/g, ' ')
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  if (!stages || stages.length === 0) {
    return (
      <div className="text-center py-8 text-neutral-500">
        <span className="material-symbols-rounded text-4xl text-neutral-300">timeline</span>
        <p className="mt-2">No pipeline stages available</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {stages.map((stage, idx) => (
        <div
          key={idx}
          className="bg-white border border-neutral-200 rounded-lg p-4 hover:shadow-sm transition-shadow"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="material-symbols-rounded text-primary-600" style={{ fontSize: '20px' }}>
                {getStageIcon(stage.name)}
              </span>
              <div>
                <h4 className="text-sm font-semibold text-neutral-900">
                  {formatStageName(stage.name)}
                </h4>
                <p className="text-xs text-neutral-500 mt-0.5">Stage {idx + 1} of {stages.length}</p>
              </div>
            </div>
            
            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${getStatusColor(stage.status)}`}>
              <span className="material-symbols-rounded" style={{ fontSize: '16px' }}>
                {getStatusIcon(stage.status)}
              </span>
              <span className="text-xs font-medium">
                {formatStatusName(stage.status)}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}