import React from 'react';
import Icon from './Icon.tsx';

interface HeaderProps {
  totalPipelines: number;
  totalRecords: number;
  totalSize: string;
}

export default function Header({ totalPipelines, totalRecords, totalSize }: HeaderProps) {
  return (
    <header className="sticky top-0 z-50 bg-white border-b border-gray-200 shadow-sm">
      <div className="h-20 max-w-[1200px] mx-auto px-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Icon name="science" className="text-primary" />
          <h1 className="text-2xl font-bold text-gray-900">FracFocus Chemical Data</h1>
        </div>
      </div>
      
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-t border-gray-100">
        <div className="max-w-[1200px] mx-auto px-6 py-4">
          <div className="grid grid-cols-3 gap-8">
            <StatItem
              icon="database"
              label="Pipelines"
              value={totalPipelines.toString()}
            />
            <StatItem
              icon="table_rows"
              label="Total Records"
              value={totalRecords.toLocaleString()}
            />
            <StatItem
              icon="storage"
              label="Total Size"
              value={totalSize}
            />
          </div>
        </div>
      </div>
    </header>
  );
}

interface StatItemProps {
  icon: string;
  label: string;
  value: string;
}

function StatItem({ icon, label, value }: StatItemProps) {
  return (
    <div className="flex items-center gap-3 bg-white rounded-lg px-4 py-3 shadow-sm">
      <Icon name={icon} className="text-primary" />
      <div>
        <div className="text-sm text-gray-600">{label}</div>
        <div className="text-xl font-bold text-gray-900">{value}</div>
      </div>
    </div>
  );
}