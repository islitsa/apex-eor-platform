import React from 'react';

interface PipelineStatusHeroProps {
  totalFiles: number;
  totalRecords: number;
  totalSize: string;
  pipelineCount: number;
}

export default function PipelineStatusHero({ 
  totalFiles, 
  totalRecords, 
  totalSize,
  pipelineCount 
}: PipelineStatusHeroProps) {
  return (
    <div className="bg-gradient-to-br from-blue-600 to-blue-800 text-white py-16 px-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center gap-4 mb-6">
          <span className="material-symbols-rounded text-7xl">oil_barrel</span>
          <h1 className="text-8xl font-bold">Chemical Data Pipeline</h1>
        </div>
        
        <div className="grid grid-cols-4 gap-8 mt-12">
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
            <div className="flex items-center gap-2 mb-2">
              <span className="material-symbols-rounded text-2xl">folder</span>
              <p className="text-sm font-medium opacity-90">Total Files</p>
            </div>
            <p className="text-4xl font-bold">{Number(totalFiles || 0).toLocaleString()}</p>
          </div>

          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
            <div className="flex items-center gap-2 mb-2">
              <span className="material-symbols-rounded text-2xl">table_rows</span>
              <p className="text-sm font-medium opacity-90">Total Records</p>
            </div>
            <p className="text-4xl font-bold">{Number(totalRecords || 0).toLocaleString()}</p>
          </div>

          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
            <div className="flex items-center gap-2 mb-2">
              <span className="material-symbols-rounded text-2xl">storage</span>
              <p className="text-sm font-medium opacity-90">Data Size</p>
            </div>
            <p className="text-4xl font-bold">{String(totalSize)}</p>
          </div>

          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
            <div className="flex items-center gap-2 mb-2">
              <span className="material-symbols-rounded text-2xl">science</span>
              <p className="text-sm font-medium opacity-90">Pipelines</p>
            </div>
            <p className="text-4xl font-bold">{Number(pipelineCount || 0)}</p>
          </div>
        </div>
      </div>
    </div>
  );
}