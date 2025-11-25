"""
Test parser handles CSS file markers correctly
"""
import sys
import io

# Fix Unicode encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_css_file_parsing():
    """Test that parser correctly handles both // and /* */ file markers"""

    # Simulate Claude output with CSS file using /* */ marker
    test_case_1 = """// === FILE: App.tsx ===
import React from 'react';
import './index.css';

function App() {
  return <div>Hello</div>;
}

/* === FILE: index.css === */
@tailwind base;
@tailwind components;
@tailwind utilities;

// === FILE: package.json ===
{
  "name": "test"
}
"""

    # Test case 2: CSS embedded without proper marker (the bug scenario)
    test_case_2 = """// === FILE: main.tsx ===
import React from 'react';

function App() {
  return <div>Hello</div>;
}

/* === FILE: index.css === */
@tailwind base;
@tailwind components;
"""

    print("="*80)
    print("TEST CASE 1: CSS with /* === FILE: */ marker followed by another file")
    print("="*80)

    files = parse_files(test_case_1)

    print("\nParsed files:")
    for filename in files.keys():
        print(f"  - {filename}")

    assert 'App.tsx' in files, "App.tsx should be parsed"
    assert 'index.css' in files, "index.css should be parsed"
    assert 'package.json' in files, "package.json should be parsed"

    # Verify CSS content is correct
    css_content = files['index.css']
    assert '@tailwind base' in css_content, "CSS should contain Tailwind directives"
    assert '/* === FILE:' not in css_content, "CSS should not contain file marker"

    # Verify App.tsx doesn't contain CSS
    app_content = files['App.tsx']
    assert '@tailwind' not in app_content, "App.tsx should NOT contain CSS"
    assert "import './index.css'" in app_content, "App.tsx should import CSS"

    print("\n✅ TEST CASE 1 PASSED")

    print("\n" + "="*80)
    print("TEST CASE 2: CSS as last file with /* === FILE: */ marker")
    print("="*80)

    files = parse_files(test_case_2)

    print("\nParsed files:")
    for filename in files.keys():
        print(f"  - {filename}")

    assert 'main.tsx' in files, "main.tsx should be parsed"
    assert 'index.css' in files, "index.css should be parsed as separate file"

    # Verify main.tsx doesn't contain CSS
    main_content = files['main.tsx']
    assert '@tailwind' not in main_content, "main.tsx should NOT contain CSS"
    assert '/* === FILE:' not in main_content, "main.tsx should not contain file marker"

    # Verify index.css has correct content
    css_content = files['index.css']
    assert '@tailwind base' in css_content, "index.css should contain Tailwind directives"

    print("\n✅ TEST CASE 2 PASSED")
    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED - Parser correctly handles CSS file markers!")
    print("="*80)


def parse_files(generated_code: str):
    """Simulated parser matching react_developer.py logic"""
    files = {}
    current_file = None
    current_content = []
    in_markdown_fence = False

    for line in generated_code.split('\n'):
        # Check for file markers - supports both // and /* */ formats
        is_file_marker = False
        marker_filename = None

        if line.startswith('// === FILE:'):
            is_file_marker = True
            marker_filename = line.split('FILE:')[1].split('===')[0].strip()
        elif '/* === FILE:' in line.strip():
            # Handle CSS-style markers
            is_file_marker = True
            try:
                marker_filename = line.split('FILE:')[1].split('===')[0].strip()
                print(f"  [Parser] Detected CSS-style file marker for: {marker_filename}")
            except:
                print(f"  [Parser] Warning: Malformed CSS file marker: {line}")

        if is_file_marker and marker_filename:
            # Save previous file
            if current_file:
                content = '\n'.join(current_content).rstrip()
                # Remove trailing markdown fences
                lines = content.split('\n')
                while lines and lines[-1].strip().startswith('```'):
                    lines.pop()
                content = '\n'.join(lines).rstrip()
                files[current_file] = content

            # Start new file
            current_file = marker_filename
            current_content = []
            in_markdown_fence = False
        else:
            if current_file:
                # Check if this line is a markdown fence marker
                if line.strip().startswith('```'):
                    in_markdown_fence = not in_markdown_fence
                    continue

                # Only append content if we're NOT inside a markdown fence
                if not in_markdown_fence:
                    current_content.append(line)

    # Save last file
    if current_file:
        content = '\n'.join(current_content).rstrip()
        lines = content.split('\n')
        while lines and lines[-1].strip().startswith('```'):
            lines.pop()
        content = '\n'.join(lines).rstrip()
        files[current_file] = content

    return files


if __name__ == "__main__":
    test_css_file_parsing()
