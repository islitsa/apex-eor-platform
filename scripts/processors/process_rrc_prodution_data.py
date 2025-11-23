"""
Texas RRC DSV Data Processor
Processes RRC pipe-delimited (}) data for APEX Attribution Engine

Reads from: data/raw/rrc/downloads/*.dsv
Outputs to: data/interim/rrc/ and data/processed/attribution/

Usage:
    python src/data_collection/process_rrc_data.py --steps all
"""

import pandas as pd
from pathlib import Path
import logging
import argparse
import json
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RRCDataProcessor:
    """
    Process raw RRC DSV data for APEX Attribution Engine
    
    Handles pipe-delimited (}) files from Texas RRC
    """
    
    def __init__(self, 
                 raw_dir='./data/raw/rrc',
                 interim_dir='./data/interim/rrc',
                 processed_dir='./data/processed/attribution'):
        
        self.raw_dir = Path(raw_dir)
        self.interim_dir = Path(interim_dir)
        self.processed_dir = Path(processed_dir)
        
        # Create directories
        self.interim_dir.mkdir(exist_ok=True, parents=True)
        self.processed_dir.mkdir(exist_ok=True, parents=True)
        
        logger.info(f"Raw: {self.raw_dir}")
        logger.info(f"Interim: {self.interim_dir}")
        logger.info(f"Processed: {self.processed_dir}")
    
    def process_production_data(self):
        """
        Process lease-level production data (OG_LEASE_CYCLE_DATA_TABLE.dsv)
        
        Outputs to: data/interim/rrc/production_monthly.parquet
        
        Returns:
            DataFrame with cleaned production data
        """
        logger.info("Processing production data...")
        
        # Look for production DSV file
        prod_file = self.raw_dir / 'downloads' / 'OG_LEASE_CYCLE_DATA_TABLE.dsv'
        
        if not prod_file.exists():
            logger.error(f"Production data not found at {prod_file}")
            return None
        
        logger.info(f"Reading production DSV: {prod_file}")
        logger.info("This may take a few minutes for large files...")
        
        try:
            # Read pipe-delimited file
            prod_df = pd.read_csv(
                prod_file, 
                sep='}',  # RRC uses } as delimiter
                low_memory=False,
                dtype={
                    'LEASE_NO': str,
                    'DISTRICT_NO': str,
                    'OPERATOR_NO': str,
                    'CYCLE_YEAR': str,
                    'CYCLE_MONTH': str,
                }
            )
            logger.info(f"Loaded {len(prod_df):,} production records")
            
        except Exception as e:
            logger.error(f"Failed to read production data: {e}")
            return None
        
        # Show columns
        logger.info(f"Columns: {prod_df.columns.tolist()}")
        
        # Data cleaning
        logger.info("Cleaning production data...")
        
        # Create full API/Lease identifier
        prod_df['LEASE_ID'] = (prod_df['LEASE_NO'].astype(str).str.zfill(6) + 
                               prod_df['DISTRICT_NO'].astype(str).str.zfill(2))
        
        # Parse date from CYCLE_YEAR_MONTH
        if 'CYCLE_YEAR_MONTH' in prod_df.columns:
            prod_df['PRODUCTION_DATE'] = pd.to_datetime(
                prod_df['CYCLE_YEAR_MONTH'].astype(str), 
                format='%Y%m',
                errors='coerce'
            )
        
        # Convert production volumes to numeric
        prod_cols = [
            'LEASE_OIL_PROD_VOL',
            'LEASE_GAS_PROD_VOL', 
            'LEASE_COND_PROD_VOL',
            'LEASE_CSGD_PROD_VOL'
        ]
        for col in prod_cols:
            if col in prod_df.columns:
                prod_df[col] = pd.to_numeric(prod_df[col], errors='coerce')
        
        # Filter out records with no production
        initial_count = len(prod_df)
        prod_df = prod_df[
            (prod_df['LEASE_OIL_PROD_VOL'] > 0) | 
            (prod_df['LEASE_GAS_PROD_VOL'] > 0)
        ].copy()
        logger.info(f"Filtered: {initial_count:,} → {len(prod_df):,} records with production")
        
        # Save to interim
        output_path = self.interim_dir / 'production_monthly.parquet'
        prod_df.to_parquet(output_path, index=False)
        logger.info(f"✓ Saved to {output_path}")
        
        return prod_df
    
    def process_completion_data(self):
        """
        Process well completion data (OG_WELL_COMPLETION_DATA_TABLE.dsv)
        
        Outputs to: data/interim/rrc/well_completions.parquet
        
        Returns:
            DataFrame with well completion info
        """
        logger.info("Processing well completion data...")
        
        comp_file = self.raw_dir / 'downloads' / 'OG_WELL_COMPLETION_DATA_TABLE.dsv'
        
        if not comp_file.exists():
            logger.error(f"Completion data not found at {comp_file}")
            return None
        
        logger.info(f"Reading completion DSV: {comp_file}")
        
        try:
            comp_df = pd.read_csv(
                comp_file,
                sep='}',
                low_memory=False,
                dtype={
                    'LEASE_NO': str,
                    'DISTRICT_NO': str,
                    'API_COUNTY_CODE': str,
                    'API_UNIQUE_NO': str,
                }
            )
            logger.info(f"Loaded {len(comp_df):,} completion records")
            
        except Exception as e:
            logger.error(f"Failed to read completion data: {e}")
            return None
        
        logger.info(f"Columns: {comp_df.columns.tolist()}")
        
        # Create identifiers
        comp_df['LEASE_ID'] = (comp_df['LEASE_NO'].astype(str).str.zfill(6) + 
                               comp_df['DISTRICT_NO'].astype(str).str.zfill(2))
        
        # Create full API number
        if 'API_COUNTY_CODE' in comp_df.columns and 'API_UNIQUE_NO' in comp_df.columns:
            comp_df['API_NUMBER'] = (
                '42' +  # Texas state code
                comp_df['API_COUNTY_CODE'].astype(str).str.zfill(3) +
                comp_df['API_UNIQUE_NO'].astype(str).str.zfill(5)
            )
        
        # Save to interim
        output_path = self.interim_dir / 'well_completions.parquet'
        comp_df.to_parquet(output_path, index=False)
        logger.info(f"✓ Saved to {output_path}")
        
        return comp_df
    
    def filter_shale_wells(self, prod_df=None):
        """
        Filter for shale/tight oil horizontal wells
        
        Focus on:
        - Eagle Ford
        - Permian Basin formations (Wolfcamp, Bone Spring, Spraberry)
        - Other shale plays
        
        Outputs to: data/interim/rrc/shale_production.parquet
        """
        logger.info("Filtering for shale wells...")
        
        if prod_df is None:
            prod_path = self.interim_dir / 'production_monthly.parquet'
            if not prod_path.exists():
                logger.error("Production data not processed yet")
                return None
            prod_df = pd.read_parquet(prod_path)
        
        # Shale formation patterns in field names
        shale_formations = [
            'EAGLE FORD',
            'WOLFCAMP',
            'BONE SPRING',
            'SPRABERRY',
            'DEAN',
            'BARNETT',
            'HAYNESVILLE',
            'AVALON',
            'LEONARD',
        ]
        
        # Check FIELD_NAME column
        if 'FIELD_NAME' not in prod_df.columns:
            logger.warning("No FIELD_NAME column found")
            return prod_df
        
        # Filter for shale formations
        pattern = '|'.join(shale_formations)
        mask = prod_df['FIELD_NAME'].astype(str).str.contains(
            pattern, 
            case=False, 
            na=False
        )
        
        shale_df = prod_df[mask].copy()
        
        logger.info(f"Filtered: {len(prod_df):,} → {len(shale_df):,} shale well records")
        
        # Show top formations
        if len(shale_df) > 0:
            top_fields = shale_df['FIELD_NAME'].value_counts().head(10)
            logger.info(f"Top shale fields:\n{top_fields}")
        
        # Save
        output_path = self.interim_dir / 'shale_production.parquet'
        shale_df.to_parquet(output_path, index=False)
        logger.info(f"✓ Saved to {output_path}")
        
        return shale_df
    
    def merge_production_and_completions(self, prod_df=None, comp_df=None):
        """
        Merge production and completion data by LEASE_ID
        
        Outputs to: data/interim/rrc/merged_shale_data.parquet
        
        Returns:
            Merged DataFrame
        """
        logger.info("Merging production and completion data...")
        
        # Load if not provided
        if prod_df is None:
            prod_path = self.interim_dir / 'shale_production.parquet'
            if not prod_path.exists():
                logger.error("Shale production data not processed yet")
                return None
            prod_df = pd.read_parquet(prod_path)
        
        if comp_df is None:
            comp_path = self.interim_dir / 'well_completions.parquet'
            if not comp_path.exists():
                logger.warning("Completion data not available, skipping merge")
                return prod_df
            comp_df = pd.read_parquet(comp_path)
        
        logger.info(f"Merging on LEASE_ID")
        
        # Merge
        merged = prod_df.merge(
            comp_df,
            on='LEASE_ID',
            how='left',
            suffixes=('', '_comp')
        )
        
        logger.info(f"Merged: {len(merged):,} records")
        
        # Save
        output_path = self.interim_dir / 'merged_shale_data.parquet'
        merged.to_parquet(output_path, index=False)
        logger.info(f"✓ Saved to {output_path}")
        
        return merged
    
    def prepare_for_attribution_engine(self, merged_df=None):
        """
        Prepare final dataset for APEX Attribution Engine
        
        Creates:
        1. Well-level summary (data/processed/attribution/wells_for_attribution.parquet)
        2. Time-series production (data/processed/attribution/production_timeseries.parquet)
        3. Metadata (data/processed/attribution/dataset_metadata.json)
        """
        logger.info("Preparing data for Attribution Engine...")
        
        if merged_df is None:
            merged_path = self.interim_dir / 'merged_shale_data.parquet'
            if not merged_path.exists():
                # Try just shale production
                merged_path = self.interim_dir / 'shale_production.parquet'
                if not merged_path.exists():
                    logger.error("No processed data found")
                    return None
            merged_df = pd.read_parquet(merged_path)
        
        logger.info(f"Processing {len(merged_df):,} records...")
        
        # 1. Create well-level summary (one row per well/lease)
        logger.info("Creating well-level summary...")
        
        agg_dict = {
            'OPERATOR_NAME': 'first',
            'FIELD_NAME': 'first',
            'COUNTY_NAME': 'first' if 'COUNTY_NAME' in merged_df.columns else lambda x: None,
            'LEASE_OIL_PROD_VOL': 'sum',
            'LEASE_GAS_PROD_VOL': 'sum',
            'PRODUCTION_DATE': ['min', 'max'],
        }
        
        # Add API if available
        if 'API_NUMBER' in merged_df.columns:
            agg_dict['API_NUMBER'] = 'first'
        
        well_summary = merged_df.groupby('LEASE_ID').agg(agg_dict).reset_index()
        
        # Flatten column names
        well_summary.columns = ['_'.join(col).strip('_') if col[1] else col[0] 
                                for col in well_summary.columns.values]
        
        # Rename for clarity
        well_summary = well_summary.rename(columns={
            'PRODUCTION_DATE_min': 'FIRST_PRODUCTION_DATE',
            'PRODUCTION_DATE_max': 'LAST_PRODUCTION_DATE',
            'LEASE_OIL_PROD_VOL_sum': 'CUMULATIVE_OIL_BBL',
            'LEASE_GAS_PROD_VOL_sum': 'CUMULATIVE_GAS_MCF',
        })
        
        well_summary_path = self.processed_dir / 'wells_for_attribution.parquet'
        well_summary.to_parquet(well_summary_path, index=False)
        logger.info(f"✓ Well summary: {well_summary_path} ({len(well_summary):,} wells)")
        
        # 2. Time-series production data
        logger.info("Creating time-series data...")
        
        time_series_cols = [
            'LEASE_ID', 'PRODUCTION_DATE', 'CYCLE_YEAR_MONTH',
            'LEASE_OIL_PROD_VOL', 'LEASE_GAS_PROD_VOL',
            'OPERATOR_NAME', 'FIELD_NAME'
        ]
        
        # Include only columns that exist
        time_series_cols = [col for col in time_series_cols if col in merged_df.columns]
        
        time_series = merged_df[time_series_cols].copy()
        time_series = time_series.sort_values(['LEASE_ID', 'PRODUCTION_DATE'])
        
        timeseries_path = self.processed_dir / 'production_timeseries.parquet'
        time_series.to_parquet(timeseries_path, index=False)
        logger.info(f"✓ Time series: {timeseries_path} ({len(time_series):,} records)")
        
        # 3. Create metadata
        metadata = {
            'created_at': datetime.now().isoformat(),
            'source': 'Texas Railroad Commission',
            'file_format': 'DSV (pipe-delimited with })',
            'well_count': len(well_summary),
            'production_records': len(time_series),
            'date_range': {
                'start': str(merged_df['PRODUCTION_DATE'].min()),
                'end': str(merged_df['PRODUCTION_DATE'].max()),
            },
            'formations': merged_df['FIELD_NAME'].value_counts().head(20).to_dict() if 'FIELD_NAME' in merged_df.columns else {},
            'schema': {
                'lease_id_column': 'LEASE_ID',
                'date_column': 'PRODUCTION_DATE',
                'oil_column': 'LEASE_OIL_PROD_VOL',
                'gas_column': 'LEASE_GAS_PROD_VOL',
            }
        }
        
        metadata_path = self.processed_dir / 'dataset_metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        logger.info(f"✓ Metadata: {metadata_path}")
        
        return {
            'well_summary': well_summary,
            'time_series': time_series,
            'metadata': metadata
        }


def main():
    parser = argparse.ArgumentParser(
        description='Process raw RRC DSV data for APEX Attribution Engine'
    )
    parser.add_argument(
        '--steps',
        nargs='+',
        choices=['production', 'completions', 'filter', 'merge', 'attribution', 'all'],
        default=['all'],
        help='Processing steps to run'
    )
    parser.add_argument(
        '--raw-dir',
        default='./data/raw/rrc',
        help='Raw data directory'
    )
    parser.add_argument(
        '--interim-dir',
        default='./data/interim/rrc',
        help='Interim data directory'
    )
    parser.add_argument(
        '--processed-dir',
        default='./data/processed/attribution',
        help='Processed data directory'
    )
    
    args = parser.parse_args()
    
    # Initialize processor
    processor = RRCDataProcessor(
        raw_dir=args.raw_dir,
        interim_dir=args.interim_dir,
        processed_dir=args.processed_dir
    )
    
    steps = args.steps if 'all' not in args.steps else [
        'production', 'completions', 'filter', 'merge', 'attribution'
    ]
    
    print("\n" + "=" * 80)
    print("RRC DSV Data Processing Pipeline")
    print("=" * 80)
    
    results = {}
    
    # Execute steps
    if 'production' in steps:
        print("\n[1/5] Processing production data...")
        results['production'] = processor.process_production_data()
    
    if 'completions' in steps:
        print("\n[2/5] Processing completion data...")
        results['completions'] = processor.process_completion_data()
    
    if 'filter' in steps:
        print("\n[3/5] Filtering for shale wells...")
        results['shale'] = processor.filter_shale_wells(results.get('production'))
    
    if 'merge' in steps:
        print("\n[4/5] Merging production and completion data...")
        results['merged'] = processor.merge_production_and_completions(
            results.get('shale'),
            results.get('completions')
        )
    
    if 'attribution' in steps:
        print("\n[5/5] Preparing for Attribution Engine...")
        results['attribution'] = processor.prepare_for_attribution_engine(
            results.get('merged')
        )
    
    # Summary
    print("\n" + "=" * 80)
    print("Processing Complete!")
    print("=" * 80)
    print(f"\nInterim data: {processor.interim_dir}")
    print(f"Processed data: {processor.processed_dir}")
    
    if results.get('attribution'):
        metadata = results['attribution']['metadata']
        print(f"\n✓ {metadata['well_count']:,} shale wells processed")
        print(f"✓ {metadata['production_records']:,} production records")
        print(f"✓ Date range: {metadata['date_range']['start']} to {metadata['date_range']['end']}")
        
        print("\nTop formations:")
        for field, count in list(metadata['formations'].items())[:5]:
            print(f"  - {field}: {count:,} records")
    
    print("\n✓ Ready for APEX Attribution Engine!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()