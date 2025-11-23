import React from 'react';

interface StatsCardProps {
  icon: string;
  label: string;
  value: string | number;
  color: 'blue' | 'green' | 'purple' | 'orange';
}

export default function StatsCard({ icon, label, value, color }: StatsCardProps) {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-700',
    green: 'bg-green-100 text-green-700',
    purple: 'bg-purple-100 text-purple-700',
    orange: 'bg-orange-100 text-orange-700'
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow duration-200">
      <div className="flex items-center gap-4">
        <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${colorClasses[color]}`}>
          <span className="material-symbols-rounded text-2xl">
            {icon}
          </span>
        </div>
        <div>
          <p className="text-sm text-gray-600 mb-1">{label}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
        </div>
      </div>
    </div>
  );
}