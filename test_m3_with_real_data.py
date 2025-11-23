"""
Test M3 pattern with real pipeline data
"""
from src.analyzers.pipeline_context_analyzer import PipelineContextAnalyzer
from src.templates.gradio_snippets import SnippetAssembler
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("M3 PATTERN TEST WITH REAL PIPELINE DATA")
print("=" * 80)
print()

# Load real pipeline data (summary only for lazy loading)
print("Loading pipeline context...")
analyzer = PipelineContextAnalyzer()
context = analyzer.generate_context_from_filesystem()

# Extract ONLY summary stats and source names (lightweight!)
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
print(f"  Summary data size: ~{len(str(pipeline_data))} bytes (vs {len(str(data_sources)):,} bytes for full data)")
print()

# Generate UI using M3 pattern
print("Generating UI with M3 pattern...")
assembler = SnippetAssembler()
code = assembler.get_pattern("hierarchical_data_navigation_m3", pipeline_data=pipeline_data)

# Write to file
output_file = "generated_m3_real_data.py"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(code)

print(f"  Generated: {output_file} ({len(code):,} chars)")
print()

# Show preview of what it contains
print("=" * 80)
print("PREVIEW")
print("=" * 80)
print()
print("Checking for real data integration:")

checks = [
    ("Lazy loading enabled", "PipelineContextAnalyzer" in code),
    ("Real sources in choices", "fracfocus" in code and "rrc" in code),
    ("File listing logic", "file_info.get" in code and "size_bytes" in code),
    ("Stage detection", "pipeline_stages" in code),
    ("Summary stats used", "SUMMARY_DATA" in code),
    ("M3 theme", "get_m3_theme_css()" in code),
    ("Breadcrumb navigation", "Current Path" in code),
]

for check_name, result in checks:
    status = "[OK]" if result else "[FAIL]"
    print(f"  {status} {check_name}")

print()
print("=" * 80)
print(f"Launch with: python {output_file}")
print("=" * 80)
