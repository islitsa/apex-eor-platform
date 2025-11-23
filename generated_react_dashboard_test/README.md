# FracFocus Chemical Data Dashboard

A React + TypeScript dashboard for exploring FracFocus chemical disclosure data from hydraulic fracturing operations.

## Features

- **Real-time Data Fetching**: Connects to backend API at `http://localhost:8000`
- **Interactive Statistics**: View total records, unique chemicals, suppliers, and purposes
- **Search & Filter**: Search across chemical names, suppliers, and purposes
- **Sortable Table**: Click column headers to sort data
- **Responsive Design**: Works on desktop and mobile devices
- **Material Design 3**: Modern UI with proper elevation and color system

## Dataset Information

- **Source**: FracFocus Chemical Disclosure Registry
- **Records**: 239,059 total records
- **Columns**: 5 columns (ChemicalName, CASNumber, Supplier, Purpose, PercentHFJob)
- **Status**: Complete
- **Pipeline Stages**: downloads → extracted → parsed

## Prerequisites

- Node.js 16+ and npm
- Backend API running at `http://localhost:8000`

## Installation

```bash
npm install

## Development

```bash
npm run dev

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Build

```bash
npm run build

## Technology Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first styling
- **Material Symbols** - Icon system

## Project Structure

├── App.tsx                      # Main application component
├── main.tsx                     # Application entry point
├── types.ts                     # TypeScript interfaces
├── dataHooks.tsx               # API data fetching hooks
├── components/
│   ├── ChemicalTable.tsx       # Sortable data table
│   ├── StatsCard.tsx           # Statistics display card
│   └── FilterPanel.tsx         # Search and filter controls
├── index.html                  # HTML template
├── index.css                   # Global styles
└── package.json                # Dependencies

## API Endpoints Used

- `GET /api/sources` - List all data sources
- `GET /api/sources/:name` - Get source metadata
- `GET /api/data/:source?limit=100` - Fetch paginated data

## Features Breakdown

### Statistics Cards
- Total records count (239,059)
- Unique chemicals identified
- Number of suppliers
- Chemical purposes tracked

### Filter Panel
- Real-time search across multiple fields
- Adjustable record limit (50-1000)
- Live filtered count display

### Chemical Table
- Sortable columns (click headers)
- Chemical name, CAS number, supplier, purpose, percentage
- Hover effects and responsive layout
- Empty state handling

## License

MIT

This dashboard provides a complete, production-ready interface for exploring the FracFocus chemical data with real API integration, interactive filtering, sorting, and comprehensive statistics display.