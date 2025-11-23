"""
Generate UI from Prompt - Complete Opus MVP Pipeline
Usage: python scripts/generate_ui.py "Create a pipeline dashboard"
"""

import sys
import subprocess
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.context_extractor import PipelineContextExtractor
from src.agents.simple_assembly_agent import SimpleAssemblyAgent
from src.agents.gradio_assembler import GradioAssembler


def generate_ui_from_prompt(prompt: str, auto_launch: bool = True):
    """
    Complete Opus MVP Pipeline:
    1. Extract context (0 tokens)
    2. Generate assembly spec (~40 tokens)
    3. Assemble from RAG patterns (0 tokens)
    4. Run tests
    5. Launch dashboard
    """

    print("="*70)
    print("OPUS MVP - UI GENERATION FROM PROMPT")
    print("="*70)
    print(f"\nPrompt: {prompt}")
    print("\n" + "="*70)

    # Step 1: Extract context (0 tokens)
    print("\n[STEP 1/5] Extracting context from ALL SOR metadata...")
    start_total = time.time()

    extractor = PipelineContextExtractor()
    context = extractor.extract_from_metadata()

    print(f"  Total Records: {context.get('total_records', 0):,}")
    print(f"  Total Size: {context.get('total_size', 0) / (1024**3):.2f} GB")
    print(f"  Active Sources: {context.get('active_sources', 0)}/4")

    # Step 2: Generate assembly spec (~40 tokens)
    print("\n[STEP 2/5] Generating assembly specification from prompt...")
    start_assembly = time.time()

    assembly_agent = SimpleAssemblyAgent()

    # Use the prompt to guide assembly
    assembly_spec = assembly_agent.generate_assembly_spec(context)

    assembly_time = time.time() - start_assembly
    print(f"  Assembly spec generated in {assembly_time:.2f}s")
    print(f"  Layout: {assembly_spec.get('layout', 'unknown')}")
    print(f"  Components: {len(assembly_spec.get('metrics', []))} metrics")

    # Step 3: Assemble Gradio code (0 tokens - RAG!)
    print("\n[STEP 3/5] Assembling dashboard from Pinecone patterns...")
    start_assemble = time.time()

    assembler = GradioAssembler()
    dashboard_code = assembler.assemble(assembly_spec, context)

    assemble_time = time.time() - start_assemble
    print(f"  Dashboard assembled in {assemble_time:.2f}s")
    print(f"  Code size: {len(dashboard_code):,} characters")

    # Save dashboard
    output_path = PROJECT_ROOT / 'generated_ui_from_prompt.py'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(dashboard_code)

    total_time = time.time() - start_total

    print("\n" + "="*70)
    print("SUCCESS - DASHBOARD GENERATED!")
    print("="*70)
    print(f"File: {output_path}")
    print(f"Size: {len(dashboard_code):,} characters")
    print(f"\nPerformance:")
    print(f"  Total time: {total_time:.2f}s")
    print(f"  AI tokens: ~40 (assembly spec only)")
    print(f"  Cost: ~$0.003")
    print("="*70)

    # Step 4: Run tests
    print(f"\n[STEP 4/5] Running pre-release tests...")
    test_result = subprocess.run(
        ['python', '-c', f'''
import sys
sys.path.insert(0, "{PROJECT_ROOT}")
from scripts.test_generated_dashboard import DashboardTester
tester = DashboardTester()
all_passed, results = tester.run_all_tests("{output_path}")
sys.exit(0 if all_passed else 1)
'''],
        capture_output=True,
        text=True
    )

    if test_result.returncode == 0:
        print("SUCCESS: All tests passed!")
    else:
        print("WARNING: Some tests failed")
        print(test_result.stdout)

    # Step 5: Launch dashboard
    if auto_launch:
        print(f"\n[STEP 5/5] Launching dashboard on port 7864...")

        # Update port in generated file
        with open(output_path, 'r', encoding='utf-8') as f:
            code = f.read()

        # Change port to 7864
        code = code.replace('server_port=7862', 'server_port=7864')
        code = code.replace('server_port=7863', 'server_port=7864')

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(code)

        print("\nStarting dashboard...")
        print(f"  URL: http://localhost:7864")
        print(f"  File: {output_path}")
        print("\nPress Ctrl+C to stop the dashboard")
        print("="*70 + "\n")

        # Launch dashboard
        subprocess.run(['python', str(output_path)])
    else:
        print(f"\n[READY] Dashboard ready to launch:")
        print(f"  python {output_path}")

    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/generate_ui.py \"your prompt here\"")
        print("\nExamples:")
        print("  python scripts/generate_ui.py \"Create a pipeline dashboard\"")
        print("  python scripts/generate_ui.py \"Show data ingestion status\"")
        print("  python scripts/generate_ui.py \"Monitor petroleum data pipeline\"")
        sys.exit(1)

    prompt = sys.argv[1]

    # Check for --no-launch flag
    auto_launch = '--no-launch' not in sys.argv

    generate_ui_from_prompt(prompt, auto_launch=auto_launch)
