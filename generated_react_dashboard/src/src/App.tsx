import React, { useMemo } from 'react';
import { usePipelines } from './dataHooks.tsx';
import { Pipeline } from './types.ts';
import PipelineCard from './components/PipelineCard.tsx';
import StatsCard from './components/StatsCard.tsx';
import LoadingSpinner from './components/LoadingSpinner.tsx';
import ErrorDisplay from './components/ErrorDisplay.tsx';

const DISCOVERED_SOURCES = ['rrc', 'production'];

export default function App() {
  const { data, loading, error } = usePipelines();

  const filteredPipelines = useMemo(() => {
    if (!data?.pipelines) return [];

    return data.pipelines.filter(pipeline => {
      return DISCOVERED_SOURCES.some(source =>
        pipeline.id.toLowerCase().includes(source.toLowerCase()) ||
        pipeline.name.toLowerCase().includes(source.toLowerCase()) ||
        pipeline.display_name.toLowerCase().includes(source.toLowerCase())
      );
    });
  }, [data]);

  const stats = useMemo(() => {
    if (!filteredPipelines.length) {
      return {
        totalFiles: 0,
        totalRecords: 0,
        totalSize: '0 B',
        activePipelines: 0
      };
    }

    const totalFiles = filteredPipelines.reduce(
      (sum, p) => sum + (Number(p.metrics?.file_count) || 0),
      0
    );

    const totalRecords = filteredPipelines.reduce(
      (sum, p) => sum + (Number(p.metrics?.record_count) || 0),
      0
    );

    const activePipelines = filteredPipelines.filter(
      p => String(p.status).toLowerCase() === 'processed' || 
           String(p.status).toLowerCase() === 'processing'
    ).length;

    return {
      totalFiles,
      totalRecords,
      totalSize: data?.summary?.total_size || '0 B',
      activePipelines
    };
  }, [filteredPipelines, data]);

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <ErrorDisplay error={error} />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center gap-3">
            <span className="material-symbols-rounded text-4xl text-primary-600">
              oil_barrel
            </span>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                RRC Production Dashboard
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                Railroad Commission of Texas - Production Data Analytics
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard
            icon="database"
            label="Data Sources"
            value={filteredPipelines.length}
            color="blue"
          />
          <StatsCard
            icon="description"
            label="Total Files"
            value={stats.totalFiles.toLocaleString()}
            color="green"
          />
          <StatsCard
            icon="table_rows"
            label="Total Records"
            value={stats.totalRecords.toLocaleString()}
            color="purple"
          />
          <StatsCard
            icon="check_circle"
            label="Active Pipelines"
            value={stats.activePipelines}
            color="orange"
          />
        </div>

        {/* Pipeline Cards */}
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Production Data Sources
          </h2>
          {filteredPipelines.length === 0 ? (
            <div className="bg-white rounded-lg shadow-sm p-8 text-center">
              <span className="material-symbols-rounded text-6xl text-gray-300 mb-4">
                inbox
              </span>
              <p className="text-gray-600">
                No production data sources found matching: {DISCOVERED_SOURCES.join(', ')}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {filteredPipelines.map(pipeline => (
                <PipelineCard key={pipeline.id} pipeline={pipeline} />
              ))}
            </div>
          )}
        </div>

        {/* Footer Info */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <span className="material-symbols-rounded text-blue-600 mt-0.5">
              info
            </span>
            <div className="text-sm text-blue-900">
              <p className="font-semibold mb-1">About This Dashboard</p>
              <p>
                This dashboard displays production data from the Railroad Commission of Texas (RRC) 
                and related production datasets. Data is automatically synchronized and processed 
                through multiple pipeline stages to ensure accuracy and completeness.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}