"""
Regenerate the dashboard with the fixed generator (Python syntax)
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from src.agents.hybrid_code_generator import HybridCodeGenerator
from src.utils.context_extractor import PipelineContextExtractor

print("Regenerating dashboard with JSON fix...")

# Extract context
extractor = PipelineContextExtractor()
context = extractor.extract_from_metadata()

# Generate fresh code
generator = HybridCodeGenerator()
requirements = {
    'screen_type': 'pipeline_dashboard_navigation',
    'intent': 'Browse pipeline data sources and datasets'
}

code = generator.generate(requirements, context)

# Save to file
output_path = project_root / "generated_pipeline_dashboard.py"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(code)

print(f"\n[OK] Generated {len(code):,} chars to {output_path}")
print("[OK] Using Python syntax (True/False/None) not JSON (true/false/null)")