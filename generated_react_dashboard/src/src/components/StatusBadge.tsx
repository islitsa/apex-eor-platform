import React from 'react';
import { getStatusColor } from '../utils.ts';

interface StatusBadgeProps {
  status: string;
  className?: string;
}

export default function StatusBadge({ status, className = '' }: StatusBadgeProps) {
  return (
    <span
      className={`inline-flex items-center px-3 h-8 rounded-full text-sm font-medium transition-colors duration-300 ${getStatusColor(status)} ${className}`}
    >
      {status.replace('_', ' ')}
    </span>
  );
}