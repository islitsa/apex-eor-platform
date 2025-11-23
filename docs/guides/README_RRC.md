# Texas RRC Data Pipeline for APEX Attribution Engine

Complete setup guide for downloading and processing Texas Railroad Commission data for your APEX EOR platform.

## Project Structure

```
APEX-EOR-PLATFORM/
├── data/
│   ├── raw/
│   │   └── rrc/                    # ← Raw downloaded files
│   │       ├── downloads/          # Original zip/compressed files
│   │       ├── extracted/          # Extracted DBF files
│   │       └── metadata/           # Download metadata (timestamps, checksums)
│   ├── interim/
│   │   └── rrc/                    # ← Cleaned, standardized data
│   │       ├── production_monthly.parquet
│   │       ├── wells.parquet
│   │       ├── shale_wells.parquet
│   │       └── merged_shale_production.parquet
│   ├── processed/
│   │   └── attribution/            # ← Ready for Attribution Engine
│   │       ├── wells_for_attribution.parquet
│   │       ├── production_timeseries.parquet
│   │       └── dataset_metadata.json
│   └── external/                   # Future: Enverus, Novi Labs data
├── scripts/
│   └── download_rrc_data.py        # ← Download script
└── src/
    └── data_collection/
        ├── process_rrc_data.py     # ← Processing script
        └── processors/             # Future: additional processors
```

## Installation

### 1. Install Dependencies

```bash
# Activate your venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install requests pandas pyarrow dbfread geopandas
```

### 2. Save the Scripts

**Download Script:** Save first artifact as `scripts/download_rrc_data.py`
**Processing Script:** Save second artifact as `src/data_collection/process_rrc_data.py`

## Usage

### Step 1: Download Raw Data

```bash
# List available datasets
python scripts/download_rrc_data.py --list

# Download specific datasets
python scripts/download_rrc_data.py \
    --datasets production well_query horizontal_permits \
    --extract

# Or download everything
python scripts/download_rrc_data.py --all --extract
```

**Downloads to:** `data/raw/rrc/downloads/`
**Extracts to:** `data/raw/rrc/extracted/`

### Step 2: Process Data

```bash
# Run full pipeline
python src/data_collection/process_rrc_data.py --steps all

# Or run specific steps
python src/data_collection/process_rrc_data.py \
    --steps production wells filter merge attribution
```

**Interim output:** `data/interim/rrc/`
**Final output:** `data/processed/attribution/`

## Data Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. DOWNLOAD (scripts/download_rrc_data.py)                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
        data/raw/rrc/downloads/PR.zip
        data/raw/rrc/downloads/wellbore_query.zip
                          ↓
                    [Extract]
                          ↓
        data/raw/rrc/extracted/production/*.dbf
        data/raw/rrc/extracted/well_query/*.dbf

┌─────────────────────────────────────────────────────────────┐
│ 2. PROCESS (src/data_collection/process_rrc_data.py)        │
└─────────────────────────────────────────────────────────────┘
                          ↓
        [Read DBF → Clean → Standardize]
                          ↓
        data/interim/rrc/production_monthly.parquet
        data/interim/rrc/wells.parquet
                          ↓
        [Filter for shale wells]
                          ↓
        data/interim/rrc/shale_wells.parquet
                          ↓
        [Merge production + wells]
                          ↓
        data/interim/rrc/merged_shale_production.parquet
                          ↓
        [Prepare for Attribution Engine]
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. READY FOR ATTRIBUTION ENGINE                              │
└─────────────────────────────────────────────────────────────┘
        data/processed/attribution/wells_for_attribution.parquet
        data/processed/attribution/production_timeseries.parquet
        data/processed/attribution/dataset_metadata.json
```

## Using in Attribution Engine

Load the processed data in your Attribution Engine:

```python
import pandas as pd
from pathlib import Path

# Load processed data
processed_dir = Path('./data/processed/attribution')

wells = pd.read_parquet(processed_dir / 'wells_for_attribution.parquet')
production = pd.read_parquet(processed_dir / 'production_timeseries.parquet')

# Get metadata
import json
with open(processed_dir / 'dataset_metadata.json', 'r') as f:
    metadata = json.load(f)

print(f"Loaded {len(wells)} wells")
print(f"Production records: {len(production)}")
print(f"Date range: {metadata['date_range']}")

# Example: Get time series for one well
api_col = metadata['schema']['api_column']
example_api = wells[api_col].iloc[0]
well_prod = production[production[api_col] == example_api]

# Now use in your Attribution Engine decline curve analysis
from src.apex.attribution import DeclineCurveAnalysis

dca = DeclineCurveAnalysis(well_prod)
baseline = dca.establish_baseline()
```

## Available Datasets

| Dataset | Description | Size | Update Frequency |
|---------|-------------|------|------------------|
| `production` | Monthly production by lease | ~500MB | Monthly |
| `well_query` | Well information database | ~200MB | Monthly |
| `wellbore` | Full wellbore database (all TX) | ~2GB | Monthly |
| `horizontal_permits` | Horizontal drilling permits | ~50MB | Daily |
| `completions_daily` | Daily completion forms | ~100MB | Daily |
| `oil_master` | Lease cycle data by county | ~300MB | Monthly |

## Data Quality Notes

### For Attribution Engine Requirements:

✅ **Available:**
- Daily/monthly production by well
- Well coordinates (for parent-child analysis)
- Operator information
- Field/formation data
- Completion dates

⚠️**Limited in free RRC data:**
- Stage-level production (need PLT or allocation algorithms)
- Detailed completion design (stages, clusters, proppant loads)
- Pressure data
- TOC and mineralogy

🎯 **Recommendation:** Start with free RRC data for Bronze tier Attribution Engine. Upgrade to Enverus/Novi Labs for Silver/Gold tier with detailed completion data.

## Next Steps

1. **Test the pipeline:**
   ```bash
   # Download small dataset
   python scripts/download_rrc_data.py --datasets production --extract
   python src/data_collection/process_rrc_data.py --steps all
   ```

2. **Integrate with Attribution Engine:**
   - Create loader in `src/apex/attribution/data_loader.py`
   - Implement decline curve analysis using processed data
   - Add unit tests in `tests/`

3. **Expand data sources:**
   - Add Novi Labs API connector
   - Add state APIs (ND, NM, OK)
   - Implement well allocation algorithms for stage-level data

## Automation

### Daily Updates (for completions and permits):

```bash
# Create cron job or scheduled task
0 6 * * * cd /path/to/APEX-EOR-PLATFORM && \
    ./venv/bin/python scripts/download_rrc_data.py \
    --datasets completions_daily horizontal_permits \
    --extract && \
    ./venv/bin/python src/data_collection/process_rrc_data.py \
    --steps all
```

### Monthly Updates (for production):

```bash
# First of each month
0 2 1 * * cd /path/to/APEX-EOR-PLATFORM && \
    ./venv/bin/python scripts/download_rrc_data.py \
    --datasets production well_query \
    --force --extract && \
    ./venv/bin/python src/data_collection/process_rrc_data.py \
    --steps all
```

## Troubleshooting

### Common Issues:

**"No DBF files found"**
- Make sure you ran download script with `--extract` flag
- Check `data/raw/rrc/extracted/` for files

**"Column not found"**
- RRC changes column names occasionally
- Check logs for actual column names
- Update processing logic if needed

**File size warnings**
- Full wellbore database is 2GB+
- Start with smaller datasets first
- Use `--datasets` to select specific files

**Encoding errors**
- DBF files use latin-1 encoding
- If errors persist, try `encoding='cp1252'` or `'utf-8'`

## Support

- RRC Data Documentation: https://www.rrc.texas.gov/resource-center/research/
- RRC Contact: publicassist@rrc.texas.gov
- Dataset Manual: Check `data/raw/rrc/metadata/` for links

## License

Texas RRC data is public domain. Please review RRC terms of use.