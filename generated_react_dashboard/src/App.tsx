import React, { useState, useMemo } from 'react';
import { usePipelines } from './dataHooks.tsx';
import PipelineHealthOverview from './components/PipelineHealthOverview.tsx';
import ExpandableDatasetCard from './components/ExpandableDatasetCard.tsx';
import DataPreviewTable from './components/DataPreviewTable.tsx';
import type { Pipeline } from './types.ts';

export default function App() {
  const { data, loading, error } = usePipelines();
  const [selectedPipeline, setSelectedPipeline] = useState<Pipeline | null>(null);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);

  // CRITICAL: Filter to only discovered sources
  const DISCOVERED_SOURCES = ["rrc"];

  const filteredPipelines = useMemo(() => {
    if (!data?.pipelines || !Array.isArray(data.pipelines)) return [];

    return data.pipelines.filter(pipeline => {
      return DISCOVERED_SOURCES.some(source =>
        pipeline.id.toLowerCase().includes(source.toLowerCase()) ||
        pipeline.name.toLowerCase().includes(source.toLowerCase())
      );
    });
  }, [data]);

  const totalFiles = useMemo(() => {
    return filteredPipelines.reduce((sum, p) => sum + (p.metrics?.file_count || 0), 0);
  }, [filteredPipelines]);

  const totalRecords = useMemo(() => {
    return filteredPipelines.reduce((sum, p) => sum + (p.metrics?.record_count || 0), 0);
  }, [filteredPipelines]);

  const handleFileSelect = (pipeline: Pipeline, filePath: string) => {
    setSelectedPipeline(pipeline);
    setSelectedFile(filePath);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-gray-600 text-lg">Loading production data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <div className="flex items-center gap-3 mb-2">
            <span className="material-symbols-rounded text-red-600">error</span>
            <h2 className="text-lg font-semibold text-red-900">Error Loading Data</h2>
          </div>
          <p className="text-red-700">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-[1200px] mx-auto px-8 py-6">
          <div className="flex items-center gap-3 mb-2">
            <span className="material-symbols-rounded text-blue-600 text-4xl">database</span>
            <h1 className="text-4xl font-bold text-gray-900">RRC Production Data Dashboard</h1>
          </div>
          <p className="text-gray-600 text-lg ml-14">
            {filteredPipelines.length} data source{filteredPipelines.length !== 1 ? 's' : ''} • {totalFiles.toLocaleString()} files • {totalRecords.toLocaleString()} records
          </p>
        </div>
      </header>

      <main className="max-w-[1200px] mx-auto px-8 py-8">
        {/* Top Tier: Pipeline Health Overview (25% height) */}
        <section className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <span className="material-symbols-rounded">monitoring</span>
            Pipeline Health by Stage
          </h2>
          <PipelineHealthOverview pipelines={filteredPipelines} />
        </section>

        {/* Middle Tier: Expandable Dataset Cards (50% height) */}
        <section className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <span className="material-symbols-rounded">oil_barrel</span>
            Data Sources
          </h2>
          <div className="space-y-4">
            {filteredPipelines.map(pipeline => (
              <ExpandableDatasetCard
                key={pipeline.id}
                pipeline={pipeline}
                onFileSelect={handleFileSelect}
                selectedFile={selectedFile}
              />
            ))}
          </div>
          {filteredPipelines.length === 0 && (
            <div className="bg-white rounded-xl shadow-md p-8 text-center">
              <span className="material-symbols-rounded text-gray-400 text-5xl mb-3">folder_off</span>
              <p className="text-gray-600 text-lg">No data sources found matching: {DISCOVERED_SOURCES.join(', ')}</p>
            </div>
          )}
        </section>

        {/* Bottom Tier: Data Preview Table (25% height) */}
        {selectedPipeline && selectedFile && (
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <span className="material-symbols-rounded">table_view</span>
              Data Preview
            </h2>
            <DataPreviewTable
              pipeline={selectedPipeline}
              filePath={selectedFile}
            />
          </section>
        )}
      </main>
    </div>
  );
}