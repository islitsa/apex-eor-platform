"""
Test that the parser fix handles all markdown fence types
"""
import sys
import io

# Fix Unicode encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_markdown_parsing():
    """Test that parser handles all markdown fence types including ```markdown"""

    test_input = """// === FILE: tsconfig.json ===
{
  "compilerOptions": {
    "target": "ES2020"
  }
}
```markdown
This should be filtered out
```

// === FILE: App.tsx ===
export default function App() {
  return <div>Hello</div>;
}
```unknown-language
This should also be filtered
```

// === FILE: package.json ===
{
  "name": "test"
}
```text
More text to filter
```
"""

    # Import the parser
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))

    from src.agents.react_developer import ReactDeveloperAgent

    # Create agent and parse
    agent = ReactDeveloperAgent(styling_framework="tailwind")
    files = agent._parse_generated_files(test_input)

    print("=" * 80)
    print("PARSER FIX TEST")
    print("=" * 80)
    print()

    # Test 1: tsconfig.json should not contain markdown
    print("TEST 1: tsconfig.json markdown filtering")
    if '```markdown' not in files['tsconfig.json']:
        print("  ✅ PASS - ```markdown filtered out")
    else:
        print("  ❌ FAIL - ```markdown still present")

    if 'This should be filtered' not in files['tsconfig.json']:
        print("  ✅ PASS - Markdown content filtered out")
    else:
        print("  ❌ FAIL - Markdown content still present")

    # Test 2: App.tsx should not contain unknown-language fence
    print()
    print("TEST 2: App.tsx unknown fence filtering")
    if '```unknown-language' not in files['App.tsx']:
        print("  ✅ PASS - ```unknown-language filtered out")
    else:
        print("  ❌ FAIL - ```unknown-language still present")

    # Test 3: package.json should not contain text fence
    print()
    print("TEST 3: package.json text fence filtering")
    if '```text' not in files['package.json']:
        print("  ✅ PASS - ```text filtered out")
    else:
        print("  ❌ FAIL - ```text still present")

    # Test 4: Verify valid JSON
    print()
    print("TEST 4: JSON validity")
    import json
    try:
        json.loads(files['tsconfig.json'])
        print("  ✅ PASS - tsconfig.json is valid JSON")
    except json.JSONDecodeError as e:
        print(f"  ❌ FAIL - tsconfig.json is invalid: {e}")

    try:
        json.loads(files['package.json'])
        print("  ✅ PASS - package.json is valid JSON")
    except json.JSONDecodeError as e:
        print(f"  ❌ FAIL - package.json is invalid: {e}")

    print()
    print("=" * 80)
    print("GENERATED FILES:")
    print("=" * 80)
    for filename, content in files.items():
        print(f"\n{filename}:")
        print("-" * 40)
        print(content[:200])
        if len(content) > 200:
            print(f"... ({len(content) - 200} more chars)")

    print()
    print("=" * 80)
    print("✅ Parser fix test complete!")
    print("=" * 80)

if __name__ == "__main__":
    test_markdown_parsing()
