import React from 'react';
import { StatsCardProps } from '../types.ts';

const colorClasses = {
  blue: {
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    icon: 'text-blue-600',
    text: 'text-blue-900',
  },
  purple: {
    bg: 'bg-purple-50',
    border: 'border-purple-200',
    icon: 'text-purple-600',
    text: 'text-purple-900',
  },
  green: {
    bg: 'bg-green-50',
    border: 'border-green-200',
    icon: 'text-green-600',
    text: 'text-green-900',
  },
  orange: {
    bg: 'bg-orange-50',
    border: 'border-orange-200',
    icon: 'text-orange-600',
    text: 'text-orange-900',
  },
};

export default function StatsCard({ icon, label, value, color }: StatsCardProps) {
  const colors = colorClasses[color];

  return (
    <div className={`${colors.bg} ${colors.border} border rounded-xl p-6 shadow-sm`}>
      <div className="flex items-center justify-between mb-3">
        <span className={`material-symbols-rounded ${colors.icon} text-3xl`}>{icon}</span>
      </div>
      <p className="text-gray-600 text-sm font-medium mb-1">{label}</p>
      <p className={`text-3xl font-bold ${colors.text}`}>{value}</p>
    </div>
  );
}