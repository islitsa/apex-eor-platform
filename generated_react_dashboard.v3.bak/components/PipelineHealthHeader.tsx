import { useMemo } from 'react';

interface PipelineHealthHeaderProps {
  totalPipelines: number;
  totalRecords: number;
}

function PipelineHealthHeader({ totalPipelines, totalRecords }: PipelineHealthHeaderProps) {
  const formattedRecords = useMemo(() => {
    return Number(totalRecords || 0).toLocaleString();
  }, [totalRecords]);

  return (
    <div className="w-full mb-8">
      <div className="flex items-center gap-3 mb-2">
        <span className="material-symbols-rounded text-5xl text-blue-600">database</span>
        <h1 className="text-5xl font-bold text-gray-900">Pipeline Health Dashboard</h1>
      </div>
      <p className="text-xl text-gray-600 ml-16">
        Monitoring {totalPipelines} active {totalPipelines === 1 ? 'pipeline' : 'pipelines'} • {formattedRecords} total records
      </p>
    </div>
  );
}

export { PipelineHealthHeader };
export default PipelineHealthHeader;