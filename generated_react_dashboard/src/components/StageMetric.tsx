import React from 'react';

interface StageMetricProps {
  icon: string;
  title: string;
  value: number;
  total: number;
  status: 'complete' | 'processing' | 'error';
}

export default function StageMetric({ icon, title, value, total, status }: StageMetricProps) {
  const percentage = total > 0 ? Math.round((value / total) * 100) : 0;

  return (
    <div className="bg-white rounded-2xl p-6 shadow-md border border-gray-200">
      <div className="flex items-center gap-3 mb-4">
        <span
          className={`material-symbols-rounded text-3xl ${
            status === 'complete'
              ? 'text-green-600'
              : status === 'processing'
              ? 'text-blue-600'
              : 'text-red-600'
          }`}
        >
          {icon}
        </span>
        <h3 className="text-xl font-bold text-gray-900">{title}</h3>
      </div>

      <div className="mb-4">
        <div className="flex items-baseline gap-2 mb-2">
          <span className="text-4xl font-bold text-blue-600">{value}</span>
          <span className="text-lg text-gray-600">/ {total}</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-500 ${
              status === 'complete'
                ? 'bg-green-600'
                : status === 'processing'
                ? 'bg-blue-600'
                : 'bg-red-600'
            }`}
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>

      <div className="flex items-center gap-2">
        <span
          className={`material-symbols-rounded text-base ${
            status === 'complete'
              ? 'text-green-600'
              : status === 'processing'
              ? 'text-blue-600'
              : 'text-red-600'
          }`}
        >
          {status === 'complete' ? 'check_circle' : status === 'processing' ? 'pending' : 'error'}
        </span>
        <span className="text-sm font-medium text-gray-700 capitalize">{status}</span>
      </div>
    </div>
  );
}