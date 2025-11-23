import React from 'react';

interface ChartData {
  name: string;
  count: number;
}

interface ChemicalChartProps {
  title: string;
  icon: string;
  data: ChartData[];
  color: 'blue' | 'orange' | 'green' | 'purple';
}

const colorMap = {
  blue: { bg: 'bg-blue-500', light: 'bg-blue-100', text: 'text-blue-700' },
  orange: { bg: 'bg-orange-500', light: 'bg-orange-100', text: 'text-orange-700' },
  green: { bg: 'bg-green-500', light: 'bg-green-100', text: 'text-green-700' },
  purple: { bg: 'bg-purple-500', light: 'bg-purple-100', text: 'text-purple-700' }
};

export default function ChemicalChart({ title, icon, data, color }: ChemicalChartProps) {
  const colors = colorMap[color];
  const maxCount = Math.max(...data.map(d => d.count), 1);

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <div className="flex items-center gap-3 mb-6">
        <span className={`material-symbols-rounded text-2xl ${colors.text}`}>{icon}</span>
        <h3 className="text-xl font-bold text-gray-900">{title}</h3>
      </div>

      <div className="space-y-3">
        {data.map((item, index) => (
          <div key={index}