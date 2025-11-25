"""
Test new pipeline_monitoring_m3 pattern with real pipeline data
"""
from src.analyzers.pipeline_context_analyzer import PipelineContextAnalyzer
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("PIPELINE MONITORING M3 PATTERN - FULL ETL DASHBOARD")
print("=" * 80)
print()

# Load real pipeline data
print("Loading pipeline context...")
analyzer = PipelineContextAnalyzer()
context = analyzer.generate_context_from_filesystem()

# Extract summary stats
data_sources = context.get("data_sources", {})
source_names = list(data_sources.keys())
total_datasets = sum(len(src.get("datasets", {})) for src in data_sources.values())
processing_count = sum(
    1 for src in data_sources.values()
    for ds in src.get("datasets", {}).values()
    if ds.get("status") in ["processing", "incomplete"]
)

pipeline_data = {
    "source_names": source_names,
    "total_sources": len(source_names),
    "total_datasets": total_datasets,
    "processing_count": processing_count
}

print(f"  Sources: {pipeline_data['total_sources']}")
print(f"  Total datasets: {pipeline_data['total_datasets']}")
print()

# Load pattern
print("Loading pipeline_monitoring_m3 pattern...")
with open("pipeline_monitoring_m3_pattern.py", "r", encoding="utf-8") as f:
    content = f.read()
    # Extract just the pattern string
    start = content.find('PIPELINE_MONITORING_M3_PATTERN = """') + len('PIPELINE_MONITORING_M3_PATTERN = """')
    end = content.rfind('"""')
    pattern_template = content[start:end]

# Substitute data
code = pattern_template.replace("{pipeline_data}", str(pipeline_data))

# Write to file
output_file = "generated_pipeline_monitor.py"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(code)

print(f"  Generated: {output_file} ({len(code):,} chars)")
print()

# Show features
print("=" * 80)
print("FEATURES INCLUDED")
print("=" * 80)
features = [
    ("Pipeline stage visualization", "DOWNLOAD" in code and "EXTRACT" in code and "PARSE" in code),
    ("Per-dataset status cards", "Dataset Status" in code),
    ("File browser with metadata", "File Preview" in code),
    ("Search/filter functionality", "Search" in code),
    ("Tree-like navigation", "Dataset Explorer" in code),
    ("Pipeline health metrics", "PIPELINE HEALTH" in code),
    ("Lazy loading enabled", "PipelineContextAnalyzer" in code),
    ("Column schema preview", "Schema" in code),
    ("Sample data preview", "Sample Data" in code),
]

for feature, present in features:
    status = "[✓]" if present else "[✗]"
    print(f"  {status} {feature}")

print()
print("=" * 80)
print(f"Launch with: python {output_file}")
print("=" * 80)
