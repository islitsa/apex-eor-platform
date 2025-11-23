"""
analyze_fracfocus_eor.py
FracFocus EOR Analyzer - Using Full Detailed Data
Advanced identification of EOR operations using chemical signatures and timing

This script analyzes the detailed FracFocus data to identify EOR operations using:
- Temporal patterns (time between fracs)
- Chemical signatures (CO2, polymers, surfactants)
- Purpose/Trade name keywords
- Water volume anomalies

Usage:
    python scripts/analyze_fracfocus_eor.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import re
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# EOR indicator patterns
EOR_KEYWORDS = {
    'refrac': ['refrac', 're-frac', 'refractur', 're-fractur', 'restimulat'],
    'workover': ['workover', 'work-over', 'recompletion', 're-completion'],
    'eor': ['eor', 'enhanced', 'secondary', 'tertiary', 'improved'],
    'flood': ['flood', 'waterflood', 'water flood', 'polymer flood', 'co2 flood', 'gas flood'],
    'huff_puff': ['huff', 'puff', 'huff and puff', 'huff-n-puff', 'cyclic'],
    'injection': ['injection', 'inject', 'gas injection', 'steam', 'thermal'],
    'maintenance': ['remedial', 'repair', 'clean', 'wash']
}

# EOR chemical indicators with CAS numbers
EOR_CHEMICALS = {
    'co2': {
        'names': ['carbon dioxide', 'co2', 'liquid carbon dioxide'],
        'cas': ['124-38-9', '000124-38-9']
    },
    'nitrogen': {
        'names': ['nitrogen', 'n2', 'liquid nitrogen'],
        'cas': ['7727-37-9', '007727-37-9']
    },
    'polymers': {
        'names': ['polyacrylamide', 'polymer', 'xanthan', 'guar', 'hpam', 'pam'],
        'cas': ['9003-05-8', '11138-66-2', '9000-30-0']  # PAM, xanthan, guar
    },
    'surfactants': {
        'names': ['surfactant', 'soap', 'detergent', 'alkyl', 'sulfonate', 'betaine'],
        'cas': []  # Various CAS numbers
    },
    'alkali': {
        'names': ['alkali', 'sodium hydroxide', 'caustic', 'naoh', 'sodium carbonate'],
        'cas': ['1310-73-2', '497-19-8']  # NaOH, Na2CO3
    },
    'acids': {
        'names': ['hydrochloric acid', 'hcl', 'acetic acid', 'formic acid'],
        'cas': ['7647-01-0', '64-19-7', '64-18-6']
    }
}


def load_detailed_data(file_path=None):
    """Load the detailed FracFocus data"""
    if file_path is None:
        # Try processed first, then interim
        processed_path = Path('data/processed/treatments/fracfocus_detailed.parquet')
        interim_path = Path('data/interim/fracfocus/fracfocus_cleaned.parquet')
        
        if processed_path.exists():
            file_path = processed_path
        elif interim_path.exists():
            file_path = interim_path
            logger.warning("Using interim file. Run the updated processor to get fracfocus_detailed.parquet")
        else:
            logger.error("No detailed data file found. Please run process_fracfocus_data.py first")
            return None
    
    logger.info(f"Loading detailed data from {file_path}")
    df = pd.read_parquet(file_path)
    
    # Ensure we have the right columns
    logger.info(f"Loaded {len(df):,} records with {len(df.columns)} columns")
    logger.info(f"Date range: {df.get('JobEndDate_parsed', df.get('JobEndDate', 'N/A')).min()} to {df.get('JobEndDate_parsed', df.get('JobEndDate', 'N/A')).max()}")
    
    return df


def identify_eor_chemical_signatures(df):
    """Identify EOR operations based on chemical signatures"""
    logger.info("\nAnalyzing chemical signatures for EOR indicators...")
    
    df['eor_chemical_type'] = ''
    df['eor_chemical_confidence'] = 0
    
    # Check IngredientName and CASNumber columns
    if 'IngredientName' in df.columns:
        ingredient_lower = df['IngredientName'].fillna('').astype(str).str.lower()
        
        for chem_type, indicators in EOR_CHEMICALS.items():
            # Check chemical names
            for name in indicators['names']:
                mask = ingredient_lower.str.contains(name, na=False, regex=False)
                df.loc[mask, 'eor_chemical_type'] = df.loc[mask, 'eor_chemical_type'] + f'{chem_type},'
                df.loc[mask, 'eor_chemical_confidence'] = df.loc[mask, 'eor_chemical_confidence'] + 1
    
    if 'CASNumber' in df.columns:
        cas_clean = df['CASNumber'].fillna('').astype(str).str.strip()
        
        for chem_type, indicators in EOR_CHEMICALS.items():
            for cas in indicators.get('cas', []):
                mask = cas_clean == cas
                df.loc[mask, 'eor_chemical_type'] = df.loc[mask, 'eor_chemical_type'] + f'{chem_type}_cas,'
                df.loc[mask, 'eor_chemical_confidence'] = df.loc[mask, 'eor_chemical_confidence'] + 2  # Higher confidence for CAS match
    
    # Clean up chemical type field
    df['eor_chemical_type'] = df['eor_chemical_type'].str.rstrip(',')
    
    chemicals_found = (df['eor_chemical_confidence'] > 0).sum()
    logger.info(f"  Found {chemicals_found:,} records with EOR chemical signatures")
    
    return df


def identify_eor_keywords(df):
    """Identify EOR operations based on keywords in Purpose and TradeName"""
    logger.info("\nAnalyzing text fields for EOR keywords...")
    
    df['eor_keyword_type'] = ''
    df['eor_keyword_confidence'] = 0
    
    # Check Purpose and TradeName columns
    text_columns = ['Purpose', 'TradeName', 'IngredientComment']
    
    for col in text_columns:
        if col in df.columns:
            text_lower = df[col].fillna('').astype(str).str.lower()
            
            for keyword_type, keywords in EOR_KEYWORDS.items():
                for keyword in keywords:
                    mask = text_lower.str.contains(keyword, na=False, regex=False)
                    df.loc[mask, 'eor_keyword_type'] = df.loc[mask, 'eor_keyword_type'] + f'{keyword_type},'
                    df.loc[mask, 'eor_keyword_confidence'] = df.loc[mask, 'eor_keyword_confidence'] + 1
    
    # Clean up keyword type field
    df['eor_keyword_type'] = df['eor_keyword_type'].str.rstrip(',')
    
    keywords_found = (df['eor_keyword_confidence'] > 0).sum()
    logger.info(f"  Found {keywords_found:,} records with EOR keywords")
    
    return df


def analyze_temporal_patterns(df):
    """Analyze temporal patterns to identify EOR based on refrac timing"""
    logger.info("\nAnalyzing temporal patterns...")
    
    # Determine which date column to use
    date_col = None
    if 'JobEndDate_parsed' in df.columns:
        date_col = 'JobEndDate_parsed'
    elif 'JobStartDate_parsed' in df.columns:
        date_col = 'JobStartDate_parsed'
    elif 'JobEndDate' in df.columns:
        df['JobEndDate_parsed'] = pd.to_datetime(df['JobEndDate'], errors='coerce')
        date_col = 'JobEndDate_parsed'
    else:
        logger.warning("No date column found for temporal analysis")
        return df
    
    # Determine API column
    api_col = 'API_NUMBER_CLEANED' if 'API_NUMBER_CLEANED' in df.columns else 'APINumber'
    
    # Sort by API and date
    df = df.sort_values([api_col, date_col])
    
    # For each well, identify time since first frac
    df['first_frac_date'] = df.groupby(api_col)[date_col].transform('min')
    df['days_since_first_frac'] = (df[date_col] - df['first_frac_date']).dt.days
    
    # Mark potential refrac/EOR based on time gap
    df['temporal_eor_confidence'] = 0
    df.loc[df['days_since_first_frac'] > 365, 'temporal_eor_confidence'] = 1  # >1 year
    df.loc[df['days_since_first_frac'] > 730, 'temporal_eor_confidence'] = 2  # >2 years
    df.loc[df['days_since_first_frac'] > 1825, 'temporal_eor_confidence'] = 3  # >5 years
    
    temporal_eor = (df['temporal_eor_confidence'] > 0).sum()
    logger.info(f"  Found {temporal_eor:,} records with temporal EOR patterns")
    
    return df


def calculate_eor_scores(df):
    """Calculate overall EOR confidence scores"""
    logger.info("\nCalculating EOR confidence scores...")
    
    # Combine all confidence indicators
    df['eor_total_score'] = (
        df.get('eor_chemical_confidence', 0) * 2 +  # Weight chemicals higher
        df.get('eor_keyword_confidence', 0) * 1.5 +
        df.get('temporal_eor_confidence', 0) * 1
    )
    
    # Classify based on score
    df['eor_classification'] = 'initial'
    df.loc[df['eor_total_score'] > 0, 'eor_classification'] = 'possible_eor'
    df.loc[df['eor_total_score'] > 2, 'eor_classification'] = 'probable_eor'
    df.loc[df['eor_total_score'] > 4, 'eor_classification'] = 'confirmed_eor'
    
    # Summary statistics
    classification_counts = df['eor_classification'].value_counts()
    logger.info("\nEOR Classification Results:")
    for classification, count in classification_counts.items():
        logger.info(f"  {classification}: {count:,} records ({count/len(df)*100:.1f}%)")
    
    return df


def create_well_eor_summary(df):
    """Create well-level EOR summary"""
    logger.info("\nCreating well-level EOR summary...")
    
    api_col = 'API_NUMBER_CLEANED' if 'API_NUMBER_CLEANED' in df.columns else 'APINumber'
    
    # Aggregate to well level
    well_summary = df.groupby(api_col).agg({
        'DisclosureId': 'nunique' if 'DisclosureId' in df.columns else 'count',
        'eor_classification': lambda x: 'confirmed_eor' if 'confirmed_eor' in x.values 
                                    else 'probable_eor' if 'probable_eor' in x.values
                                    else 'possible_eor' if 'possible_eor' in x.values
                                    else 'initial',
        'eor_total_score': 'max',
        'days_since_first_frac': 'max',
        'StateName': 'first' if 'StateName' in df.columns else lambda x: None,
        'CountyName': 'first' if 'CountyName' in df.columns else lambda x: None,
        'OperatorName': 'first' if 'OperatorName' in df.columns else lambda x: None
    }).reset_index()
    
    well_summary.columns = [
        'API_NUMBER', 'job_count', 'eor_status', 'max_eor_score',
        'max_days_between_fracs', 'state', 'county', 'operator'
    ]
    
    # Add binary EOR flag
    well_summary['has_eor'] = well_summary['eor_status'] != 'initial'
    
    logger.info(f"  Created summary for {len(well_summary):,} wells")
    logger.info(f"  Wells with EOR: {well_summary['has_eor'].sum():,} ({well_summary['has_eor'].sum()/len(well_summary)*100:.1f}%)")
    
    return well_summary


def save_results(df, well_summary):
    """Save analysis results"""
    output_dir = Path('data/processed/treatments')
    output_dir.mkdir(exist_ok=True, parents=True)
    
    logger.info("\nSaving results...")
    
    # Save detailed data with EOR flags
    detailed_output = output_dir / 'fracfocus_eor_detailed.parquet'
    df.to_parquet(detailed_output, index=False)
    logger.info(f"  Detailed data with EOR flags: {detailed_output}")
    
    # Save well summary
    well_output = output_dir / 'fracfocus_eor_wells.parquet'
    well_summary.to_parquet(well_output, index=False)
    logger.info(f"  Well-level EOR summary: {well_output}")
    
    # Save confirmed EOR records only
    confirmed_eor = df[df['eor_classification'].isin(['confirmed_eor', 'probable_eor'])]
    if len(confirmed_eor) > 0:
        eor_output = output_dir / 'fracfocus_confirmed_eor.parquet'
        confirmed_eor.to_parquet(eor_output, index=False)
        logger.info(f"  Confirmed EOR records: {eor_output} ({len(confirmed_eor):,} records)")
    
    # Save initial fracking only
    initial_only = df[df['eor_classification'] == 'initial']
    initial_output = output_dir / 'fracfocus_initial_only.parquet'
    initial_only.to_parquet(initial_output, index=False)
    logger.info(f"  Initial fracking only: {initial_output} ({len(initial_only):,} records)")
    
    # Generate summary statistics CSV
    stats_output = output_dir / 'fracfocus_eor_statistics.csv'
    stats = pd.DataFrame({
        'Metric': [
            'Total Records',
            'Initial Fracking',
            'Possible EOR',
            'Probable EOR',
            'Confirmed EOR',
            'Records with Chemical Indicators',
            'Records with Keyword Indicators',
            'Records with Temporal Indicators'
        ],
        'Count': [
            len(df),
            (df['eor_classification'] == 'initial').sum(),
            (df['eor_classification'] == 'possible_eor').sum(),
            (df['eor_classification'] == 'probable_eor').sum(),
            (df['eor_classification'] == 'confirmed_eor').sum(),
            (df.get('eor_chemical_confidence', 0) > 0).sum(),
            (df.get('eor_keyword_confidence', 0) > 0).sum(),
            (df.get('temporal_eor_confidence', 0) > 0).sum()
        ]
    })
    stats.to_csv(stats_output, index=False)
    logger.info(f"  Statistics saved: {stats_output}")


def main():
    """Main execution function"""
    
    print("\n" + "=" * 80)
    print("FRACFOCUS EOR ANALYZER - DETAILED ANALYSIS")
    print("=" * 80)
    
    # Load data
    df = load_detailed_data()
    if df is None:
        return
    
    # Run analyses
    df = identify_eor_chemical_signatures(df)
    df = identify_eor_keywords(df)
    df = analyze_temporal_patterns(df)
    df = calculate_eor_scores(df)
    
    # Create well summary
    well_summary = create_well_eor_summary(df)
    
    # Save results
    save_results(df, well_summary)
    
    print("\n" + "=" * 80)
    print("✓ EOR ANALYSIS COMPLETE!")
    print("=" * 80)
    
    # Print summary
    print("\nKey Findings:")
    print(f"  Total wells analyzed: {len(well_summary):,}")
    print(f"  Wells with EOR operations: {well_summary['has_eor'].sum():,}")
    print(f"  Percentage with EOR: {well_summary['has_eor'].sum()/len(well_summary)*100:.1f}%")
    
    if 'OperatorName' in df.columns:
        # Top operators by EOR
        operator_eor = df[df['eor_classification'] != 'initial'].groupby('OperatorName').size()
        top_operators = operator_eor.nlargest(5)
        print("\nTop 5 Operators by EOR Activity:")
        for op, count in top_operators.items():
            print(f"  {op}: {count:,} EOR records")


if __name__ == "__main__":
    main()