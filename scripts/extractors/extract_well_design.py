"""
Extract Well Design Metrics from W-2 and FracFocus Data
Creates comprehensive well design dataset for attribution

Usage:
    python scripts/extract_well_design.py
"""

import pandas as pd
from pathlib import Path
import logging
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WellDesignExtractor:
    """
    Extract and process well design metrics
    """
    
    def __init__(self, interim_dir, processed_dir):
        self.interim_dir = Path(interim_dir)
        self.processed_dir = Path(processed_dir)
        
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_casing_design(self):
        """
        Extract casing design from W-2 Casing Data
        """
        logger.info("Extracting casing design from W-2 data...")
        
        casing_file = self.interim_dir / 'W-2_Casing_Data.parquet'
        if not casing_file.exists():
            logger.warning(f"Casing data not found: {casing_file}")
            return None
        
        casing_df = pd.read_parquet(casing_file)
        logger.info(f"  Loaded {len(casing_df):,} casing records")
        
        # Parse casing data
        # Typical W-2 casing fields: tracking_no, size, weight, depth, hole_size, cement_top
        casing_clean = pd.DataFrame({
            'tracking_no': casing_df['field_1'].astype(str),
            'casing_sequence': casing_df['field_4'],
            'casing_size': casing_df['field_5'],  # e.g., "13 3/8", "9 5/8", "7"
            'casing_weight': casing_df['field_6'],
            'casing_depth': pd.to_numeric(casing_df['field_7'], errors='coerce'),
            'hole_size': casing_df['field_9'],
            'casing_type': casing_df['field_8'],  # Surface, Intermediate, Production
        })
        
        # Pivot to get casing strings per well
        casing_summary = casing_clean.groupby('tracking_no').agg({
            'casing_size': lambda x: ', '.join(x.dropna().astype(str).unique()),
            'casing_depth': 'max',  # Deepest casing (likely production casing)
            'casing_sequence': 'count'  # Number of casing strings
        }).reset_index()
        
        casing_summary.columns = ['tracking_no', 'casing_sizes', 'max_casing_depth', 'num_casing_strings']
        
        logger.info(f"  Processed {len(casing_summary):,} wells with casing data")
        
        return casing_summary
    
    def extract_tubing_design(self):
        """
        Extract tubing design from W-2 Tubing Data
        """
        logger.info("\nExtracting tubing design from W-2 data...")
        
        tubing_file = self.interim_dir / 'W-2_Tubing_Data.parquet'
        if not tubing_file.exists():
            logger.warning(f"Tubing data not found: {tubing_file}")
            return None
        
        tubing_df = pd.read_parquet(tubing_file)
        logger.info(f"  Loaded {len(tubing_df):,} tubing records")
        
        # Parse tubing data
        tubing_clean = pd.DataFrame({
            'tracking_no': tubing_df['field_1'].astype(str),
            'tubing_size': tubing_df['field_4'],  # e.g., "2 3/8", "2 7/8"
            'tubing_depth': pd.to_numeric(tubing_df['field_5'], errors='coerce'),
        })
        
        # Get primary tubing per well
        tubing_summary = tubing_clean.groupby('tracking_no').agg({
            'tubing_size': 'first',
            'tubing_depth': 'max'
        }).reset_index()
        
        logger.info(f"  Processed {len(tubing_summary):,} wells with tubing data")
        
        return tubing_summary
    
    def extract_liner_design(self):
        """
        Extract liner design from W-2 Liner Data
        """
        logger.info("\nExtracting liner design from W-2 data...")
        
        liner_file = self.interim_dir / 'W-2_Liner_Data.parquet'
        if not liner_file.exists():
            logger.warning(f"Liner data not found: {liner_file}")
            return None
        
        liner_df = pd.read_parquet(liner_file)
        logger.info(f"  Loaded {len(liner_df):,} liner records")
        
        # Parse liner data
        liner_clean = pd.DataFrame({
            'tracking_no': liner_df['field_1'].astype(str),
            'liner_size': liner_df['field_4'],
            'liner_top_depth': pd.to_numeric(liner_df['field_5'], errors='coerce'),
            'liner_bottom_depth': pd.to_numeric(liner_df['field_6'], errors='coerce'),
        })
        
        # Get liner info per well
        liner_summary = liner_clean.groupby('tracking_no').agg({
            'liner_size': 'first',
            'liner_top_depth': 'min',
            'liner_bottom_depth': 'max'
        }).reset_index()
        
        # Calculate liner length
        liner_summary['liner_length'] = (
            liner_summary['liner_bottom_depth'] - liner_summary['liner_top_depth']
        )
        
        logger.info(f"  Processed {len(liner_summary):,} wells with liner data")
        
        return liner_summary
    
    def extract_completion_design(self):
        """
        Extract completion design from FracFocus data
        """
        logger.info("\nExtracting completion design from FracFocus...")
        
        ff_file = self.interim_dir.parent / 'fracfocus' / 'fracfocus_cleaned.parquet'
        if not ff_file.exists():
            logger.warning(f"FracFocus data not found: {ff_file}")
            return None
        
        ff_df = pd.read_parquet(ff_file)
        logger.info(f"  Loaded {len(ff_df):,} FracFocus records")
        
        # Calculate completion metrics per well
        completion_summary = ff_df.groupby('API_NUMBER').agg({
            'TotalBaseWaterVolume': 'sum',
            'TotalBaseNonWaterVolume': 'sum',
            'TVD': 'first',
            'TotalDepth': 'first' if 'TotalDepth' in ff_df.columns else lambda x: None,
            'JobEndDate_parsed': ['min', 'max', 'count']
        }).reset_index()
        
        # Flatten column names
        completion_summary.columns = ['_'.join(col).strip('_') if col[1] else col[0] 
                                      for col in completion_summary.columns.values]
        
        # Calculate lateral length (for horizontal wells)
        if 'TotalDepth_first' in completion_summary.columns:
            completion_summary['lateral_length'] = (
                completion_summary['TotalDepth_first'] - completion_summary['TVD_first']
            )
            # Set to 0 if negative (vertical wells)
            completion_summary['lateral_length'] = completion_summary['lateral_length'].clip(lower=0)
        
        # Rename columns
        completion_summary = completion_summary.rename(columns={
            'TotalBaseWaterVolume_sum': 'total_water_volume',
            'TotalBaseNonWaterVolume_sum': 'total_non_water_volume',
            'TVD_first': 'tvd',
            'TotalDepth_first': 'total_depth',
            'JobEndDate_parsed_min': 'first_treatment_date',
            'JobEndDate_parsed_max': 'last_treatment_date',
            'JobEndDate_parsed_count': 'num_treatments'
        })
        
        # Calculate completion intensity
        if 'lateral_length' in completion_summary.columns:
            completion_summary['water_per_foot'] = (
                completion_summary['total_water_volume'] / 
                completion_summary['lateral_length'].replace(0, np.nan)
            )
        
        logger.info(f"  Processed {len(completion_summary):,} wells with completion data")
        
        return completion_summary
    
    def extract_proppant_metrics(self):
        """
        Extract proppant loading from FracFocus ingredient data
        """
        logger.info("\nExtracting proppant metrics from FracFocus...")
        
        ff_file = self.interim_dir.parent / 'fracfocus' / 'fracfocus_cleaned.parquet'
        if not ff_file.exists():
            return None
        
        ff_df = pd.read_parquet(ff_file)
        
        # Filter for proppant (sand, ceramic, etc.)
        proppant_keywords = ['sand', 'proppant', 'ceramic', 'frac sand', 'silica']
        
        if 'Purpose' in ff_df.columns:
            proppant_mask = ff_df['Purpose'].astype(str).str.lower().str.contains(
                '|'.join(proppant_keywords), 
                na=False
            )
            proppant_df = ff_df[proppant_mask].copy()
            
            logger.info(f"  Found {len(proppant_df):,} proppant records")
            
            # Aggregate proppant by well
            proppant_summary = proppant_df.groupby('API_NUMBER').agg({
                'MassIngredient': 'sum',  # Total proppant mass
                'PercentHFJob': 'mean'    # Average proppant concentration
            }).reset_index()
            
            proppant_summary = proppant_summary.rename(columns={
                'MassIngredient': 'total_proppant_lbs',
                'PercentHFJob': 'avg_proppant_percent'
            })
            
            logger.info(f"  Processed {len(proppant_summary):,} wells with proppant data")
            
            return proppant_summary
        
        return None
    
    def extract_chemical_metrics(self):
        """
        Extract key chemical types from FracFocus
        """
        logger.info("\nExtracting chemical metrics from FracFocus...")
        
        ff_file = self.interim_dir.parent / 'fracfocus' / 'fracfocus_cleaned.parquet'
        if not ff_file.exists():
            return None
        
        ff_df = pd.read_parquet(ff_file)
        
        # Define chemical categories
        chemical_categories = {
            'friction_reducer': ['friction', 'slick'],
            'surfactant': ['surfactant', 'surface tension'],
            'acid': ['acid', 'hcl', 'hydrochloric'],
            'scale_inhibitor': ['scale'],
            'biocide': ['biocide', 'bacteria'],
            'crosslinker': ['crosslink', 'gel'],
            'breaker': ['breaker', 'enzyme']
        }
        
        chemical_summary = []
        
        for api in ff_df['API_NUMBER'].unique():
            well_data = ff_df[ff_df['API_NUMBER'] == api]
            well_chemicals = {'API_NUMBER': api}
            
            for chem_type, keywords in chemical_categories.items():
                if 'Purpose' in well_data.columns:
                    mask = well_data['Purpose'].astype(str).str.lower().str.contains(
                        '|'.join(keywords), 
                        na=False
                    )
                    well_chemicals[f'uses_{chem_type}'] = mask.any()
                    well_chemicals[f'{chem_type}_count'] = mask.sum()
            
            chemical_summary.append(well_chemicals)
        
        chemical_df = pd.DataFrame(chemical_summary)
        
        logger.info(f"  Processed {len(chemical_df):,} wells with chemical data")
        
        return chemical_df
    
    def link_to_packet_data(self, design_df):
        """
        Link well design to PACKET data for API/Lease mapping
        """
        logger.info("\nLinking to PACKET data for API numbers...")
        
        packet_file = self.interim_dir / 'PACKET.parquet'
        if not packet_file.exists():
            logger.warning("PACKET data not found")
            return design_df
        
        packet_df = pd.read_parquet(packet_file)
        
        # Extract key identifiers
        packet_clean = pd.DataFrame({
            'tracking_no': packet_df['field_1'].astype(str),
            'lease_no': packet_df['field_6'].astype(str),
            'district': packet_df['field_27'].astype(str),
        })
        
        # Create LEASE_ID
        packet_clean['LEASE_ID'] = (
            packet_clean['lease_no'].str.zfill(6) + 
            packet_clean['district'].str.strip().str.zfill(2)
        )
        
        # Merge
        design_with_ids = design_df.merge(
            packet_clean[['tracking_no', 'LEASE_ID']],
            on='tracking_no',
            how='left'
        )
        
        logger.info(f"  Linked {design_with_ids['LEASE_ID'].notna().sum():,} wells to LEASE_ID")
        
        return design_with_ids
    
    def create_master_well_design(self):
        """
        Create master well design dataset
        """
        logger.info("\n" + "="*70)
        logger.info("CREATING MASTER WELL DESIGN DATASET")
        logger.info("="*70)
        
        # Extract all components
        casing = self.extract_casing_design()
        tubing = self.extract_tubing_design()
        liner = self.extract_liner_design()
        completion = self.extract_completion_design()
        proppant = self.extract_proppant_metrics()
        chemicals = self.extract_chemical_metrics()
        
        # Start with casing as base (has tracking_no)
        if casing is not None:
            master = casing
        else:
            logger.error("Cannot create master dataset without casing data")
            return None
        
        # Merge tubing
        if tubing is not None:
            master = master.merge(tubing, on='tracking_no', how='left')
        
        # Merge liner
        if liner is not None:
            master = master.merge(liner, on='tracking_no', how='left')
        
        # Link to PACKET for LEASE_ID and API mapping
        master = self.link_to_packet_data(master)
        
        # For FracFocus data (uses API_NUMBER), need API in master
        # We'll merge these separately and join by API when available
        
        logger.info(f"\n✓ Master well design dataset: {len(master):,} wells")
        logger.info(f"  Columns: {len(master.columns)}")
        
        # Save W-2 based design
        w2_output = self.processed_dir / 'well_design_w2.parquet'
        master.to_parquet(w2_output, index=False)
        logger.info(f"\n✓ Saved W-2 well design to: {w2_output}")
        
        # Save FracFocus completion design separately
        if completion is not None:
            ff_output = self.processed_dir / 'completion_design_fracfocus.parquet'
            completion.to_parquet(ff_output, index=False)
            logger.info(f"✓ Saved FracFocus completion design to: {ff_output}")
        
        # Save proppant metrics
        if proppant is not None:
            prop_output = self.processed_dir / 'proppant_metrics.parquet'
            proppant.to_parquet(prop_output, index=False)
            logger.info(f"✓ Saved proppant metrics to: {prop_output}")
        
        # Save chemical metrics
        if chemicals is not None:
            chem_output = self.processed_dir / 'chemical_metrics.parquet'
            chemicals.to_parquet(chem_output, index=False)
            logger.info(f"✓ Saved chemical metrics to: {chem_output}")
        
        return {
            'w2_design': master,
            'completion_design': completion,
            'proppant': proppant,
            'chemicals': chemicals
        }


def main():
    project_root = Path.cwd()
    interim_dir = project_root / 'data' / 'interim' / 'rrc'
    processed_dir = project_root / 'data' / 'processed' / 'completions'
    
    print("\n" + "=" * 80)
    print("WELL DESIGN EXTRACTION")
    print("=" * 80)
    
    extractor = WellDesignExtractor(interim_dir, processed_dir)
    
    results = extractor.create_master_well_design()
    
    if results:
        print("\n" + "=" * 80)
        print("✓ EXTRACTION COMPLETE!")
        print("=" * 80)
        print(f"\nOutput files in: {processed_dir}")
        print(f"\nWell Design Datasets Created:")
        print(f"  - well_design_w2.parquet (casing, tubing, liner)")
        print(f"  - completion_design_fracfocus.parquet (stages, fluids, intensity)")
        print(f"  - proppant_metrics.parquet (sand/proppant loading)")
        print(f"  - chemical_metrics.parquet (surfactants, acids, etc.)")
        print(f"\n✓ Ready for attribution analysis!")


if __name__ == "__main__":
    main()