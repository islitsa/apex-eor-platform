from src.analyzers.pipeline_context_analyzer import PipelineContextAnalyzer
import warnings
import json

warnings.filterwarnings('ignore')

analyzer = PipelineContextAnalyzer()
context = analyzer.generate_context_from_filesystem()

print("=" * 80)
print("PIPELINE CONTEXT STRUCTURE")
print("=" * 80)
print(f"\nTop-level keys: {list(context.keys())}")

data_sources = context.get('data_sources', {})
print(f"\nNumber of data sources: {len(data_sources)}")
print(f"Data source keys: {list(data_sources.keys())}")

if data_sources:
    first_key = list(data_sources.keys())[0]
    print(f"\nFirst source '{first_key}' structure:")
    print(json.dumps(data_sources[first_key], indent=2)[:800])

# Check what the test script was using
print("\n" + "=" * 80)
print("WHAT test_gradient_with_pipeline.py EXPECTS")
print("=" * 80)
pipeline_data = context.get("pipeline_data", {"sources": {}})
print(f"pipeline_data: {pipeline_data}")
print(f"pipeline_data.sources: {pipeline_data.get('sources', {})}")
