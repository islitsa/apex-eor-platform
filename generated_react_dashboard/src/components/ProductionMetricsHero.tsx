import React from 'react';

interface ProductionMetricsHeroProps {
  totalFiles: number;
  totalSize: number;
  totalRecords: number;
  datasetCount: number;
}

export default function ProductionMetricsHero({
  totalFiles,
  totalSize,
  totalRecords,
  datasetCount
}: ProductionMetricsHeroProps) {
  const sizeInGB = totalSize / (1024 * 1024 * 1024);

  return (
    <div className="bg-gradient-to-r from-[#FF6B35] to-[#FF8C42] rounded-xl shadow-lg p-8 mb-8">
      <div className="grid grid-cols-4 gap-6">
        <MetricCard
          icon="folder"
          label="Datasets"
          value={String(datasetCount)}
          iconColor="text-white"
        />
        <MetricCard
          icon="description"
          label="Total Files"
          value={Number(totalFiles || 0).toLocaleString()}
          iconColor="text-white"
        />
        <MetricCard
          icon="storage"
          label="Total Size"
          value={`${Number(sizeInGB || 0).toFixed(2)} GB`}
          iconColor="text-white"
        />
        <MetricCard
          icon="table_rows"
          label="Total Records"
          value={Number(totalRecords || 0).toLocaleString()}
          iconColor="text-white"
        />
      </div>
    </div>
  );
}

interface MetricCardProps {
  icon: string;
  label: string;
  value: string;
  iconColor: string;
}

function MetricCard({ icon, label, value, iconColor }: MetricCardProps) {
  return (
    <div className="bg-white bg-opacity-10 backdrop-blur-sm rounded-lg p-6">
      <div className="flex items-center gap-3 mb-2">
        <span className={`material-symbols-rounded ${iconColor} text-3xl`}>{icon}</span>
      </div>
      <div className="text-white text-5xl font-bold mb-1">{value}</div>
      <div className="text-white text-opacity-90 text-sm font-medium">{label}</div>
    </div>
  );
}