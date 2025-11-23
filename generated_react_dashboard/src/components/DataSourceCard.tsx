import React, { useState, useMemo } from 'react';
import { useDataSource } from '../dataHooks';
import type { Pipeline } from '../types';
import FileExplorer from './FileExplorer.tsx';
import DataTable from './DataTable.tsx';

interface DataSourceCardProps {
  pipeline: Pipeline;
}

export default function DataSourceCard({ pipeline }: DataSourceCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showData, setShowData] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const rowsPerPage = 100;

  const { data: tableData, total, loading: dataLoading, error: dataError } = useDataSource(
    pipeline.id,
    {
      limit: rowsPerPage,
      offset: (currentPage - 1) * rowsPerPage
    }
  );

  const validStages = useMemo(() => {
    return (pipeline.stages || []).filter(stage => 
      typeof stage === 'object' && 
      stage !== null && 
      'name' in stage && 
      'status' in stage
    );
  }, [pipeline.stages]);

  const getStatusColor = (status: string) => {
    const statusStr = String(status || '').toLowerCase();
    if (statusStr === 'complete' || statusStr === 'processed') return 'text-green-600 bg-green-50';
    if (statusStr === 'processing' || statusStr === 'pending') return 'text-amber-600 bg-amber-50';
    if (statusStr === 'error' || statusStr === 'failed') return 'text-red-600 bg-red-50';
    return 'text-gray-600 bg-gray-50';
  };

  const getStatusIcon = (status: string) => {
    const statusStr = String(status || '').toLowerCase();
    if (statusStr === 'complete' || statusStr === 'processed') return 'check_circle';
    if (statusStr === 'processing' || statusStr === 'pending') return 'pending';
    if (statusStr === 'error' || statusStr === 'failed') return 'error';
    return 'help';
  };

  const totalPages = Math.ceil((total || 0) / rowsPerPage);

  return (
    <div className="w-4/5 mx-auto">
      <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
        {/* Card Header */}
        <div 
          className="p-6 cursor-pointer hover:bg-gray-50 transition-colors"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <span className="material-symbols-rounded text-blue-600 text-5xl">science</span>
              <div>
                <h2 className="text-3xl font-bold text-gray-900">
                  {pipeline.display_name || pipeline.name}
                </h2>
                <p className="text-lg text-gray-500 mt-1">
                  {Number(pipeline.metrics?.record_count || 0).toLocaleString()} records
                  {pipeline.metrics?.data_size && ` • ${pipeline.metrics.data_size}`}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className={`px-4 py-2 rounded-full ${getStatusColor(pipeline.status)}`}>
                <div className="flex items-center gap-2">
                  <span className="material-symbols-rounded text-xl">
                    {getStatusIcon(pipeline.status)}
                  </span>
                  <span className="font-semibold capitalize">
                    {String(pipeline.status || 'unknown').replace(/_/g, ' ')}
                  </span>
                </div>
              </div>
              <span className={`material-symbols-rounded text-3xl text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}>
                expand_more
              </span>
            </div>
          </div>
        </div>

        {/* Expanded Content */}
        {isExpanded && (
          <div className="border-t border-gray-200">
            {/* Pipeline Stages */}
            <div className="p-6 bg-gray-50">
              <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <span className="material-symbols-rounded">account_tree</span>
                Pipeline Stages
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {validStages.map((stage, index) => (
                  <div 
                    key={index}
                    className="bg-white rounded-lg p-4 shadow-sm"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-gray-900 capitalize">
                        {String(stage.name || '').replace(/_/g, ' ')}
                      </span>
                      <span className={`material-symbols-rounded text-xl ${getStatusColor(String(stage.status || ''))}`}>
                        {getStatusIcon(String(stage.status || ''))}
                      </span>
                    </div>
                    <div className="text-sm text-gray-500">
                      {stage.file_count !== undefined && (
                        <div>{Number(stage.file_count || 0).toLocaleString()} files</div>
                      )}
                      {stage.record_count !== undefined && (
                        <div>{Number(stage.record_count || 0).toLocaleString()} records</div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* File Explorer */}
            <div className="p-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <span className="material-symbols-rounded">storage</span>
                File Structure
              </h3>
              <FileExplorer files={pipeline.files} pipelineName={pipeline.name} />
            </div>

            {/* Data Preview Toggle */}
            <div className="p-6 border-t border-gray-200">
              <button
                onClick={() => setShowData(!showData)}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                <span className="material-symbols-rounded">
                  {showData ? 'visibility_off' : 'visibility'}
                </span>
                {showData ? 'Hide Data Preview' : 'Show Data Preview (First 100 Rows)'}
              </button>
            </div>

            {/* Data Table */}
            {showData && (
              <div className="p-6 border-t border-gray-200">
                <DataTable
                  data={tableData || []}
                  total={total || 0}
                  loading={dataLoading}
                  error={dataError}
                  currentPage={currentPage}
                  totalPages={totalPages}
                  onPageChange={setCurrentPage}
                />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}