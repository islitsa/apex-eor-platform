import React from 'react';

interface SummaryCardProps {
  icon: string;
  label: string;
  value: string;
  color: 'primary' | 'success' | 'warning' | 'error';
}

const colorClasses = {
  primary: 'bg-blue-50 text-primary',
  success: 'bg-green-50 text-success',
  warning: 'bg-orange-50 text-warning',
  error: 'bg-red-50 text-error',
};

export default function SummaryCard({ icon, label, value, color }: SummaryCardProps) {
  return (
    <div className="bg-white rounded-2xl shadow-sm p-6 hover:shadow-md transition-shadow">
      <div className={`inline-flex p-3 rounded-xl ${colorClasses[color]} mb-4`}>
        <span className="material-symbols-rounded text-2xl">{icon}</span>
      </div>
      <p className="text-sm text-gray-600 mb-1">{label}</p>
      <p className="text-3xl font-bold text-gray-900">{value}</p>
    </div>
  );
}