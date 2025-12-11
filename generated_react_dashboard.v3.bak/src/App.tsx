import React, { useMemo } from 'react';
import { usePipelines } from './dataHooks.tsx';
import DatasetOverviewCard from './components/DatasetOverviewCard.tsx';
import PipelineHealthBanner from './components/PipelineHealthBanner.tsx';

const DISCOVERED_SOURCES = ["fracfocus_chemical_data"];

function App() {
  const { data, loading, error } = usePipelines();

  const filteredPipelines = useMemo(() => {
    if (!data?.pipelines) return [];
    return data.pipelines.filter(p =>
      DISCOVERED_SOURCES.some(s =>
        p.id.toLowerCase().includes(s.toLowerCase())
      )
    );
  }, [data]);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation Bar */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-[1200px] mx-auto px-6 py-4">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <span className="material-symbols-rounded text-xl">database</span>
            <span className="font-semibold text-gray-900">Data Sources</span>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-[1200px] mx-auto px-6 py-8">
        {loading && (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
              <p className="mt-4 text-gray-600">Loading pipelines...</p>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <div className="flex items-start gap-3">
              <span className="material-symbols-rounded text-red-600">error</span>
              <div>
                <h3 className="font-semibold text-red-900">Error Loading Data</h3>
                <p className="text-red-700 mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        {!loading && !error && filteredPipelines.length === 0 && (
          <div className="bg-white rounded-3xl shadow-lg p-12 text-center">
            <span className="material-symbols-rounded text-6xl text-gray-300">folder_off</span>
            <h3 className="mt-4 text-xl font-semibold text-gray-900">No Data Sources Found</h3>
            <p className="mt-2 text-gray-600">No discovered data sources are available.</p>
          </div>
        )}

        {!loading && !error && filteredPipelines.length > 0 && (
          <div className="space-y-6">
            {filteredPipelines.map(pipeline => (
              <DatasetOverviewCard key={pipeline.id} pipeline={pipeline} />
            ))}
          </div>
        )}
      </main>

      {/* Pipeline Health Banner */}
      {!loading && !error && data && (
        <PipelineHealthBanner pipelines={data.pipelines} summary={data.summary} />
      )}
    </div>
  );
}

export default App;