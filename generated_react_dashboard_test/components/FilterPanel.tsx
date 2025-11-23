import React from 'react';
import { FilterPanelProps } from '../types.ts';

export default function FilterPanel({
  searchTerm,
  onSearchChange,
  limit,
  onLimitChange,
  totalRecords,
  filteredCount,
}: FilterPanelProps) {
  const limitOptions = [50, 100, 250, 500, 1000];

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6 mb-6">
      <div className="flex flex-col lg:flex-row gap-4">
        {/* Search Input */}
        <div className="flex-1">
          <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-2">
            Search Chemicals, Suppliers, or Purposes
          </label>
          <div className="relative">
            <span className="material-symbols-rounded absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
              search
            </span>
            <input
              id="search"
              type="text"
              value={searchTerm}
              onChange={(e) => onSearchChange(e.target.value)}
              placeholder="Type to search..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            />
          </div>
        </div>

        {/* Limit Selector */}
        <div className="lg:w-48">
          <label htmlFor="limit" className="block text-sm font-medium text-gray-700 mb-2">
            Records to Load
          </label>
          <select
            id="limit"
            value={limit}
            onChange={(e) => onLimitChange(Number(e.target.value))}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none bg-white"
          >
            {limitOptions.map((option) => (
              <option key={option} value={option}>
                {option} records
              </option>
            ))}
          </select>
        </div>

        {/* Results Count */}
        <div className="lg:w-48 flex items-end">
          <div className="bg-gray-50 rounded-lg px-4 py-2 w-full border border-gray-200">
            <p className="text-sm text-gray-600">Showing</p>
            <p className="text-lg font-semibold text-gray-900">
              {filteredCount.toLocaleString()} / {totalRecords.toLocaleString()}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}