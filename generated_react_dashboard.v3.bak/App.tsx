import { useMemo } from 'react';
import { usePipelines } from './dataHooks.tsx';
import { Pipeline } from './types.ts';
import PipelineHealthHeader from './components/PipelineHealthHeader.tsx';
import PipelineStageCard from './components/PipelineStageCard.tsx';
import DatasetOverviewCard from './components/DatasetOverviewCard.tsx';

const DISCOVERED_SOURCES = ['fracfocus_chemical_data'];

function App() {
  const { data, loading, error } = usePipelines();

  const filteredPipelines = useMemo(() => {
    if (!data?.pipelines) return [];
    return data.pipelines.filter((p: Pipeline) =>
      DISCOVERED_SOURCES.some((s: string) =>
        p.id.toLowerCase().includes(s.toLowerCase())
      )
    );
  }, [data]);

  const totalRecords = useMemo(() => {
    if (!data?.summary) return 0;
    return Number(data.summary.metrics.record_count || 0);
  }, [data]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <span className="material-symbols-rounded text-6xl text-blue-600 animate-spin">
            refresh
          </span>
          <p className="mt-4 text-xl text-gray-600">Loading pipeline data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-2xl shadow-lg p-8 max-w-md">
          <span className="material-symbols-rounded text-6xl text-red-600">error</span>
          <h2 className="text-2xl font-bold text-gray-900 mt-4">Error Loading Data</h2>
          <p className="text-gray-600 mt-2">{error.message}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-6 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (filteredPipelines.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-2xl shadow-lg p-8 max-w-md text-center">
          <span className="material-symbols-rounded text-6xl text-gray-400">folder_off</span>
          <h2 className="text-2xl font-bold text-gray-900 mt-4">No Pipelines Found</h2>
          <p className="text-gray-600 mt-2">
            No pipelines matching the discovered sources were found.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 px-6 py-8">
      <div className="max-w-7xl mx-auto">
        <PipelineHealthHeader
          totalPipelines={filteredPipelines.length}
          totalRecords={totalRecords}
        />

        <div className="flex gap-8">
          <div className="w-2/5 space-y-8">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Pipeline Stages</h2>
              <div className="space-y-4">
                {filteredPipelines.map((pipeline: Pipeline) => (
                  <div key={pipeline.id} className="space-y-3">
                    {pipeline.stages?.map((stage, idx: number) => (
                      <PipelineStageCard
                        key={`${pipeline.id}-stage-${idx}`}
                        stageName={stage.name}
                        status={stage.status}
                      />
                    )) ?? []}
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="w-3/5">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Dataset Explorer</h2>
            <div className="space-y-8">
              {filteredPipelines.map((pipeline: Pipeline) => (
                <DatasetOverviewCard key={pipeline.id} pipeline={pipeline} />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export { App };
export default App;