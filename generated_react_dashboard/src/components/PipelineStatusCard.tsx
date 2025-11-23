import React from 'react';
import type { Pipeline } from '../types.ts';

interface PipelineStatusCardProps {
  pipeline?: Pipeline;
  onExploreFiles: () => void;
}

export function PipelineStatusCard({ pipeline, onExploreFiles }: PipelineStatusCardProps) {
  if (!pipeline) {
    return (
      <div className="bg-white rounded-2xl shadow-md p-6">
        <div className="flex items-center gap-3 mb-6">
          <span className="material-symbols-rounded text-gray-400 text-[24px]">pending</span>
          <h2 className="text-xl font-bold text-gray-900">Pipeline Status</h2>
        </div>
        <p className="text-gray-500">No pipeline data available</p>
      </div>
    );
  }

  const stages = pipeline.stages || {};
  const stageOrder = ['download', 'extraction', 'parsing', 'validation', 'loading'];
  
  const getStageIcon = (status: string) => {
    switch (status) {
      case 'complete': return 'check_circle';
      case 'not_started': return 'pending';
      case 'error': return 'error';
      default: return 'pending';
    }
  };

  const getStageColor = (status: string) => {
    switch (status) {
      case 'complete': return 'text-green-600 bg-green-100';
      case 'not_started': return 'text-gray-400 bg-gray-100';
      case 'error': return 'text-red-600 bg-red-100';
      default: return 'text-amber-600 bg-amber-100';
    }
  };

  const completedStages = Object.values(stages).filter(s => s.status === 'complete').length;
  const totalStages = stageOrder.length;
  const progressPercent = (completedStages / totalStages) * 100;

  return (
    <div className="bg-white rounded-2xl shadow-md p-6 hover:shadow-xl transition-shadow">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${getStageColor(pipeline.status)}`}>
          <span className="material-symbols-rounded text-[20px]">
            {getStageIcon(pipeline.status)}
          </span>
        </div>
        <h2 className="text-xl font-bold text-gray-900">Pipeline Status</h2>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <p className="text-sm font-medium text-gray-700">Overall Progress</p>
          <p className="text-sm font-bold text-gray-900">{completedStages}/{totalStages}</p>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-1">
          <div 
            className="bg-blue-600 h-1 rounded-full transition-all duration-500"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      {/* Stages */}
      <div className="space-y-3 mb-6">
        {stageOrder.map(stageName => {
          const stage = stages[stageName];
          const status = stage?.status || 'not_started';
          
          return (
            <div key={stageName} className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className={`material-symbols-rounded text-[20px] ${getStageColor(status).split(' ')[0]}`}>
                  {getStageIcon(status)}
                </span>
                <span className="text-sm font-medium text-gray-900 capitalize">
                  {stageName}
                </span>
              </div>
              <span className={`text-xs font-medium px-2 py-1 rounded ${getStageColor(status)}`}>
                {status.replace('_', ' ')}
              </span>
            </div>
          );
        })}
      </div>

      {/* Action Buttons */}
      <div className="grid grid-cols-3 gap-3">
        <button 
          onClick={onExploreFiles}
          className="flex flex-col items-center gap-2 p-3 rounded-lg hover:bg-gray-50 transition-colors group"
        >
          <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center group-hover:bg-blue-200 transition-colors">
            <span className="material-symbols-rounded text-blue-600 text-[20px]">folder_open</span>
          </div>
          <span className="text-xs font-medium text-gray-700">Files</span>
        </button>
        
        <button className="flex flex-col items-center gap-2 p-3 rounded-lg hover:bg-gray-50 transition-colors group">
          <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center group-hover:bg-green-200 transition-colors">
            <span className="material-symbols-rounded text-green-600 text-[20px]">transform</span>
          </div>
          <span className="text-xs font-medium text-gray-700">Transform</span>
        </button>
        
        <button className="flex flex-col items-center gap-2 p-3 rounded-lg hover:bg-gray-50 transition-colors group">
          <div className="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center group-hover:bg-purple-200 transition-colors">
            <span className="material-symbols-rounded text-purple-600 text-[20px]">analytics</span>
          </div>
          <span className="text-xs font-medium text-gray-700">Analyze</span>
        </button>
      </div>
    </div>
  );
}