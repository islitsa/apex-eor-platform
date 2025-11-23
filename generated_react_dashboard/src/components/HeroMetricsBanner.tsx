import React from 'react';

interface HeroMetricsBannerProps {
  totalRows: number;
  totalFiles: number;
}

export default function HeroMetricsBanner({ totalRows, totalFiles }: HeroMetricsBannerProps) {
  return (
    <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-2xl shadow-lg p-8 border-2 border-blue-500">
      <div className="max-w-[1200px] mx-auto">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-6">
            <span className="material-symbols-rounded text-white text-6xl">science</span>
            <div>
              <div className="text-white text-5xl font-bold mb-2">
                {Number(totalRows || 0).toLocaleString()}
              </div>
              <div className="text-blue-100 text-2xl">Total Chemical Records</div>
            </div>
          </div>
          
          <div className="text-right">
            <div className="text-white text-4xl font-semibold mb-2">
              {Number(totalFiles || 0).toLocaleString()}
            </div>
            <div className="text-blue-100 text-xl">Data Files</div>
          </div>
        </div>
      </div>
    </div>
  );
}