"""Test that data hallucination fix works - forces primitive composition"""
from src.agents.ux_designer import UXDesignerAgent, DesignSpec
from src.agents.gradio_developer import GradioImplementationAgent
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("TESTING: Data Hallucination Fix (Primitive Composition Only)")
print("=" * 80)
print()

# Create a VERY SIMPLE prompt that won't match any patterns
# This will force primitive composition
test_prompt = "show Fracfocus chemical data with Download, Extract, Parse stages all complete"

print(f"Test Prompt: {test_prompt}")
print()

# Provide ONLY Fracfocus data source
data_sources = {
    'fracfocus': {
        'name': 'Fracfocus',
        'type': 'Chemical Data',
        'stages': [
            {'name': 'Download', 'status': 'complete'},
            {'name': 'Extract', 'status': 'complete'},
            {'name': 'Parse', 'status': 'complete'}
        ]
    }
}

requirements = {
    'screen_type': 'simple_display',  # NOT "dashboard" to avoid pattern matching
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
print(f"  Screen type: {design_spec.screen_type}")
print(f"  Recommended pattern: {design_spec.recommended_pattern}")
print()

# Check detection
print("Checking complexity detection...")
is_simple = gradio_dev._is_simple_request(design_spec, data_sources)
print(f"  Simple request: {is_simple}")
if not is_simple:
    print("  ERROR: Should be detected as simple! Pattern matching interfering.")
    print(f"  Pattern: {design_spec.recommended_pattern}")
print()

# Gradio Developer builds UI - should use primitives
print("Gradio Developer building UI...")
context = {'data_sources': data_sources}
code = gradio_dev.build(design_spec, context)
print()

# Write output
output_file = "generated_hallucination_test.py"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(code)

print(f"Generated: {output_file}")
print(f"Code length: {len(code):,} chars")
print()

# Critical checks
print("=" * 80)
print("HALLUCINATION CHECKS")
print("=" * 80)

# Check for hallucinated sources
hallucinated_sources = [
    'EPA Chemical Registry',
    'Well Production',
    'Geological Survey',
    'Water Quality',
    'Air Quality',
    'Seismic Activity',
    'Chemical Safety',
    'Infrastructure'
]

found_hallucinations = []
for source in hallucinated_sources:
    if source in code:
        found_hallucinations.append(source)

if found_hallucinations:
    print(f"FAIL: Found hallucinated sources: {found_hallucinations}")
else:
    print("PASS: No hallucinated sources found")

# Check it only has Fracfocus
if 'fracfocus' in code.lower() or 'Fracfocus' in code:
    print("PASS: Fracfocus is present")
else:
    print("FAIL: Fracfocus not found in output")

# Count how many data source cards/mentions
import re
card_pattern = r"(source[-_]?card|data[-_]?source)"
matches = re.findall(card_pattern, code, re.IGNORECASE)
print(f"Info: Found {len(matches)} source card references")

print()
print(f"Launch with: python {output_file}")
