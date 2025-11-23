from src.analyzers.pipeline_context_analyzer import PipelineContextAnalyzer
import json

ctx = PipelineContextAnalyzer().generate_context_from_filesystem()

# Look at fracfocus/Chemical_data
src = 'fracfocus'
ds = 'Chemical_data'
dataset_info = ctx['data_sources'][src]['datasets'][ds]

print("Dataset keys:")
print(list(dataset_info.keys()))
print()

print("Dataset info (first 2000 chars):")
filtered = {k: v for k, v in dataset_info.items() if k != 'directory_structure'}
print(json.dumps(filtered, indent=2, default=str)[:2000])
