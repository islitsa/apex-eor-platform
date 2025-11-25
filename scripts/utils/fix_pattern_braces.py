"""Fix braces in pipeline_explorer_m3_beautiful pattern"""

# Read the file
with open("src/templates/gradio_snippets.py", "r", encoding="utf-8") as f:
    content = f.read()

# Find the pattern
start_marker = '"pipeline_explorer_m3_beautiful": """'
end_marker = '"""\n}'

start_idx = content.find(start_marker)
if start_idx == -1:
    print("Pattern not found!")
    exit(1)

start_idx += len(start_marker)
end_idx = content.find(end_marker, start_idx)

if end_idx == -1:
    print("End marker not found!")
    exit(1)

# Extract pattern
pattern = content[start_idx:end_idx]
print(f"Found pattern: {len(pattern)} chars")

# Escape braces except {pipeline_data}
pattern = pattern.replace('{pipeline_data}', 'PIPELINE_DATA_PLACEHOLDER')
pattern = pattern.replace('{', '{{').replace('}', '}}')
pattern = pattern.replace('PIPELINE_DATA_PLACEHOLDER', '{pipeline_data}')

print(f"Escaped: {pattern.count('{{')} braces")

# Replace in content
new_content = content[:start_idx] + pattern + content[end_idx:]

# Write back
with open("src/templates/gradio_snippets.py", "w", encoding="utf-8") as f:
    f.write(new_content)

print("Done!")
