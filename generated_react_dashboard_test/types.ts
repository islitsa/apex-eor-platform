export interface ChemicalRecord {
  ChemicalName?: string;
  CASNumber?: string;
  Supplier?: string;
  Purpose?: string;
  PercentHFJob?: number | string;
  [key: string]: any;
}

export interface DataSourceInfo {
  name: string;
  status: string;
  columns?: string[];
  rowCount?: number;
}

export interface StatsCardProps {
  icon: string;
  label: string;
  value: string;
  color: 'blue' | 'green' | 'purple' | 'orange';
}

export interface FilterPanelProps {
  searchTerm: string;
  onSearchChange: (value: string) => void;
  limit: number;
  onLimitChange: (value: number) => void;
  totalRecords: number;
  filteredCount: number;
}

export interface ChemicalTableProps {
  data: ChemicalRecord[];
}