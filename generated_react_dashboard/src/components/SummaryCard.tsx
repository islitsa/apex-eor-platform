import React from 'react';

interface SummaryCardProps {
  icon: string;
  label: string;
  value: string;
  color: 'blue' | 'green' | 'purple' | 'orange';
}

export function SummaryCard({ icon, label, value, color }: SummaryCardProps) {
  const colorClasses = {
    blue: 'from-blue-500 to-blue-600 text-blue-600',
    green: 'from-green-500 to-green-600 text-green-600',
    purple: 'from-purple-500 to-purple-600 text-purple-600',
    orange: 'from-orange-500 to-orange-600 text-orange-600'
  };

  const bgClasses = {
    blue: 'bg-blue-50',
    green: 'bg-green-50',
    purple: 'bg-purple-50',
    orange: 'bg-orange-50'
  };

  return (
    <div className="bg-white rounded-2xl shadow-md hover:shadow-lg transition-shadow duration-300 p-6">
      <div className="flex items-center gap-4">
        <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${colorClasses[color]} flex items-center justify-center`}>
          <span className="material-symbols-rounded text-white text-2xl">
            {icon}
          </span>
        </div>
        <div className="flex-1">
          <p className="text-sm font-medium text-slate-600 mb-1">{label}</p>
          <p className="text-2xl font-bold text-slate-900">{value}</p>
        </div>
      </div>
    </div>
  );
}