"""Test Option 3 - Generic domain-agnostic prompt"""
from src.agents.ux_designer import UXDesignerAgent, DesignSpec
from src.agents.gradio_developer import GradioImplementationAgent
from src.analyzers.pipeline_context_analyzer import PipelineContextAnalyzer
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("TESTING: Option 3 - Generic Lovable Approach")
print("=" * 80)
print()

# Load pipeline context
print("Loading pipeline context...")
analyzer = PipelineContextAnalyzer()
context = analyzer.generate_context_from_filesystem()
data_sources = context.get("data_sources", {})
print(f"  Loaded {len(data_sources)} data sources")
print()

# Define test prompt (same as before)
test_prompt = "create a dashboard that shows stages for data pipeline. Data Sources: Fracfocus: Data type: Chemical Data : Stages: Download-Extracted-Parsed. All stages are complete"

print(f"Test Prompt: {test_prompt}")
print()

# Create requirements dict
requirements = {
    'screen_type': 'dashboard',
    'intent': test_prompt,
    'user_needs': test_prompt,
    'data_sources': data_sources
}

# Create agents
print("Creating agents...")
ux_designer = UXDesignerAgent()
gradio_dev = GradioImplementationAgent()
print()

# UX Designer creates design spec
print("UX Designer analyzing request...")
design_spec = ux_designer.design(requirements)
print(f"  Design spec created")
print(f"  Screen type: {design_spec.screen_type}")
print(f"  Intent: {design_spec.intent}")
print(f"  Recommended pattern: {design_spec.recommended_pattern}")
print()

# Gradio Developer builds UI
print("Gradio Developer building UI...")
code = gradio_dev.build(design_spec, context)
print()

# Write output
output_file = "generated_lovable_option3.py"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(code)

print(f"Generated: {output_file}")
print(f"Code length: {len(code):,} chars")
print()

# Check for improvements
print("=" * 80)
print("CHECKING FOR IMPROVEMENTS")
print("=" * 80)

checks = [
    ("No unwanted metrics grid", "metrics-grid" not in code),
    ("No 'Pipeline Status' summary", "Pipeline Status" not in code and "status summary" not in code.lower()),
    ("No generic 'Data Pipeline Dashboard' title", "Data Pipeline Dashboard" not in code),
    ("Simple focused output", code.count(".md-card") <= 2),  # Should be 1-2 cards max
]

for check_name, passed in checks:
    status = "[✓]" if passed else "[✗]"
    print(f"  {status} {check_name}")

print()
print("=" * 80)
print(f"Launch with: python {output_file}")
print("=" * 80)
