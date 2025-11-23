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
  record_count?: number;
  column_count?: number;
  status?: string;
  stages?: string[];
}

export interface StatsCardProps {
  icon: string;
  label: string;
  value: string;
  color: 'blue' | 'purple' | 'green' | 'orange';
}

export interface FilterPanelProps {
  searchTerm: string;
  onSearchChange: (value: string) => void;
  limit: number;
  onLimitChange: (value: number) => void;
  resultCount: number;
  totalCount: number;
}

export interface ChemicalTableProps {
  data: ChemicalRecord[];
}