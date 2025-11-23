"""
Merge FracFocus Treatment Data with RRC Production + Formations
Creates complete attribution dataset

Usage:
    python scripts/merge_treatments_with_production.py
"""

import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_fracfocus_data(interim_dir):
    """
    Load FracFocus treatment data
    """
    logger.info("Loading FracFocus treatment data...")
    
    ff_file = interim_dir / 'fracfocus_cleaned.parquet'
    if not ff_file.exists():
        logger.error(f"FracFocus data not found at: {ff_file}")
        return None
    
    ff_df = pd.read_parquet(ff_file)
    logger.info(f"  Loaded {len(ff_df):,} treatment records")
    logger.info(f"  Unique wells: {ff_df['API_NUMBER'].nunique():,}")
    
    return ff_df


def load_production_with_formations(production_dir):
    """
    Load production data with formations
    """
    logger.info("\nLoading production data with formations...")
    
    prod_file = production_dir / 'production_with_formations.parquet'
    if not prod_file.exists():
        logger.error(f"Production+formations data not found at: {prod_file}")
        return None
    
    prod_df = pd.read_parquet(prod_file)
    logger.info(f"  Loaded {len(prod_df):,} production records")
    
    return prod_df


def load_well_completions_for_api_mapping(interim_dir):
    """
    Load well completions data to map LEASE_ID to API_NUMBER
    """
    logger.info("\nLoading well completions for API mapping...")
    
    comp_file = interim_dir / 'well_completions.parquet'
    if not comp_file.exists():
        logger.error(f"Well completions data not found at: {comp_file}")
        return None
    
    comp_df = pd.read_parquet(comp_file)
    logger.info(f"  Loaded {len(comp_df):,} completion records")
    
    # Keep only LEASE_ID and API_NUMBER mapping
    api_map = comp_df[['LEASE_ID', 'API_NUMBER']].drop_duplicates()
    logger.info(f"  Created API mapping for {len(api_map):,} unique leases")
    
    return api_map


def add_api_to_production(prod_df, api_map):
    """
    Add API numbers to production data using well completions mapping
    """
    logger.info("\nAdding API numbers to production data...")
    
    if api_map is None:
        return prod_df
    
    # Merge to add API_NUMBER
    prod_with_api = prod_df.merge(
        api_map,
        on='LEASE_ID',
        how='left'
    )
    
    api_count = prod_with_api['API_NUMBER'].notna().sum()
    pct_matched = (api_count / len(prod_with_api)) * 100
    
    logger.info(f"  Added API numbers to {api_count:,} records ({pct_matched:.1f}%)")
    
    return prod_with_api


def merge_treatments_with_production(ff_df, prod_df, api_map):
    """
    Merge FracFocus treatments with production data
    """
    logger.info("\nMerging treatments with production...")
    
    # Add API numbers to production data
    prod_df = add_api_to_production(prod_df, api_map)
    
    # Check if we have API numbers
    if 'API_NUMBER' not in prod_df.columns or prod_df['API_NUMBER'].isna().all():
        logger.error("Cannot merge - no API numbers available")
        return None
    
    # Clean API numbers for matching
    prod_df['API_NUMBER_clean'] = prod_df['API_NUMBER'].astype(str).str.strip()
    ff_df['API_NUMBER_clean'] = ff_df['API_NUMBER'].astype(str).str.strip()
    
    # Merge on API number
    logger.info("  Merging on API_NUMBER...")
    
    merged = prod_df.merge(
        ff_df,
        on='API_NUMBER_clean',
        how='left',
        suffixes=('', '_ff')
    )
    
    logger.info(f"  Merged records: {len(merged):,}")
    
    # Count matches
    with_treatments = merged['JobEndDate_parsed'].notna().sum()
    pct_matched = (with_treatments / len(merged)) * 100
    logger.info(f"  Records with treatment data: {with_treatments:,} ({pct_matched:.1f}%)")
    
    return merged


def create_attribution_dataset(merged_df):
    """
    Create final attribution dataset with key metrics
    """
    logger.info("\nCreating attribution dataset...")
    
    # Select key columns for attribution
    attribution_cols = [
        # Identifiers
        'LEASE_ID', 'API_NUMBER_clean',
        
        # Production
        'PRODUCTION_DATE', 'LEASE_OIL_PROD_VOL', 'LEASE_GAS_PROD_VOL',
        'OPERATOR_NAME', 'FIELD_NAME',
        
        # Formations
        'formation_name', 'formation_top_depth',
        
        # Treatment
        'JobEndDate_parsed', 'TotalBaseWaterVolume', 
        'TVD', 'TotalDepth'
    ]
    
    # Include only columns that exist
    available_cols = [col for col in attribution_cols if col in merged_df.columns]
    
    attribution_df = merged_df[available_cols].copy()
    
    logger.info(f"  Attribution dataset: {len(attribution_df):,} records")
    logger.info(f"  Columns: {len(available_cols)}")
    
    return attribution_df


def analyze_attribution_potential(merged_df):
    """
    Analyze the attribution dataset potential
    """
    logger.info("\n" + "="*70)
    logger.info("ATTRIBUTION ANALYSIS")
    logger.info("="*70)
    
    # Wells with complete data
    has_production = merged_df['LEASE_OIL_PROD_VOL'].notna().sum()
    has_formation = merged_df['formation_name'].notna().sum()
    has_treatment = merged_df['JobEndDate_parsed'].notna().sum()
    
    logger.info(f"\nData Completeness:")
    logger.info(f"  Records with production: {has_production:,}")
    logger.info(f"  Records with formation: {has_formation:,}")
    logger.info(f"  Records with treatment: {has_treatment:,}")
    
    # Complete records (all three)
    complete = merged_df[
        merged_df['LEASE_OIL_PROD_VOL'].notna() &
        merged_df['formation_name'].notna() &
        merged_df['JobEndDate_parsed'].notna()
    ]
    
    logger.info(f"\n  COMPLETE records (production + formation + treatment): {len(complete):,}")
    
    if len(complete) > 0:
        logger.info(f"\nTop formations in complete dataset:")
        top_formations = complete['formation_name'].value_counts().head(10)
        for formation, count in top_formations.items():
            logger.info(f"  {formation}: {count:,} records")
    
    return complete


def main():
    # Define paths
    project_root = Path.cwd()
    ff_interim_dir = project_root / 'data' / 'interim' / 'fracfocus'
    rrc_interim_dir = project_root / 'data' / 'interim' / 'rrc'
    production_dir = project_root / 'data' / 'processed' / 'production'
    output_dir = project_root / 'data' / 'processed' / 'attribution'
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("="*70)
    logger.info("MERGING TREATMENTS WITH PRODUCTION + FORMATIONS")
    logger.info("="*70)
    
    # Step 1: Load well completions for API mapping
    api_map = load_well_completions_for_api_mapping(rrc_interim_dir)
    if api_map is None:
        logger.error("Cannot proceed without API mapping")
        return
    
    # Step 2: Load FracFocus data
    ff_df = load_fracfocus_data(ff_interim_dir)
    if ff_df is None:
        return
    
    # Step 3: Load production with formations
    prod_df = load_production_with_formations(production_dir)
    if prod_df is None:
        return
    
    # Step 4: Merge
    merged_df = merge_treatments_with_production(ff_df, prod_df, api_map)
    if merged_df is None:
        return
    
    # Step 5: Create attribution dataset
    attribution_df = create_attribution_dataset(merged_df)
    
    # Step 6: Analyze
    complete_df = analyze_attribution_potential(merged_df)
    
    # Step 7: Save results
    logger.info("\n" + "="*70)
    logger.info("SAVING RESULTS")
    logger.info("="*70)
    
    # Save full merged dataset
    full_output = output_dir / 'production_formations_treatments_merged.parquet'
    logger.info(f"\nSaving full merged dataset...")
    merged_df.to_parquet(full_output, index=False)
    logger.info(f"✓ Saved to {full_output}")
    logger.info(f"  Records: {len(merged_df):,}")
    
    # Save attribution-ready dataset
    attr_output = output_dir / 'attribution_dataset.parquet'
    logger.info(f"\nSaving attribution dataset...")
    attribution_df.to_parquet(attr_output, index=False)
    logger.info(f"✓ Saved to {attr_output}")
    logger.info(f"  Records: {len(attribution_df):,}")
    
    # Save complete records only
    if len(complete_df) > 0:
        complete_output = output_dir / 'complete_attribution_records.parquet'
        logger.info(f"\nSaving complete records (prod + formation + treatment)...")
        complete_df.to_parquet(complete_output, index=False)
        logger.info(f"✓ Saved to {complete_output}")
        logger.info(f"  Records: {len(complete_df):,}")
    
    logger.info("\n" + "="*70)
    logger.info("✓ MERGE COMPLETE!")
    logger.info("="*70)
    logger.info(f"\nOutput files in: {output_dir}")
    logger.info(f"\n✓ Ready for APEX Attribution Engine!")


if __name__ == "__main__":
    main()