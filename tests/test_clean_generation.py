"""
Test clean generation with all fixes in place
"""
import sys
import io
from pathlib import Path

# Fix Unicode encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.agents.ui_orchestrator import UICodeOrchestrator

print("="*80)
print("TESTING CLEAN DASHBOARD GENERATION WITH ALL FIXES")
print("="*80)

# Create orchestrator
orchestrator = UICodeOrchestrator()

# User request
user_request = "Create a pipeline monitoring dashboard showing data sources with their status, file counts, and processing stages"

print(f"\n📝 User Request: {user_request}")
print(f"\n🔧 Generating with:")
print("  ✓ Enhanced parser (handles /* === FILE: */ markers)")
print("  ✓ Updated prompt (enforces // === FILE: format)")
print("  ✓ CSS-in-TSX validation")
print("  ✓ Gradient context enabled")
print("  ✓ Mock data validation")

# Generate
output_dir = Path(__file__).parent / "generated_dashboard_clean"
print(f"\n📁 Output directory: {output_dir}")

try:
    result = orchestrator.generate_ui_code(
        requirements={'user_intent': user_request},
        output_dir=str(output_dir),
        enable_gradient=True  # Enable gradient context
    )

    print("\n" + "="*80)
    print("✅ GENERATION COMPLETE")
    print("="*80)

    if result.get('success'):
        print(f"\n✓ Files generated: {len(result.get('files', []))}")
        print(f"✓ Output: {output_dir}")

        # List generated files
        if output_dir.exists():
            all_files = list(output_dir.rglob('*'))
            file_list = [f for f in all_files if f.is_file()]
            print(f"\n📄 Generated {len(file_list)} files:")
            for f in sorted(file_list)[:20]:  # Show first 20
                rel_path = f.relative_to(output_dir)
                print(f"  - {rel_path}")
            if len(file_list) > 20:
                print(f"  ... and {len(file_list) - 20} more")

        # Check for issues
        issues = []

        # Check main.tsx for CSS
        main_tsx = output_dir / "src" / "main.tsx"
        if main_tsx.exists():
            content = main_tsx.read_text()
            if '@tailwind' in content:
                issues.append("❌ main.tsx contains CSS (@tailwind)")
            else:
                print(f"\n✓ main.tsx does NOT contain CSS")

        # Check if index.css exists
        index_css = output_dir / "src" / "index.css"
        if index_css.exists():
            print(f"✓ index.css exists as separate file")
        else:
            issues.append("⚠️ index.css not found")

        # Check tsconfig files
        for tsconfig in ["tsconfig.json", "tsconfig.node.json"]:
            tsconfig_path = output_dir / tsconfig
            if tsconfig_path.exists():
                content = tsconfig_path.read_text()
                if '```' in content:
                    issues.append(f"❌ {tsconfig} contains markdown fences")
                else:
                    print(f"✓ {tsconfig} is clean (no markdown fences)")

        if issues:
            print(f"\n⚠️ Issues found:")
            for issue in issues:
                print(f"  {issue}")
        else:
            print(f"\n🎉 All validation checks passed!")
            print(f"\n🚀 To test the dashboard:")
            print(f"  cd {output_dir}")
            print(f"  npm install")
            print(f"  npm run dev")
    else:
        print(f"\n❌ Generation failed: {result.get('error', 'Unknown error')}")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
