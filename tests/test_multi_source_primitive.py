"""Test multi-source dashboard using primitive composition"""
from src.agents.ux_designer import UXDesignerAgent, DesignSpec
from src.agents.gradio_developer import GradioImplementationAgent
from src.analyzers.pipeline_context_analyzer import PipelineContextAnalyzer
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("TESTING: Multi-Source Dashboard with Primitive Composition")
print("=" * 80)
print()

# Load pipeline context
print("Loading pipeline context...")
analyzer = PipelineContextAnalyzer()
context = analyzer.generate_context_from_filesystem()
data_sources = context.get("data_sources", {})
print(f"  Loaded {len(data_sources)} data sources")
print()

# Create a prompt for MULTIPLE data sources
test_prompt = """create a dashboard showing all data sources with their pipeline stages.
Show: Fracfocus (Chemical Data), NETL EDX (Laboratory Data), USGS (Water Data).
Each source has stages: Download, Extract, Parse. All complete."""

print(f"Test Prompt: {test_prompt}")
print()

# Create requirements dict with multiple sources
# Filter to just 3 sources for testing
filtered_sources = {
    k: v for k, v in list(data_sources.items())[:3]
}

requirements = {
    'screen_type': 'dashboard',
    'intent': test_prompt,
    'user_needs': test_prompt,
    'data_sources': filtered_sources
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

# Check if it detects as simple or complex
print("Checking complexity detection...")
is_simple = gradio_dev._is_simple_request(design_spec, filtered_sources)
print(f"  Simple request: {is_simple}")
print(f"  Explanation: {gradio_dev._explain_simple_detection(design_spec, filtered_sources)}")
print()

# Gradio Developer builds UI
print("Gradio Developer building UI...")
context = {
    'data_sources': filtered_sources
}
code = gradio_dev.build(design_spec, context)
print()

# Write to file
output_file = "generated_multi_source.py"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(code)

print(f"Generated: {output_file}")
print(f"Code length: {len(code):,} chars")
print()

print("=" * 80)
print("ANALYSIS")
print("=" * 80)
print(f"Number of sources: {len(filtered_sources)}")
print(f"Sources: {', '.join(filtered_sources.keys())}")
print(f"Detection: {'SIMPLE (primitives)' if is_simple else 'COMPLEX (pattern)'}")
print()

print("Next: Launch the UI with 'python generated_multi_source.py'")
