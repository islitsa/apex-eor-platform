import React from 'react';

interface SummaryStatsProps {
  totalFiles: number;
  totalRecords: number;
  totalSize: string;
  processedCount: number;
  errorCount: number;
  pipelineCount: number;
}

export function SummaryStats({
  totalFiles,
  totalRecords,
  totalSize,
  processedCount,
  errorCount,
  pipelineCount
}: SummaryStatsProps) {
  const stats = [
    {
      icon: 'description',
      label: 'Total Files',
      value: totalFiles.toLocaleString(),
      color: 'blue'
    },
    {
      icon: 'database',
      label: 'Total Records',
      value: totalRecords.toLocaleString(),
      color: 'purple'
    },
    {
      icon: 'storage',
      label: 'Data Size',
      value: totalSize,
      color: 'indigo'
    },
    {
      icon: 'check_circle',
      label: 'Processed',
      value: `${processedCount}/${pipelineCount}`,
      color: 'green'
    },
    {
      icon: 'error',
      label: 'Errors',
      value: errorCount.toString(),
      color: errorCount > 0 ? 'red' : 'slate'
    }
  ];

  const colorClasses: Record<string, { bg: string; text: string; icon: string }> = {
    blue: { bg: 'bg-blue-50', text: 'text-blue-900', icon: 'text-blue-600' },
    purple: { bg: 'bg-purple-50', text: 'text-purple-900', icon: 'text-purple-600' },
    indigo: { bg: 'bg-indigo-50', text: 'text-indigo-900', icon: 'text-indigo-600' },
    green: { bg: 'bg-green-50', text: 'text-green-900', icon: 'text-green-600' },
    red: { bg: 'bg-red-50', text: 'text-red-900', icon: 'text-red-600' },
    slate: { bg: 'bg-slate-50', text: 'text-slate-900', icon: 'text-slate-600' }
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
      {stats.map((stat, index) => {
        const colors = colorClasses[stat.color];
        return (
          <div
            key={index}
            className={`${colors.bg} rounded-2xl p-6 shadow-md border border-${stat.color}-100`}
          >
            <div className="flex items-center gap-3">
              <span className={`material-symbols-rounded ${colors.icon} text-3xl`}>
                {stat.icon}
              </span>
              <div>
                <p className="text-sm text-slate-600 font-medium">{stat.label}</p>
                <p className={`text-2xl font-bold ${colors.text} mt-1`}>{stat.value}</p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}