"""Check actual dataset count"""
from src.analyzers.pipeline_context_analyzer import PipelineContextAnalyzer
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("DATASET COUNT ANALYSIS")
print("="*80)

analyzer = PipelineContextAnalyzer()
ctx = analyzer.generate_context_from_filesystem()

print(f"\nTotal Sources: {len(ctx['data_sources'])}")
print()

total_datasets = 0
for src_name, src_data in ctx['data_sources'].items():
    datasets = src_data.get('datasets', {})
    print(f"{src_name}: {len(datasets)} dataset(s)")
    for ds_name in datasets.keys():
        print(f"  - {ds_name}")
        total_datasets += 1

print()
print("="*80)
print(f"TOTAL DATASETS: {total_datasets}")
print("="*80)
