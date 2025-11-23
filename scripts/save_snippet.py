"""
Save approved generated dashboard as a snippet template

Usage:
    python scripts/save_snippet.py pipeline_navigation

This will:
1. Read generated_pipeline_dashboard.py
2. Extract the code template
3. Update src/templates/gradio_snippets.py
4. Replace hardcoded data with {pipeline_data} placeholder
"""

import sys
import re
from pathlib import Path

def save_as_snippet(snippet_name: str, source_file: str = "generated_pipeline_dashboard.py"):
    """Save generated code as a reusable snippet"""

    project_root = Path(__file__).parent.parent
    source_path = project_root / source_file
    snippets_path = project_root / "src" / "templates" / "gradio_snippets.py"

    if not source_path.exists():
        print(f"ERROR: {source_path} not found!")
        print("Generate a dashboard first with --force-llm")
        return

    # Read generated code
    print(f"Reading generated code from {source_path}...")
    with open(source_path, 'r', encoding='utf-8') as f:
        code = f.read()

    # Replace the actual PIPELINE_DATA with placeholder
    # Find the PIPELINE_DATA = {...} section and replace with placeholder
    pattern = r'PIPELINE_DATA = \{[^}]+\}'

    # For nested dicts, we need a more sophisticated approach
    # Find start of PIPELINE_DATA and end (matching braces)
    start_match = re.search(r'PIPELINE_DATA = ', code)
    if not start_match:
        print("ERROR: Could not find PIPELINE_DATA in generated code")
        return

    start_idx = start_match.end()

    # Find matching closing brace
    brace_count = 0
    in_pipeline_data = False
    end_idx = start_idx

    for i, char in enumerate(code[start_idx:], start=start_idx):
        if char == '{':
            brace_count += 1
            in_pipeline_data = True
        elif char == '}':
            brace_count -= 1
            if in_pipeline_data and brace_count == 0:
                end_idx = i + 1
                break

    # Extract the data portion
    data_section = code[start_match.start():end_idx]

    # Replace with placeholder
    template_code = code.replace(data_section, 'PIPELINE_DATA = {pipeline_data}')

    # Clean up the template - remove extra blank lines
    template_code = re.sub(r'\n\n\n+', '\n\n', template_code)

    print(f"\n{'='*80}")
    print(f"SNIPPET PREVIEW")
    print(f"{'='*80}")
    print(template_code[:500] + "...")
    print(f"\nTotal length: {len(template_code):,} chars")

    # Confirm
    response = input("\nSave this as snippet? (yes/no): ").lower().strip()

    if response != 'yes':
        print("Cancelled.")
        return

    # Read current snippets file
    with open(snippets_path, 'r', encoding='utf-8') as f:
        snippets_content = f.read()

    # Find the PATTERNS dict and the specific snippet
    pattern_start = snippets_content.find(f'"{snippet_name}":')

    if pattern_start == -1:
        print(f"\nWARNING: Snippet '{snippet_name}' not found in gradio_snippets.py")
        print("You'll need to manually add it to the PATTERNS dict")

        # Save to a separate file
        output_path = project_root / f"snippet_{snippet_name}.py"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f'# Snippet: {snippet_name}\n')
            f.write(f'# Add this to PATTERNS dict in gradio_snippets.py\n\n')
            f.write(f'"{snippet_name}": """\n{template_code}\n""",\n')

        print(f"\nSaved snippet template to: {output_path}")
        print("Manually copy it into gradio_snippets.py PATTERNS dict")
        return

    # Find the end of this snippet (next triple quote)
    # Find the opening triple quotes
    opening_quotes = snippets_content.find('"""', pattern_start)
    if opening_quotes == -1:
        print("ERROR: Could not find opening quotes for snippet")
        return

    # Find the closing triple quotes
    closing_quotes = snippets_content.find('"""', opening_quotes + 3)
    if closing_quotes == -1:
        print("ERROR: Could not find closing quotes for snippet")
        return

    # Replace the snippet content
    new_snippets = (
        snippets_content[:opening_quotes + 3] +
        '\n' + template_code + '\n' +
        snippets_content[closing_quotes:]
    )

    # Backup original
    backup_path = snippets_path.with_suffix('.py.backup')
    print(f"\nBacking up original to: {backup_path}")
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(snippets_content)

    # Write updated snippets
    print(f"Updating: {snippets_path}")
    with open(snippets_path, 'w', encoding='utf-8') as f:
        f.write(new_snippets)

    print(f"\n{'='*80}")
    print("SUCCESS!")
    print(f"{'='*80}")
    print(f"Snippet '{snippet_name}' updated in gradio_snippets.py")
    print(f"Original backed up to: {backup_path.name}")
    print(f"\nNext time you generate without --force-llm, it will use this improved snippet!")
    print(f"This gives you 99.3% token savings with the design you approved.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/save_snippet.py <snippet_name>")
        print("\nAvailable snippets:")
        print("  - pipeline_navigation")
        print("  - data_grid_with_filter")
        print("  - master_detail_view")
        sys.exit(1)

    snippet_name = sys.argv[1]
    save_as_snippet(snippet_name)