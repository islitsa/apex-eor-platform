"""Test the new beautiful pipeline pattern"""
from src.analyzers.pipeline_context_analyzer import PipelineContextAnalyzer
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("TESTING: pipeline_explorer_m3_beautiful")
print("=" * 80)
print()

# Load pipeline context
print("Loading pipeline context...")
analyzer = PipelineContextAnalyzer()
context = analyzer.generate_context_from_filesystem()

# Extract summary
data_sources = context.get("data_sources", {})
source_names = list(data_sources.keys())
total_datasets = sum(
    1 for src in data_sources.values()
    if src.get("display_name", "").count("/") > 0
)

pipeline_data = {
    "source_names": source_names,
    "total_sources": len(source_names),
    "total_datasets": total_datasets,
}

print(f"  Sources: {pipeline_data['total_sources']}")
print(f"  Datasets: {pipeline_data['total_datasets']}")
print()

# Load pattern
print("Loading pipeline_explorer_m3_beautiful pattern...")
from src.templates.gradio_snippets import PATTERNS

if "pipeline_explorer_m3_beautiful" not in PATTERNS:
    print("  ✗ Pattern not found in PATTERNS dict!")
    print(f"  Available patterns: {len(PATTERNS)}")
    exit(1)

pattern = PATTERNS["pipeline_explorer_m3_beautiful"]
print(f"  [OK] Pattern loaded ({len(pattern):,} chars)")
print()

# Generate UI code
print("Generating UI code...")
code = pattern.format(pipeline_data=pipeline_data)

# Write to file
output_file = "generated_beautiful_pipeline.py"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(code)

print(f"  [OK] Generated: {output_file}")
print()

print("=" * 80)
print("FEATURES")
print("=" * 80)
features = [
    ("3D Hexagon Cards", "clip-path: polygon" in code),
    ("M3 Color Gradients", "linear-gradient(135deg" in code),
    ("Per-Dataset Pipelines", "selected_dataset" in code),
    ("Status Indicators", "stage-hexagon complete" in code),
    ("Hover Effects", "transform: translateY" in code),
    ("Pulse Animation", "@keyframes pulse" in code),
    ("File Browser", "files_table" in code),
    ("Defensive Format Handling", "isinstance(files, list)" in code),
]

for feature, present in features:
    status = "[✓]" if present else "[✗]"
    print(f"  {status} {feature}")

print()
print("=" * 80)
print(f"Launch with: python {output_file}")
print("=" * 80)
