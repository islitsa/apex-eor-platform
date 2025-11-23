import React, { useState, useMemo } from 'react';
import { useDataSource, useDataSourceInfo } from './dataHooks.tsx';
import ChemicalTable from './components/ChemicalTable.tsx';
import StatsCard from './components/StatsCard.tsx';
import FilterPanel from './components/FilterPanel.tsx';
import { ChemicalRecord } from './types.ts';

export default function App() {
  const [limit, setLimit] = useState(100);
  const [searchTerm, setSearchTerm] = useState('');
  
  const { info, loading: infoLoading } = useDataSourceInfo('fracfocus');
  const { data, total, loading, error } = useDataSource('fracfocus', { limit });

  // Calculate statistics from data
  const stats = useMemo(() => {
    if (!data || data.length === 0) return null;

    const chemicals = new Set<string>();
    const suppliers = new Set<string>();
    const purposes = new Set<string>();
    
    data.forEach((record: ChemicalRecord) => {
      if (record.ChemicalName) chemicals.add(record.ChemicalName);
      if (record.Supplier) suppliers.add(record.Supplier);
      if (record.Purpose) purposes.add(record.Purpose);
    });

    return {
      totalRecords: total,
      uniqueChemicals: chemicals.size,
      uniqueSuppliers: suppliers.size,
      uniquePurposes: purposes.size,
    };
  }, [data, total]);

  // Filter data based on search term
  const filteredData = useMemo(() => {
    if (!data || !searchTerm) return data;
    
    const term = searchTerm.toLowerCase();
    return data.filter((record: ChemicalRecord) => 
      record.ChemicalName?.toLowerCase().includes(term) ||
      record.Supplier?.toLowerCase().includes(term) ||
      record.Purpose?.toLowerCase().includes(term)
    );
  }, [data, searchTerm]);

  if (infoLoading || loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-gray-600 text-lg">Loading FracFocus data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <div className="flex items-center gap-3 mb-2">
            <span className="material-symbols-rounded text-red-600 text-3xl">error</span>
            <h2 className="text-xl font-semibold text-red-900">Error Loading Data</h2>
          </div>
          <p className="text-red-700">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center gap-3">
            <span className="material-symbols-rounded text-blue-600 text-4xl">science</span>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">FracFocus Chemical Data</h1>
              <p className="text-gray-600 mt-1">
                Hydraulic fracturing chemical disclosure registry
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Data Source Info */}
        {info && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <div className="flex items-start gap-3">
              <span className="material-symbols-rounded text-blue-600 text-2xl">info</span>
              <div className="flex-1">
                <h3 className="font-semibold text-blue-900 mb-1">Dataset Information</h3>
                <div className="text-sm text-blue-800 space-y-1">
                  <p><strong>Records:</strong> {info.record_count?.toLocaleString() || 'N/A'}</p>
                  <p><strong>Columns:</strong> {info.column_count || 'N/A'}</p>
                  <p><strong>Status:</strong> <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                    {info.status || 'complete'}
                  </span></p>
                  <p><strong>Pipeline:</strong> downloads → extracted → parsed</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Statistics Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <StatsCard
              icon="database"
              label="Total Records"
              value={stats.totalRecords.toLocaleString()}
              color="blue"
            />
            <StatsCard
              icon="science"
              label="Unique Chemicals"
              value={stats.uniqueChemicals.toLocaleString()}
              color="purple"
            />
            <StatsCard
              icon="factory"
              label="Suppliers"
              value={stats.uniqueSuppliers.toLocaleString()}
              color="green"
            />
            <StatsCard
              icon="category"
              label="Purposes"
              value={stats.uniquePurposes.toLocaleString()}
              color="orange"
            />
          </div>
        )}

        {/* Filter Panel */}
        <FilterPanel
          searchTerm={searchTerm}
          onSearchChange={setSearchTerm}
          limit={limit}
          onLimitChange={setLimit}
          resultCount={filteredData?.length || 0}
          totalCount={total}
        />

        {/* Chemical Data Table */}
        <ChemicalTable data={filteredData || []} />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-gray-600 text-sm">
            Data from FracFocus Chemical Disclosure Registry • {total.toLocaleString()} total records
          </p>
        </div>
      </footer>
    </div>
  );
}