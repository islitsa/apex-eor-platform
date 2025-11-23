"""
Test parser bug with markdown fences
"""
import sys
import io

# Fix Unicode encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Simulate the parser logic - Test Case 1: Normal flow with fence between files
test_input1 = """// === FILE: tsconfig.node.json ===
{
  "compilerOptions": {
    "composite": true
  }
}

```markdown
// === FILE: README.md ===
# README
"""

# Test Case 2: Fence appears but is NOT followed by another file marker (the actual bug!)
test_input2 = """// === FILE: tsconfig.node.json ===
{
  "compilerOptions": {
    "composite": true
  }
}

```markdown
"""

print("="*80)
print("TEST CASE 1: Fence followed by another file")
print("="*80)
test_input = test_input1

files = {}
current_file = None
current_content = []
in_markdown_fence = False

for line_num, line in enumerate(test_input.split('\n'), 1):
    print(f"Line {line_num}: {repr(line)[:60]} | in_fence={in_markdown_fence}")

    if line.startswith('// === FILE:'):
        # Save previous file
        if current_file:
            content = '\n'.join(current_content).rstrip()
            if content.endswith('```'):
                content = content[:-3].rstrip()
            files[current_file] = content
            print(f"  → Saved {current_file} ({len(content)} chars)")

        # Start new file
        current_file = line.split('FILE:')[1].split('===')[0].strip()
        current_content = []
        in_markdown_fence = False
        print(f"  → Started {current_file}")
    else:
        if current_file:
            # Check if this line is a markdown fence marker
            if line.strip().startswith('```'):
                print(f"  → Detected fence, toggling (was {in_markdown_fence})")
                in_markdown_fence = not in_markdown_fence
                continue  # Skip the fence line itself

            # Only append content if we're NOT inside a markdown fence
            if not in_markdown_fence:
                current_content.append(line)
                print(f"  → Appended to {current_file}")
            else:
                print(f"  → Skipped (inside fence)")

# Save last file (with enhanced fence removal)
if current_file:
    content = '\n'.join(current_content).rstrip()
    # Remove trailing markdown fences (handles both ``` and ```language)
    lines = content.split('\n')
    while lines and lines[-1].strip().startswith('```'):
        lines.pop()
        print(f"  → Removed trailing markdown fence")
    content = '\n'.join(lines).rstrip()
    files[current_file] = content
    print(f"  → Saved last {current_file} ({len(content)} chars)")

print("\n" + "="*80)
print("RESULTS:")
for filename, content in files.items():
    print(f"\n{filename}:")
    print(repr(content))
    print(f"Ends with '```'? {content.endswith('```')}")
    print(f"Ends with '```markdown'? {content.endswith('```markdown')}")

# Now test case 2
print("\n\n" + "="*80)
print("TEST CASE 2: Fence at end of output (THE BUG SCENARIO)")
print("="*80)

files = {}
current_file = None
current_content = []
in_markdown_fence = False

for line_num, line in enumerate(test_input2.split('\n'), 1):
    if line.startswith('// === FILE:'):
        if current_file:
            content = '\n'.join(current_content).rstrip()
            lines = content.split('\n')
            while lines and lines[-1].strip().startswith('```'):
                lines.pop()
                print(f"  → Removed trailing markdown fence from {current_file}")
            content = '\n'.join(lines).rstrip()
            files[current_file] = content

        current_file = line.split('FILE:')[1].split('===')[0].strip()
        current_content = []
        in_markdown_fence = False
        print(f"Line {line_num}: Started {current_file}")
    else:
        if current_file:
            if line.strip().startswith('```'):
                in_markdown_fence = not in_markdown_fence
                print(f"Line {line_num}: Detected fence, toggling")
                continue

            if not in_markdown_fence:
                current_content.append(line)
                print(f"Line {line_num}: Appended to {current_file}")

# Save last file with enhanced cleanup
if current_file:
    content = '\n'.join(current_content).rstrip()
    print(f"\nBefore cleanup: {repr(content)}")
    lines = content.split('\n')
    while lines and lines[-1].strip().startswith('```'):
        lines.pop()
        print(f"  → Removed trailing markdown fence from {current_file}")
    content = '\n'.join(lines).rstrip()
    print(f"After cleanup: {repr(content)}")
    files[current_file] = content

print("\n" + "="*80)
print("RESULTS (TEST CASE 2):")
for filename, content in files.items():
    print(f"\n{filename}:")
    print(repr(content))
    print(f"✓ Ends with '```'? {content.endswith('```')}")
    print(f"✓ Ends with '```markdown'? {content.endswith('```markdown')}")
