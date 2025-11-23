"""
FracFocus Data Processor - FIXED VERSION
Processes hydraulic fracturing treatment data while preserving ALL details

Key Changes:
- Saves detailed cleaned data to processed folder (fracfocus_detailed.parquet)
- Well summary is created as a separate supplementary file
- No data loss - all columns and records preserved

Reads from: OneDrive FracFocus CSVs
Outputs to: data/interim/fracfocus/ and data/processed/treatments/

Usage:
    python scripts/process_fracfocus_data.py
"""

import pandas as pd
from pathlib import Path
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FracFocusProcessor:
    """
    Process FracFocus treatment data for APEX Attribution Engine
    """
    
    def __init__(self, 
                 source_dir,
                 interim_dir='./data/interim/fracfocus',
                 processed_dir='./data/processed/treatments'):
        
        self.source_dir = Path(source_dir)
        self.interim_dir = Path(interim_dir)
        self.processed_dir = Path(processed_dir)
        
        # Create directories
        self.interim_dir.mkdir(exist_ok=True, parents=True)
        self.processed_dir.mkdir(exist_ok=True, parents=True)
        
        logger.info(f"Source: {self.source_dir}")
        logger.info(f"Interim: {self.interim_dir}")
        logger.info(f"Processed: {self.processed_dir}")
    
    def process_registry_files(self):
        """
        Process all FracFocusRegistry CSV files and combine them
        
        These contain the main treatment data with API numbers, dates, 
        proppant, fluids, chemicals, etc.
        """
        logger.info("Processing FracFocus Registry files...")
        
        # Find all registry files
        registry_files = sorted(self.source_dir.glob("FracFocusRegistry_*.csv"))
        
        if not registry_files:
            logger.error(f"No FracFocusRegistry files found in {self.source_dir}")
            return None
        
        logger.info(f"Found {len(registry_files)} registry files")
        
        # Read and combine all files
        chunks = []
        
        for idx, file in enumerate(registry_files, 1):
            logger.info(f"  Reading {file.name} ({idx}/{len(registry_files)})...")
            
            try:
                df = pd.read_csv(file, low_memory=False, encoding='utf-8-sig')
                chunks.append(df)
                logger.info(f"    Loaded {len(df):,} records")
            except Exception as e:
                logger.error(f"    Error reading {file.name}: {e}")
        
        if not chunks:
            logger.error("No data loaded from registry files")
            return None
        
        # Combine all chunks
        logger.info("\nCombining all registry files...")
        registry_df = pd.concat(chunks, ignore_index=True)
        logger.info(f"✓ Total records: {len(registry_df):,}")
        
        # Show columns - ALL of them are preserved!
        logger.info(f"\nTotal columns preserved: {len(registry_df.columns)}")
        logger.info(f"Columns: {registry_df.columns.tolist()}")
        
        # Fix data types before saving to parquet
        logger.info("\nFixing data types for parquet compatibility...")
        
        # Ensure string columns are actually strings (prevent mixed types)
        string_cols = ['APINumber', 'DisclosureId', 'StateName', 'CountyName', 
                      'OperatorName', 'WellName', 'TradeName', 'Supplier', 
                      'Purpose', 'CASNumber', 'IngredientName', 'IngredientCommonName',
                      'IngredientComment', 'IngredientMSDS', 'ClaimantCompany',
                      'Projection', 'FFVersion', 'PurposeId', 'IngredientsId']
        
        for col in string_cols:
            if col in registry_df.columns:
                registry_df[col] = registry_df[col].astype(str).replace('nan', '')
        
        # Ensure numeric columns are numeric
        numeric_cols = ['TVD', 'TotalBaseWaterVolume', 'TotalBaseNonWaterVolume',
                       'Latitude', 'Longitude', 'PercentHighAdditive', 
                       'PercentHFJob', 'MassIngredient']
        
        for col in numeric_cols:
            if col in registry_df.columns:
                registry_df[col] = pd.to_numeric(registry_df[col], errors='coerce')
        
        # Parse date columns
        date_cols = ['JobStartDate', 'JobEndDate']
        for col in date_cols:
            if col in registry_df.columns:
                registry_df[f'{col}_parsed'] = pd.to_datetime(registry_df[col], errors='coerce')
        
        # Save combined interim file with ALL data
        output_file = self.interim_dir / 'fracfocus_registry_combined.parquet'
        registry_df.to_parquet(output_file, index=False)
        logger.info(f"\n✓ Saved ALL {len(registry_df):,} records with {len(registry_df.columns)} columns to {output_file}")
        
        return registry_df
    
    def clean_and_process(self, registry_df=None):
        """
        Clean and process FracFocus data while preserving ALL records and columns
        """
        if registry_df is None:
            interim_file = self.interim_dir / 'fracfocus_registry_combined.parquet'
            if not interim_file.exists():
                logger.error("Registry data not processed yet")
                return None
            registry_df = pd.read_parquet(interim_file)
        
        logger.info("\nCleaning and processing FracFocus data...")
        logger.info(f"Starting with {len(registry_df):,} records and {len(registry_df.columns)} columns")
        
        # Create a copy to preserve original
        cleaned_df = registry_df.copy()
        
        # Clean API numbers (add cleaned version, keep original)
        if 'APINumber' in cleaned_df.columns:
            cleaned_df['API_NUMBER_CLEANED'] = cleaned_df['APINumber'].astype(str).str.strip()
            # Remove dashes and format
            cleaned_df['API_NUMBER_CLEANED'] = cleaned_df['API_NUMBER_CLEANED'].str.replace('-', '')
            
            # For Texas-specific analysis, create a flag instead of filtering
            cleaned_df['is_texas'] = cleaned_df['API_NUMBER_CLEANED'].str.startswith('42')
            logger.info(f"  Texas wells: {cleaned_df['is_texas'].sum():,} records")
            logger.info(f"  Non-Texas wells: {(~cleaned_df['is_texas']).sum():,} records")
        
        # Add analysis columns without removing data
        if 'JobEndDate_parsed' in cleaned_df.columns:
            # Add temporal analysis columns
            cleaned_df['year'] = cleaned_df['JobEndDate_parsed'].dt.year
            cleaned_df['month'] = cleaned_df['JobEndDate_parsed'].dt.month
            cleaned_df['quarter'] = cleaned_df['JobEndDate_parsed'].dt.quarter
        
        # Add EOR indicator columns (preliminary, based on keywords)
        cleaned_df['potential_eor'] = False
        
        # Check Purpose field for EOR keywords
        if 'Purpose' in cleaned_df.columns:
            eor_keywords = ['refrac', 're-frac', 'restim', 'workover', 'eor', 
                          'enhance', 'secondary', 'tertiary', 'flood']
            for keyword in eor_keywords:
                mask = cleaned_df['Purpose'].astype(str).str.lower().str.contains(keyword, na=False)
                cleaned_df.loc[mask, 'potential_eor'] = True
        
        # Check chemicals for EOR indicators
        if 'IngredientName' in cleaned_df.columns:
            eor_chemicals = ['carbon dioxide', 'co2', 'nitrogen', 'polymer', 
                           'surfactant', 'alkali', 'steam']
            for chemical in eor_chemicals:
                mask = cleaned_df['IngredientName'].astype(str).str.lower().str.contains(chemical, na=False)
                cleaned_df.loc[mask, 'potential_eor'] = True
        
        logger.info(f"✓ Cleaned data: {len(cleaned_df):,} records with {len(cleaned_df.columns)} columns")
        logger.info(f"  Potential EOR records flagged: {cleaned_df['potential_eor'].sum():,}")
        
        # Save cleaned data with ALL records to both interim and processed
        interim_output = self.interim_dir / 'fracfocus_cleaned.parquet'
        cleaned_df.to_parquet(interim_output, index=False)
        logger.info(f"✓ Saved to interim: {interim_output}")
        
        # IMPORTANT: Save detailed data to processed folder
        processed_detailed = self.processed_dir / 'fracfocus_detailed.parquet'
        cleaned_df.to_parquet(processed_detailed, index=False)
        logger.info(f"✓ Saved DETAILED data to processed: {processed_detailed}")
        
        return cleaned_df
    
    def create_supplementary_files(self, cleaned_df=None):
        """
        Create supplementary analysis files WITHOUT losing the detailed data
        These are IN ADDITION to the detailed file, not replacements
        """
        if cleaned_df is None:
            detailed_file = self.processed_dir / 'fracfocus_detailed.parquet'
            if not detailed_file.exists():
                logger.error("Detailed data not found")
                return None
            cleaned_df = pd.read_parquet(detailed_file)
        
        logger.info("\nCreating supplementary analysis files...")
        
        # 1. Well-level summary (aggregated) - SUPPLEMENTARY FILE
        logger.info("Creating well summary...")
        api_col = 'API_NUMBER_CLEANED' if 'API_NUMBER_CLEANED' in cleaned_df.columns else 'APINumber'
        
        agg_dict = {}
        
        # Add string columns (first occurrence)
        for col in ['OperatorName', 'WellName', 'StateName', 'CountyName', 'Latitude', 'Longitude']:
            if col in cleaned_df.columns:
                agg_dict[col] = 'first'
        
        # Add numeric aggregations
        if 'TotalBaseWaterVolume' in cleaned_df.columns:
            agg_dict['TotalBaseWaterVolume'] = ['sum', 'mean', 'max']
        
        if 'JobEndDate_parsed' in cleaned_df.columns:
            agg_dict['JobEndDate_parsed'] = ['min', 'max', 'count']
        
        if 'potential_eor' in cleaned_df.columns:
            agg_dict['potential_eor'] = 'any'  # True if any record for well has potential_eor
        
        # Count unique disclosures (jobs)
        if 'DisclosureId' in cleaned_df.columns:
            agg_dict['DisclosureId'] = 'nunique'
        
        well_summary = cleaned_df.groupby(api_col).agg(agg_dict).reset_index()
        
        # Flatten column names
        well_summary.columns = ['_'.join(col).strip('_') if col[1] else col[0] 
                                for col in well_summary.columns.values]
        
        # Rename for clarity
        rename_map = {
            'JobEndDate_parsed_min': 'first_job_date',
            'JobEndDate_parsed_max': 'last_job_date', 
            'JobEndDate_parsed_count': 'record_count',
            'DisclosureId_nunique': 'job_count',
            'TotalBaseWaterVolume_sum': 'total_water_volume',
            'TotalBaseWaterVolume_mean': 'avg_water_volume',
            'TotalBaseWaterVolume_max': 'max_water_volume',
            'potential_eor_any': 'has_potential_eor'
        }
        
        well_summary = well_summary.rename(columns={k: v for k, v in rename_map.items() if k in well_summary.columns})
        
        # Add time-based analysis
        if 'first_job_date' in well_summary.columns and 'last_job_date' in well_summary.columns:
            well_summary['days_between_jobs'] = (well_summary['last_job_date'] - well_summary['first_job_date']).dt.days
            well_summary['multiple_fracs'] = well_summary['job_count'] > 1
        
        # Save well summary as SUPPLEMENTARY file
        summary_output = self.processed_dir / 'fracfocus_well_summary.parquet'
        well_summary.to_parquet(summary_output, index=False)
        logger.info(f"✓ Well summary saved: {summary_output} ({len(well_summary):,} wells)")
        
        # 2. Create job-level summary (one row per disclosure/job) - SUPPLEMENTARY FILE
        logger.info("Creating job summary...")
        if 'DisclosureId' in cleaned_df.columns:
            job_cols = [api_col, 'DisclosureId', 'OperatorName', 'WellName', 
                       'StateName', 'CountyName', 'JobStartDate_parsed', 
                       'JobEndDate_parsed', 'TotalBaseWaterVolume', 
                       'TotalBaseNonWaterVolume', 'potential_eor']
            
            job_cols = [col for col in job_cols if col in cleaned_df.columns]
            
            job_summary = cleaned_df[job_cols].drop_duplicates(subset=['DisclosureId'])
            job_output = self.processed_dir / 'fracfocus_job_summary.parquet'
            job_summary.to_parquet(job_output, index=False)
            logger.info(f"✓ Job summary saved: {job_output} ({len(job_summary):,} jobs)")
        
        return well_summary
    
    def analyze_results(self, cleaned_df, well_summary):
        """
        Analyze FracFocus data
        """
        logger.info("\n" + "="*70)
        logger.info("FRACFOCUS DATA ANALYSIS")
        logger.info("="*70)
        
        logger.info(f"\nDETAILED DATA PRESERVED:")
        logger.info(f"  Total records: {len(cleaned_df):,}")
        logger.info(f"  Total columns: {len(cleaned_df.columns)}")
        logger.info(f"  File: data/processed/treatments/fracfocus_detailed.parquet")
        
        logger.info(f"\nSUPPLEMENTARY FILES CREATED:")
        logger.info(f"  Well summary: {len(well_summary):,} unique wells")
        logger.info(f"  Job summary: saved separately")
        
        # Check for potential EOR
        if 'potential_eor' in cleaned_df.columns:
            eor_records = cleaned_df['potential_eor'].sum()
            logger.info(f"\nEOR INDICATORS:")
            logger.info(f"  Records with EOR keywords: {eor_records:,} ({eor_records/len(cleaned_df)*100:.1f}%)")
        
        # Date range
        if 'JobEndDate_parsed' in cleaned_df.columns:
            logger.info(f"\nTEMPORAL RANGE:")
            logger.info(f"  First job: {cleaned_df['JobEndDate_parsed'].min()}")
            logger.info(f"  Last job: {cleaned_df['JobEndDate_parsed'].max()}")
            
            # Jobs by year
            if 'year' in cleaned_df.columns:
                yearly = cleaned_df.groupby('year').size()
                logger.info(f"\n  Jobs by year:")
                for year, count in yearly.items():
                    if pd.notna(year):
                        logger.info(f"    {int(year)}: {count:,} records")
        
        # Chemical diversity
        if 'IngredientName' in cleaned_df.columns:
            unique_chemicals = cleaned_df['IngredientName'].nunique()
            logger.info(f"\nCHEMICAL DATA:")
            logger.info(f"  Unique ingredients: {unique_chemicals:,}")
            
            # Top chemicals
            top_chemicals = cleaned_df['IngredientName'].value_counts().head(10)
            logger.info(f"  Top 10 chemicals:")
            for chem, count in top_chemicals.items():
                logger.info(f"    {str(chem)[:40]}: {count:,} occurrences")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Process FracFocus CSV data while preserving ALL details'
    )
    parser.add_argument(
        '--source-dir',
        default='./data/raw/fracfocus',
        help='Path to FracFocus CSV files'
    )
    parser.add_argument(
        '--interim-dir',
        default='./data/interim/fracfocus',
        help='Interim data directory'
    )
    parser.add_argument(
        '--processed-dir',
        default='./data/processed/treatments',
        help='Processed data directory'
    )
    
    args = parser.parse_args()
    
    # Initialize processor
    processor = FracFocusProcessor(
        source_dir=args.source_dir,
        interim_dir=args.interim_dir,
        processed_dir=args.processed_dir
    )
    
    print("\n" + "=" * 80)
    print("FRACFOCUS DATA PROCESSING PIPELINE - DETAIL PRESERVING VERSION")
    print("=" * 80)
    
    # Step 1: Process registry files
    print("\n[1/3] Processing FracFocus Registry files...")
    registry_df = processor.process_registry_files()
    
    if registry_df is None:
        print("❌ Failed to process registry files")
        return
    
    # Step 2: Clean and process - SAVES DETAILED DATA
    print("\n[2/3] Cleaning and processing (preserving all details)...")
    cleaned_df = processor.clean_and_process(registry_df)
    
    if cleaned_df is None:
        print("❌ Failed to clean data")
        return
    
    # Step 3: Create supplementary files (summaries)
    print("\n[3/3] Creating supplementary summary files...")
    well_summary = processor.create_supplementary_files(cleaned_df)
    
    # Analysis
    processor.analyze_results(cleaned_df, well_summary)
    
    print("\n" + "=" * 80)
    print("✓ PROCESSING COMPLETE - ALL DETAILS PRESERVED!")
    print("=" * 80)
    print(f"\nOutput files:")
    print(f"  DETAILED DATA: {processor.processed_dir}/fracfocus_detailed.parquet")
    print(f"  Well Summary: {processor.processed_dir}/fracfocus_well_summary.parquet")
    print(f"  Job Summary: {processor.processed_dir}/fracfocus_job_summary.parquet")
    print(f"\n✓ Ready for EOR analysis with full chemical and job details!")


if __name__ == "__main__":
    main()