# Data Ingestion Pipeline

Automated data ingestion pipeline for the APEX EOR Platform.

## Overview

This pipeline automates the **download**, **extract**, and **parse** phases of data ingestion for all data sources used in APEX:

- **Texas Railroad Commission (RRC)** - Production, permits, completions
- **FracFocus** - Chemical disclosure data

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Data Ingestion Pipeline                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  PHASE 1: DOWNLOAD                                      │
│  ├─ RRC Production (PDQ_DSV.zip) - 3.4GB               │
│  ├─ RRC Permits (DAF318.txt) - 58MB                    │
│  ├─ RRC Completions (nested ZIPs) - 1.1GB              │
│  └─ FracFocus (FracFocusCSV.zip) - 425MB               │
│                                                         │
│  PHASE 2: EXTRACT                                       │
│  ├─ Unzip archives                                      │
│  ├─ Extract nested structures                          │
│  └─ Organize extracted files                           │
│                                                         │
│  PHASE 3: PARSE                                         │
│  ├─ Convert DSV → CSV (production)                     │
│  ├─ Parse fixed-width (permits)                        │
│  ├─ Parse delimited files (completions)                │
│  └─ Consolidate CSVs (FracFocus)                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Directory Structure

```
scripts/
├── pipeline/
│   ├── run_ingestion.py          # Main pipeline runner
│   ├── extract.py                # Extraction orchestrator
│   ├── parse.py                  # Parsing orchestrator
│   ├── config.yaml               # Configuration
│   └── README.md                 # This file
│
├── downloaders/
│   ├── rrc_downloader.py         # RRC data downloader
│   └── fracfocus_downloader.py   # FracFocus downloader
│
├── extractors/                   # Individual extractors
├── parsers/                      # Individual parsers
└── processors/                   # Data processors
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `requests` - HTTP downloads
- `pandas` - Data parsing
- `tqdm` - Progress bars
- `pyyaml` - Configuration
- `streamlit` - Web UI (for `--ui` flag)
- `anthropic` - UI Agent (for `--ui` flag)

### 2. Launch Web UI (Recommended)

**The easiest way to use the pipeline is through the web interface:**

```bash
# Launch web UI - UI Agent will generate the dashboard and open it in your browser
python scripts/pipeline/run_ingestion.py --ui
```

This will:
1. Initialize the UI Agent
2. Prompt the agent to generate a complete Streamlit dashboard
3. Save the dashboard to `src/ui/pipeline_dashboard.py`
4. Launch the Streamlit server
5. Open your browser to `http://localhost:8501`

The web UI provides:
- Interactive buttons to run each pipeline phase
- Dataset selection with checkboxes
- Real-time progress monitoring
- Visual status indicators
- Log viewer
- Data statistics and charts

### 3. Run Complete Pipeline (CLI)

```bash
# Run all phases for all datasets
python scripts/pipeline/run_ingestion.py --all

# See what would be done (dry run)
python scripts/pipeline/run_ingestion.py --all --dry-run
```

### 4. Run Specific Phases (CLI)

```bash
# Download only
python scripts/pipeline/run_ingestion.py --download

# Extract only
python scripts/pipeline/run_ingestion.py --extract

# Parse only
python scripts/pipeline/run_ingestion.py --parse

# Download and extract
python scripts/pipeline/run_ingestion.py --download --extract
```

### 5. Run for Specific Datasets (CLI)

```bash
# Process only RRC production data
python scripts/pipeline/run_ingestion.py --all --datasets rrc_production

# Process multiple specific datasets
python scripts/pipeline/run_ingestion.py --all --datasets rrc_production fracfocus

# Download only FracFocus
python scripts/pipeline/run_ingestion.py --download --datasets fracfocus
```

### 6. Force Re-download (CLI)

```bash
# Force re-download even if files exist
python scripts/pipeline/run_ingestion.py --download --force
```

## Usage Examples

### Example 1: Launch Web UI (Easiest)

The simplest way to use the pipeline:

```bash
python scripts/pipeline/run_ingestion.py --ui
```

Then use the web interface to:
- Select which datasets to process
- Choose which phases to run
- Monitor progress in real-time
- View logs and statistics

### Example 2: Fresh Install (CLI)

Starting from scratch, download and process everything:

```bash
python scripts/pipeline/run_ingestion.py --all
```

### Example 3: Update Existing Data

Re-download and re-process production data:

```bash
python scripts/pipeline/run_ingestion.py --all --datasets rrc_production --force
```

### Example 4: Parse New Data

If you've manually downloaded data, just parse it:

```bash
python scripts/pipeline/run_ingestion.py --parse --datasets rrc_permits
```

### Example 5: Extract and Parse

If downloads are complete, run extraction and parsing:

```bash
python scripts/pipeline/run_ingestion.py --extract --parse
```

## Components

### Downloaders

Located in `scripts/downloaders/`

#### RRCDownloader

Downloads Texas RRC data:
- Production data (PDQ_DSV.zip)
- Horizontal drilling permits (DAF318.txt)
- Completion packets (requires manual download or web scraping)

```python
from downloaders.rrc_downloader import RRCDownloader

downloader = RRCDownloader()
downloader.download_production()
downloader.download_permits()
```

#### FracFocusDownloader

Downloads FracFocus chemical disclosure data:

```python
from downloaders.fracfocus_downloader import FracFocusDownloader

downloader = FracFocusDownloader()
downloader.download_csv_bulk()
```

### ExtractionOrchestrator

Located in `scripts/pipeline/extract.py`

Handles extraction of all compressed archives:
- ZIP files (single and nested)
- Organizing extracted files
- Metadata tracking

```python
from pipeline.extract import ExtractionOrchestrator

extractor = ExtractionOrchestrator()
extractor.extract_all()
```

### ParsingOrchestrator

Located in `scripts/pipeline/parse.py`

Converts extracted data to structured formats:
- DSV → CSV (RRC production)
- Fixed-width → CSV (RRC permits)
- Delimited files → CSV (RRC completions)
- CSV consolidation (FracFocus)

```python
from pipeline.parse import ParsingOrchestrator

parser = ParsingOrchestrator()
parser.parse_all()
```

## Data Flow

### RRC Production Data

```
PDQ_DSV.zip (3.4GB)
  ↓ DOWNLOAD
downloads/PDQ_DSV.zip
  ↓ EXTRACT
extracted/OG_LEASE_CYCLE_DATA_TABLE.dsv (33GB)
extracted/OG_COUNTY_LEASE_CYCLE_DATA_TABLE.dsv
extracted/... (16 .dsv files total)
  ↓ PARSE
parsed/OG_LEASE_CYCLE_DATA_TABLE.csv
parsed/... (16 .csv files)
```

### RRC Horizontal Permits

```
daf318.txt (58MB)
  ↓ DOWNLOAD
downloads/daf318.txt
  ↓ EXTRACT (copy)
extracted/daf318.txt
  ↓ PARSE (fixed-width)
parsed/horizontal_permits.csv (168K records)
```

### RRC Completion Packets

```
completion_YYYYMMDD.zip (1.1GB total)
  ↓ DOWNLOAD (manual)
downloads/completion_20250101.zip
downloads/completion_20250102.zip
...
  ↓ EXTRACT (nested)
extracted/20250101/district_01/tracking_12345/packetData_G1.dat
extracted/20250101/district_01/tracking_12345/packetData_W2.dat
...
  ↓ PARSE
parsed/PACKET_DATA.csv
parsed/G1_RECORDS.csv
parsed/W2_RECORDS.csv
... (28 CSV tables)
```

### FracFocus Data

```
FracFocusCSV.zip (425MB)
  ↓ DOWNLOAD
downloads/FracFocusCSV.zip
  ↓ EXTRACT
extracted/FracFocusRegistry_1.csv
extracted/FracFocusRegistry_2.csv
... (17 CSV files)
  ↓ PARSE (organize)
parsed/FracFocusRegistry_1.csv
parsed/FracFocusRegistry_2.csv
... (17 CSV files)
```

## Configuration

Edit `config.yaml` to customize:
- Data source URLs
- File paths
- Processing options
- Timeout settings
- Output formats

## Metadata Tracking

Each dataset maintains a `metadata.json` file tracking:
- Download date and source URL
- File checksums (MD5)
- Processing state (download, extraction, parsing)
- File counts and record counts
- Data quality notes

Example metadata structure:

```json
{
  "processing_state": {
    "download": "complete",
    "download_date": "2025-01-15T10:30:00",
    "extraction": "complete",
    "extraction_date": "2025-01-15T10:35:00",
    "parsing": "complete",
    "parsing_date": "2025-01-15T11:00:00",
    "parsed_files": 16,
    "total_files": 16
  },
  "last_download": {
    "source_url": "https://...",
    "file_size": 3600000000,
    "md5_checksum": "abc123..."
  }
}
```

## Error Handling

The pipeline includes robust error handling:

- **Download failures**: Automatically retry, clean up partial downloads
- **Extraction errors**: Log warnings, continue with other files
- **Parsing errors**: Skip bad records with warnings, continue processing
- **Missing files**: Clear error messages, graceful degradation

## Performance

Typical processing times (varies by system):

| Phase | Dataset | Time | Output Size |
|-------|---------|------|-------------|
| Download | RRC Production | 5-10 min | 3.4GB |
| Download | FracFocus | 2-5 min | 425MB |
| Extract | RRC Production | 3-5 min | 33GB |
| Extract | FracFocus | 1-2 min | 3.1GB |
| Parse | RRC Production | 10-20 min | 33GB CSV |
| Parse | RRC Permits | 1-2 min | 45MB CSV |

**Total pipeline time**: Approximately 30-60 minutes for all datasets

## Storage Requirements

Ensure adequate disk space:

| Stage | Size Required |
|-------|---------------|
| Downloads only | ~5GB |
| Downloads + Extracted | ~40GB |
| Full pipeline (all stages) | ~75GB |

## Next Steps

After running the ingestion pipeline:

1. **Validate Data** - Check parsed files for completeness
2. **Load to Database** - Import CSV files to DuckDB or PostgreSQL
3. **Run Processors** - Execute data processors in `scripts/processors/`
4. **Link Datasets** - Merge data via API numbers
5. **Run Analysis** - Execute analysis scripts in `scripts/analysis/`

## Troubleshooting

### Download Issues

**Problem**: Download times out or fails

**Solution**:
```bash
# Increase timeout in downloaders (edit the script)
# Or download manually and skip download phase
python scripts/pipeline/run_ingestion.py --extract --parse
```

### Extraction Issues

**Problem**: ZIP file is corrupted

**Solution**:
```bash
# Re-download with force flag
python scripts/pipeline/run_ingestion.py --download --force --datasets rrc_production
```

### Parsing Issues

**Problem**: Parsing fails on malformed data

**Solution**:
- Check error messages for specific files
- Review source data quality
- Adjust parser error handling (in `parse.py`)

### Storage Issues

**Problem**: Running out of disk space

**Solution**:
```bash
# Process one dataset at a time
python scripts/pipeline/run_ingestion.py --all --datasets rrc_permits

# Delete intermediate files after validation
rm -rf data/raw/rrc/production/extracted/
```

## Contributing

To add a new data source:

1. Create downloader in `scripts/downloaders/`
2. Add extraction logic to `extract.py`
3. Add parsing logic to `parse.py`
4. Update `config.yaml`
5. Add to `AVAILABLE_DATASETS` in `run_ingestion.py`

## License

This pipeline is part of the APEX EOR Platform. See main project LICENSE.

## Support

For issues or questions:
- Check existing data documentation in `data/raw/*/README.md`
- Review individual script documentation
- Consult main project README
