import React from 'react';

interface ProductionStatusHeaderProps {
  isActive: boolean;
  sourceCount: number;
}

export default function ProductionStatusHeader({ isActive, sourceCount }: ProductionStatusHeaderProps) {
  return (
    <header className="w-full bg-gray-900 text-white py-6 shadow-lg">
      <div className="max-w-[1200px] mx-auto px-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="material-symbols-rounded text-4xl">database</span>
            <div>
              <h1 className="text-3xl font-bold">Production Data Dashboard</h1>
              <p className="text-gray-400 text-sm mt-1">RRC Dataset Monitoring</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className={`flex items-center gap-2 px-4 py-2 rounded-full ${
              isActive ? 'bg-green-500/20 text-green-400' : 'bg-gray-700 text-gray-400'
            }`}>
              <span className={`material-symbols-rounded text-xl ${isActive ? 'animate-pulse' : ''}`}>
                check_circle
              </span>
              <span className="font-medium">
                {isActive ? 'Active' : 'Inactive'}
              </span>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold">{sourceCount}</div>
              <div className="text-xs text-gray-400">Sources</div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}