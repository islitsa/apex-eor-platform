import React from 'react';

interface ProductionOverviewHeaderProps {
  sourceCount: number;
  discoveredSources: string[];
}

export default function ProductionOverviewHeader({ 
  sourceCount, 
  discoveredSources 
}: ProductionOverviewHeaderProps) {
  return (
    <div className="h-full flex flex-col justify-center">
      <div className="flex items-center gap-4 mb-4">
        <span className="material-symbols-rounded text-white text-5xl">database</span>
        <div>
          <h1 className="text-4xl font-bold text-white">Production Data Dashboard</h1>
          <p className="text-blue-100 text-lg mt-1">
            Railroad Commission of Texas (RRC) Data Repository
          </p>
        </div>
      </div>
      <div className="flex items-center gap-2 text-blue-100">
        <span className="material-symbols-rounded text-xl">info</span>
        <span className="text-sm">
          Showing {sourceCount} datasets: {discoveredSources.join(', ')}
        </span>
      </div>
    </div>
  );
}