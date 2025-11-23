"""
Merge RRC Production Data with W-2 Formation Data
Links production volumes to landing zones/formations

Usage:
    python scripts/merge_production_with_formations.py
"""

import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_and_prepare_packet_data(interim_dir):
    """
    Load PACKET data and extract key identifiers
    """
    logger.info("Loading PACKET data...")
    
    packet = pd.read_parquet(interim_dir / 'PACKET.parquet')
    logger.info(f"  Loaded {len(packet):,} packet records")
    
    # Extract key fields
    packet_clean = pd.DataFrame({
        'tracking_no': packet['field_1'].astype(str),
        'lease_no': packet['field_6'].astype(str),
        'district': packet['field_27'].astype(str),
        'field_name': packet['field_29'],
        'operator_no': packet['field_5'],
        'lease_name': packet['field_26'],
        'source_date': packet['source_date'],
        'district_folder': packet['district']
    })
    
    # Create LEASE_ID to match production data
    packet_clean['LEASE_ID'] = (
        packet_clean['lease_no'].str.zfill(6) + 
        packet_clean['district'].str.strip().str.zfill(2)
    )
    
    # Remove records without valid lease numbers
    packet_clean = packet_clean[packet_clean['lease_no'].str.strip() != '']
    
    logger.info(f"  Created {len(packet_clean):,} clean packet records with LEASE_ID")
    
    return packet_clean


def load_and_prepare_formation_data(interim_dir):
    """
    Load W-2 Formation Data and extract formation names
    """
    logger.info("Loading W-2 Formation Data...")
    
    formations = pd.read_parquet(interim_dir / 'W-2_Formation_Data.parquet')
    logger.info(f"  Loaded {len(formations):,} formation records")
    
    # Extract key fields
    formations_clean = pd.DataFrame({
        'tracking_no': formations['field_1'].astype(str),
        'completion_id': formations['field_3'],
        'formation_seq': formations['field_4'],
        'formation_name': formations['field_5'],
        'formation_top_depth': formations['field_6'],
        'is_productive': formations['field_8']
    })
    
    # Keep only productive formations or filter as needed
    # Uncomment next line to filter only productive formations:
    # formations_clean = formations_clean[formations_clean['is_productive'] == 'Y']
    
    logger.info(f"  Prepared {len(formations_clean):,} formation records")
    
    # Show top formations
    top_formations = formations_clean['formation_name'].value_counts().head(10)
    logger.info(f"\nTop formations in completion data:")
    for formation, count in top_formations.items():
        logger.info(f"  {formation}: {count:,}")
    
    return formations_clean


def merge_packet_and_formations(packet_data, formation_data):
    """
    Merge PACKET with Formation data on tracking number
    """
    logger.info("\nMerging PACKET with Formation data...")
    
    merged = packet_data.merge(
        formation_data,
        on='tracking_no',
        how='left'
    )
    
    logger.info(f"  Merged records: {len(merged):,}")
    logger.info(f"  Unique wells (LEASE_ID): {merged['LEASE_ID'].nunique():,}")
    
    return merged


def merge_with_production(packet_formations, production_file):
    """
    Merge packet/formation data with production data
    """
    logger.info("\nLoading production data...")
    
    if not production_file.exists():
        logger.error(f"Production data not found at: {production_file}")
        return None
    
    production = pd.read_parquet(production_file)
    logger.info(f"  Loaded {len(production):,} production records")
    
    # Check if LEASE_ID exists in production data
    if 'LEASE_ID' not in production.columns:
        logger.info("  Creating LEASE_ID in production data...")
        production['LEASE_ID'] = (
            production['LEASE_NO'].astype(str).str.zfill(6) + 
            production['DISTRICT_NO'].astype(str).str.zfill(2)
        )
    
    logger.info("\nMerging production with formation data...")
    logger.info("  This may take several minutes for large datasets...")
    
    # Merge production with packet/formation data
    final = production.merge(
        packet_formations,
        on='LEASE_ID',
        how='left',
        suffixes=('', '_completion')
    )
    
    logger.info(f"  Final merged records: {len(final):,}")
    
    # Count records with formation data
    with_formations = final['formation_name'].notna().sum()
    pct_matched = (with_formations / len(final)) * 100
    logger.info(f"  Records with formation data: {with_formations:,} ({pct_matched:.1f}%)")
    
    return final


def analyze_results(merged_data):
    """
    Analyze the merged dataset
    """
    logger.info("\n" + "="*70)
    logger.info("ANALYSIS OF MERGED DATASET")
    logger.info("="*70)
    
    # Production by formation
    if 'formation_name' in merged_data.columns:
        prod_by_formation = merged_data.groupby('formation_name').agg({
            'LEASE_OIL_PROD_VOL': 'sum',
            'LEASE_GAS_PROD_VOL': 'sum',
            'LEASE_ID': 'nunique'
        }).sort_values('LEASE_OIL_PROD_VOL', ascending=False)
        
        logger.info("\nTop 10 Formations by Oil Production:")
        for idx, (formation, row) in enumerate(prod_by_formation.head(10).iterrows(), 1):
            logger.info(f"  {idx}. {formation}")
            logger.info(f"     Oil: {row['LEASE_OIL_PROD_VOL']:,.0f} BBL")
            logger.info(f"     Gas: {row['LEASE_GAS_PROD_VOL']:,.0f} MCF")
            logger.info(f"     Wells: {row['LEASE_ID']}")
    
    # Date range
    if 'PRODUCTION_DATE' in merged_data.columns:
        logger.info(f"\nProduction Date Range:")
        logger.info(f"  Start: {merged_data['PRODUCTION_DATE'].min()}")
        logger.info(f"  End: {merged_data['PRODUCTION_DATE'].max()}")
    
    # Column list
    logger.info(f"\nAvailable columns ({len(merged_data.columns)}):")
    logger.info(f"  {', '.join(merged_data.columns.tolist()[:15])}...")


def main():
    # Define paths
    project_root = Path.cwd()
    interim_dir = project_root / 'data' / 'interim' / 'rrc'
    
    # Organize outputs by type
    production_dir = project_root / 'data' / 'processed' / 'production'
    completions_dir = project_root / 'data' / 'processed' / 'completions'
    
    production_dir.mkdir(parents=True, exist_ok=True)
    completions_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("="*70)
    logger.info("MERGING PRODUCTION DATA WITH FORMATION/LANDING ZONE DATA")
    logger.info("="*70)
    
    # Step 1: Load and prepare packet data
    packet_data = load_and_prepare_packet_data(interim_dir)
    
    # Step 2: Load and prepare formation data
    formation_data = load_and_prepare_formation_data(interim_dir)
    
    # Step 3: Merge packet with formations
    packet_formations = merge_packet_and_formations(packet_data, formation_data)
    
    # Step 4: Merge with production data
    production_file = interim_dir / 'shale_production.parquet'
    
    if not production_file.exists():
        logger.warning(f"Shale production file not found, trying full production...")
        production_file = interim_dir / 'production_monthly.parquet'
    
    final_data = merge_with_production(packet_formations, production_file)
    
    if final_data is None:
        logger.error("Merge failed - production data not found")
        return
    
    # Step 5: Analyze results
    analyze_results(final_data)
    
    # Step 6: Save final dataset
    logger.info("\n" + "="*70)
    logger.info("SAVING RESULTS")
    logger.info("="*70)
    
    # Save main production dataset with formations
    output_file = production_dir / 'production_with_formations.parquet'
    logger.info(f"\nSaving to: {output_file}")
    final_data.to_parquet(output_file, index=False)
    logger.info(f"✓ Saved {len(final_data):,} records")
    
    # Save summary by formation
    if 'formation_name' in final_data.columns:
        summary = final_data.groupby('formation_name').agg({
            'LEASE_OIL_PROD_VOL': 'sum',
            'LEASE_GAS_PROD_VOL': 'sum',
            'LEASE_ID': 'nunique',
            'PRODUCTION_DATE': ['min', 'max']
        }).reset_index()
        
        summary.columns = ['formation_name', 'total_oil_bbl', 'total_gas_mcf', 
                          'unique_leases', 'first_prod_date', 'last_prod_date']
        
        summary_file = production_dir / 'summary_by_formation.parquet'
        summary.to_parquet(summary_file, index=False)
        logger.info(f"✓ Saved formation summary: {summary_file}")
    
    # Save completion-focused dataset (one row per well with formations)
    if 'LEASE_ID' in final_data.columns:
        well_completions = final_data.groupby('LEASE_ID').agg({
            'formation_name': lambda x: ', '.join(x.dropna().unique()),
            'lease_name': 'first',
            'field_name': 'first',
            'OPERATOR_NAME': 'first' if 'OPERATOR_NAME' in final_data.columns else lambda x: None,
            'source_date': 'first',
            'LEASE_OIL_PROD_VOL': 'sum',
            'LEASE_GAS_PROD_VOL': 'sum',
        }).reset_index()
        
        well_completions.columns = ['lease_id', 'formations', 'lease_name', 'field_name', 
                                     'operator', 'completion_date', 'cumulative_oil_bbl', 'cumulative_gas_mcf']
        
        completions_file = completions_dir / 'wells_with_formations.parquet'
        well_completions.to_parquet(completions_file, index=False)
        logger.info(f"✓ Saved well completions: {completions_file}")
    
    logger.info("\n" + "="*70)
    logger.info("✓ MERGE COMPLETE!")
    logger.info("="*70)
    logger.info(f"\nOutput files:")
    logger.info(f"  Production data:")
    logger.info(f"    - {output_file}")
    logger.info(f"    - {summary_file}")
    logger.info(f"  Completion data:")
    logger.info(f"    - {completions_file}")
    logger.info(f"\nYou can now analyze production by landing zone/formation!")


if __name__ == "__main__":
    main()