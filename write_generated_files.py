"""
Write generated files from test to disk
"""
import sys
from pathlib import Path
import io

# Fix encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agents.react_developer import ReactDeveloperAgent
from agents.ux_designer import DesignSpec

print("\n[SETUP] Generating code...")

# Create agent
react_dev = ReactDeveloperAgent()

# Create design spec
design_spec = DesignSpec(
    screen_type="dashboard",
    intent="Display fracfocus chemical data in a dashboard",
    components=[],
    interactions=[],
    patterns=["data-table", "loading-state"],
    styling={"framework": "tailwind", "theme": "light"},
    design_reasoning="Simple dashboard to display chemical data from fracfocus dataset"
)

# Mock data sources
data_sources = {
    'fracfocus': {
        'row_count': 239059,
        'columns': ['API', 'ChemicalName', 'CASNumber', 'Supplier', 'IngredientName'],
        'status': 'complete',
        'stages': ['downloads', 'extracted', 'parsed']
    }
}

design_spec.data_sources = data_sources

# Generate files
generated_files = react_dev.build(
    design_spec=design_spec,
    context={'user_prompt': "Create a dashboard showing fracfocus chemical data"}
)

# Write to disk
output_dir = Path('generated_react_dashboard_test')
output_dir.mkdir(exist_ok=True)

print(f"\n[WRITING] Writing {len(generated_files)} files to {output_dir}/")

for filename, content in generated_files.items():
    filepath = output_dir / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding='utf-8')
    print(f"  - {filename}")

print(f"\n✅ Files written to {output_dir}/")
print(f"\nNext steps:")
print(f"  1. cd {output_dir}")
print(f"  2. npm install")
print(f"  3. npm run dev")
print(f"  4. Open browser to http://localhost:5173")
