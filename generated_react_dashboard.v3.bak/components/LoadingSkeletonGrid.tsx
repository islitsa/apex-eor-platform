import React from 'react';

export function LoadingSkeletonGrid() {
  return (
    <div className="flex gap-6 pt-16 px-8">
      <div className="w-[300px] flex-shrink-0">
        <div className="h-6 w-48 bg-gray-200 rounded mb-6 animate-pulse" />
        <div className="w-[280px] flex flex-col gap-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex flex-col items-center">
              <div className="w-12 h-12 bg-gray-200 rounded-full animate-pulse" />
              <div className="mt-2 h-4 w-24 bg-gray-200 rounded animate-pulse" />
            </div>
          ))}
        </div>
      </div>
      <div className="flex-1 min-w-0">
        <div className="bg-gray-200 rounded-2xl h-64 animate-pulse" />
      </div>
      <div className="w-[500px] flex-shrink-0">
        <div className="bg-gray-200 rounded-2xl h-96 animate-pulse" />
      </div>
    </div>
  );
}