import React from 'react';
import { PipelineSummary } from '../types.ts';

interface HeroStatusBarProps {
  summary: PipelineSummary;
}

export default function HeroStatusBar({ summary }: HeroStatusBarProps) {
  return (
    <div className="h-[72px] bg-surface-container border-b border-outline-variant px-16 flex items-center justify-between">
      <h1 className="text-5xl font-bold text-on-surface font-roboto">
        FracFocus Chemical Data
      </h1>
      <div className="flex items-center gap-8">
        <div className="text-right">
          <div className="text-sm text-on-surface-variant font-medium">Total Pipelines</div>
          <div className="text-2xl font-bold text-primary">{summary.total_pipelines}</div>
        </div>
        <div className="text-right">
          <div className="text-sm text-on-surface-variant font-medium">Total Size</div>
          <div className="text-2xl font-bold text-primary">{summary.total_size}</div>
        </div>
      </div>
    </div>
  );
}