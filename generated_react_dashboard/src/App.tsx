import React, { useState, useMemo } from 'react';
import { usePipelines } from './dataHooks.tsx';
import DatasetOverviewCard from './components/DatasetOverviewCard.tsx';
import PipelineStageIndicators from './components/PipelineStageIndicators.tsx';
import FileExplorerPanel from './components/FileExplorerPanel.tsx';
import DataPreviewTable from './components/DataPreviewTable.tsx';
import PaginationControls from './components/PaginationControls.tsx';
import QuickStatsBar from './components/QuickStatsBar.tsx';
import type { Pipeline } from './types.ts';

export default function App() {
  const { data, loading, error } = usePipelines();
  const [selectedPipeline, setSelectedPipeline] = useState<Pipeline | null>(null);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  // CRITICAL: Filter to only discovered sources
  const DISCOVERED_SOURCES = ["fracfocus"];

  const filteredPipelines = useMemo(() => {
    if (!data?.pipelines || !Array.isArray(data.pipelines)) return [];

    return data.pipelines.filter(pipeline => {
      return DISCOVERED_SOURCES.some(source =>
        String(pipeline.id || '').toLowerCase().includes(source.toLowerCase()) ||
        String(pipeline.name || '').toLowerCase().includes(source.toLowerCase())
      );
    });
  }, [data]);

  // Calculate totals from filtered pipelines
  const totalFiles = useMemo(() => {
    return filteredPipelines.reduce((sum, p) => sum + (p.metrics?.file_count || 0), 0);
  }, [filteredPipelines]);

  const totalRecords = useMemo(() => {
    return filteredPipelines.reduce((sum, p) => sum + (p.metrics?.record_count || 0), 0);
  }, [filteredPipelines]);

  const totalSize = useMemo(() => {
    return filteredPipelines.reduce((sum, p) => {
      const sizeStr = p.metrics?.data_size || '0';
      const sizeNum = parseFloat(String(sizeStr).replace(/[^0-9.]/g, ''));
      return sum + (isNaN(sizeNum) ? 0 : sizeNum);
    }, 0);
  }, [filteredPipelines]);

  // Auto-select first pipeline
  React.useEffect(() => {
    if (filteredPipelines.length > 0 && !selectedPipeline) {
      setSelectedPipeline(filteredPipelines[0]);
    }
  }, [filteredPipelines, selectedPipeline]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading chemical data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-center">
          <span className="material-symbols-rounded text-red-600 text-5xl mb-4">error</span>
          <p className="text-red-600 font-semibold">Error loading data</p>
          <p className="text-gray-600 mt-2">{String(error)}</p>
        </div>
      </div>
    );
  }

  if (filteredPipelines.length === 0) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-center">
          <span className="material-symbols-rounded text-gray-400 text-5xl mb-4">database</span>
          <p className="text-gray-600">No data sources found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Left Sidebar */}
      <div className="w-80 bg-white border-r border-gray-200 overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center gap-2 mb-2">
            <span className="material-symbols-rounded text-blue-600">database</span>
            <h1 className="text-xl font-bold text-gray-900">Data Sources</h1>
          </div>
          <p className="text-sm text-gray-600">
            {filteredPipelines.length} {filteredPipelines.length === 1 ? 'source' : 'sources'} available
          </p>
        </div>

        <QuickStatsBar
          totalFiles={totalFiles}
          totalRecords={totalRecords}
          totalSize={totalSize}
        />

        <div className="p-4 space-y-4">
          {filteredPipelines.map(pipeline => (
            <DatasetOverviewCard
              key={pipeline.id}
              pipeline={pipeline}
              isSelected={selectedPipeline?.id === pipeline.id}
              onClick={() => setSelectedPipeline(pipeline)}
            />
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {selectedPipeline ? (
          <>
            {/* Header */}
            <div className="bg-white border-b border-gray-200 p-6">
              <div className="flex items-center gap-3 mb-4">
                <span className="material-symbols-rounded text-blue-600 text-3xl">science</span>
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">
                    {String(selectedPipeline.display_name || selectedPipeline.name || 'Unknown')}
                  </h2>
                  <p className="text-sm text-gray-600">
                    {Number(selectedPipeline.metrics?.record_count || 0).toLocaleString()} records • {' '}
                    {Number(selectedPipeline.metrics?.file_count || 0).toLocaleString()} files
                  </p>
                </div>
              </div>

              <PipelineStageIndicators stages={selectedPipeline.stages || []} />
            </div>

            {/* Content Area */}
            <div className="flex-1 flex overflow-hidden">
              {/* File Explorer */}
              <div className="w-96 bg-white border-r border-gray-200 overflow-y-auto">
                <FileExplorerPanel
                  pipeline={selectedPipeline}
                  selectedFile={selectedFile}
                  onFileSelect={setSelectedFile}
                />
              </div>

              {/* Data Preview */}
              <div className="flex-1 flex flex-col overflow-hidden">
                <div className="flex-1 overflow-auto p-6">
                  <DataPreviewTable
                    pipeline={selectedPipeline}
                    selectedFile={selectedFile}
                    currentPage={currentPage}
                    rowsPerPage={rowsPerPage}
                  />
                </div>

                <div className="bg-white border-t border-gray-200 p-4">
                  <PaginationControls
                    currentPage={currentPage}
                    rowsPerPage={rowsPerPage}
                    totalRecords={selectedPipeline.metrics?.record_count || 0}
                    onPageChange={setCurrentPage}
                    onRowsPerPageChange={setRowsPerPage}
                  />
                </div>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <span className="material-symbols-rounded text-gray-300 text-6xl mb-4">folder_open</span>
              <p className="text-gray-500">Select a data source to view details</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}