"""
Quick test to regenerate generated_ui.py with fixed M3 template
"""
from src.templates.gradio_snippets import SnippetAssembler
from src.analyzers.pipeline_context_analyzer import PipelineContextAnalyzer

# Extract pipeline data
extractor = PipelineContextAnalyzer()
context = extractor.extract_context()

# Get M3 pattern code
assembler = SnippetAssembler()
code = assembler.get_pattern("hierarchical_data_navigation_m3", pipeline_data=context["pipeline_data"])

# Write to file
with open("generated_ui.py", "w", encoding="utf-8") as f:
    f.write(code)

print(f"[OK] Regenerated generated_ui.py with fixed M3 template ({len(code)} chars)")
