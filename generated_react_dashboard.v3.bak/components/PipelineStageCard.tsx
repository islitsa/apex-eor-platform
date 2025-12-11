import { useMemo } from 'react';
import { PipelineStage } from '../types.ts';

interface PipelineStageCardProps {
  stageName: string;
  status: string;
  onClick?: () => void;
}

function PipelineStageCard({ stageName, status, onClick }: PipelineStageCardProps) {
  const statusIcon = useMemo(() => {
    const normalizedStatus = String(status || '').toLowerCase();
    if (normalizedStatus === 'completed' || normalizedStatus === 'success') {
      return 'check_circle';
    }
    if (normalizedStatus === 'failed' || normalizedStatus === 'error') {
      return 'error';
    }
    return 'pending';
  }, [status]);

  const statusColor = useMemo(() => {
    const normalizedStatus = String(status || '').toLowerCase();
    if (normalizedStatus === 'completed' || normalizedStatus === 'success') {
      return 'text-green-600';
    }
    if (normalizedStatus === 'failed' || normalizedStatus === 'error') {
      return 'text-red-600';
    }
    return 'text-yellow-600';
  }, [status]);

  return (
    <div
      className="w-80 bg-white rounded-2xl shadow-lg p-5 cursor-pointer hover:shadow-xl transition-shadow"
      onClick={onClick}
    >
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-gray-900">{stageName}</h3>
        <span className={`material-symbols-rounded text-2xl ${statusColor}`}>
          {statusIcon}
        </span>
      </div>
      <p className="text-sm text-gray-500 mt-1 capitalize">{status}</p>
    </div>
  );
}

export { PipelineStageCard };
export default PipelineStageCard;