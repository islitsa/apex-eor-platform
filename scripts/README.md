# Scripts Organization

This directory contains all data processing, analysis, and utility scripts for the APEX EOR Platform.

## Directory Structure

```
scripts/
├── parsers/              # Format-specific parsers for raw data
├── processors/           # Data processing/transformation scripts
├── extractors/           # Data extraction utilities
├── analysis/             # Analysis and research scripts
└── utils/                # General utility scripts
```

## Module Descriptions

### 📄 parsers/
Format-specific parsers that convert raw data files into structured formats (CSV, Parquet, DataFrames).

**Current Parsers:**
- `parse_daf318.py` - Texas RRC Horizontal Drilling Permits (DAF318 fixed-width format)

**Usage Example:**
```python
from scripts.parsers import DAF318Parser

parser = DAF318Parser()
df = parser.parse_file('data/raw/rrc/downloads/.../daf318')
parser.export_to_parquet(input_file, output_file)
```

### ⚙️ processors/
Scripts that transform, clean, enrich, and merge data from various sources.

**Current Processors:**
- `process_rrc_production_data.py` - Process Texas RRC production data
- `process_completion_packets.py` - Process well completion packets
- `process_fracfocus_data.py` - Process FracFocus chemical disclosure data
- `merge_production_with_formations.py` - Merge production with geological formation data
- `merge_treatments_with_production.py` - Merge treatment data with production metrics

### 📦 extractors/
Utilities for extracting data from compressed archives, nested structures, and complex file formats.

**Current Extractors:**
- `extract_nested_zips.py` - Extract nested ZIP archives
- `extract_well_design.py` - Extract well design data from completion packets

### 📊 analysis/
Analysis and research scripts for generating insights, reports, and visualizations.

**Current Analysis Scripts:**
- `analyze_fracfocus_eor.py` - Analyze FracFocus data for EOR applications

### 🛠️ utils/
General utility and helper scripts for debugging, testing, and common operations.

**Current Utilities:**
- `debug_folder_structure.py` - Debug and analyze folder structures
- `test.py` - Testing utilities

## Data Flow

The typical data processing pipeline follows this flow:

```
1. EXTRACTORS → Extract raw data from archives
        ↓
2. PARSERS → Parse proprietary/fixed-width formats into structured data
        ↓
3. PROCESSORS → Clean, transform, merge, and enrich data
        ↓
4. ANALYSIS → Generate insights and research outputs
```

## Adding New Scripts

### Where to place new scripts:

- **Parser**: Converting a new raw data format (e.g., DBF, fixed-width, proprietary) → `parsers/`
- **Processor**: Transforming/cleaning/merging data → `processors/`
- **Extractor**: Extracting from archives or complex structures → `extractors/`
- **Analysis**: Research, insights, or reporting → `analysis/`
- **Utility**: General helpers, debugging tools → `utils/`

### Naming Conventions:

- **Parsers**: `parse_<format>.py` (e.g., `parse_daf318.py`, `parse_daf420.py`)
- **Processors**: `process_<data_source>.py` or `merge_<source1>_with_<source2>.py`
- **Extractors**: `extract_<what>.py`
- **Analysis**: `analyze_<subject>.py`
- **Utils**: `<descriptive_name>.py`

## Running Scripts

Most scripts can be run directly:

```bash
# Run a parser
python scripts/parsers/parse_daf318.py

# Run a processor
python scripts/processors/process_rrc_production_data.py

# Run an analysis
python scripts/analysis/analyze_fracfocus_eor.py
```

Or imported as modules:

```python
from scripts.parsers import DAF318Parser
from scripts.processors import process_completion_packets
```

## Data Sources

- **Texas RRC** - Railroad Commission of Texas (oil & gas regulatory data)
- **FracFocus** - Chemical disclosure registry for hydraulic fracturing
- **Completion Packets** - Well completion reports and design data

## Contributing

When adding new scripts:
1. Place in the appropriate directory based on function
2. Follow naming conventions
3. Add docstrings at module and function level
4. Update the relevant `__init__.py` file
5. Update this README with script description

## Questions?

For questions about script organization or usage, contact the data engineering team.
