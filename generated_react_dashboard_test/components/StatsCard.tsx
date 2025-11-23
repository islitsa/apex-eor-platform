import React from 'react';
import { StatsCardProps } from '../types.ts';

const colorClasses = {
  blue: 'bg-blue-50 border-blue-200 text-blue-600',
  green: 'bg-green-50 border-green-200 text-green-600',
  purple: 'bg-purple-50 border-purple-200 text-purple-600',
  orange: 'bg-orange-50 border-orange-200 text-orange-600',
};

const textColorClasses = {
  blue: 'text-blue-900',
  green: 'text-green-900',
  purple: 'text-purple-900',
  orange: 'text-orange-900',
};

export default function StatsCard({ icon, label, value, color }: StatsCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-center gap-4">
        <div className={`rounded-full p-3 ${colorClasses[color]}`}>
          <span className="material-symbols-rounded text-3xl">{icon}</span>
        </div>
        <div className="flex-1">
          <p className="text-sm text-gray-600 mb-1">{label}</p>
          <p className={`text-2xl font-bold ${textColorClasses[color]}`}>{value}</p>
        </div>
      </div>
    </div>
  );
}