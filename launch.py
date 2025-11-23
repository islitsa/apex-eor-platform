"""
APEX EOR Platform Launcher

Central launcher for all platform tools.
Provides a simple interface to run data ingestion or launch UI tools.

Usage:
    python launch.py                     # Interactive menu
    python launch.py ingest --all        # Run full ingestion pipeline
    python launch.py ui studio           # Launch Agent Studio
    python launch.py ui runner           # Launch Agent Chat Runner
    python launch.py ui collaborate      # Launch Collaborative Multi-Agent System (RECOMMENDED)
    python launch.py ui interface        # Launch Agent Chat Interface
    python launch.py status              # Check platform status
"""

import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from shared_state import PipelineState, SessionState


class APEXLauncher:
    """Central launcher for APEX EOR Platform"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.scripts_dir = self.project_root / 'scripts'

    def check_status(self):
        """Check and display platform status"""
        print("\n" + "="*70)
        print("APEX EOR PLATFORM STATUS")
        print("="*70)

        # Check for context
        summary = PipelineState.get_summary()

        print("\nPipeline Context:")
        if summary['has_context']:
            print(f"  [OK] Context exists ({summary.get('age_hours', 'Unknown')} hours old)")
            if summary['is_fresh']:
                print(f"  [OK] Context is fresh")
            else:
                print(f"  [WARNING] Context is stale (>{PipelineState.STALE_HOURS} hours old)")
                print(f"     Run: python launch.py ingest --generate-context")
        else:
            print("  [ERROR] No context found")
            print("     Run: python launch.py ingest --all")

        # Check for saved sessions
        session = SessionState.load_session()
        if session:
            print("\nLast Session:")
            if 'last_dashboard_file' in session:
                print(f"  Dashboard: {Path(session['last_dashboard_file']).name}")
            if 'last_generation_time' in session:
                gen_time = datetime.fromisoformat(session['last_generation_time'])
                print(f"  Generated: {gen_time.strftime('%Y-%m-%d %H:%M')}")

        # Show available context details
        context = PipelineState.load_context(check_freshness=False)
        if context and 'summary' in context:
            print("\nData Summary:")
            print(f"  Datasets:  {context['summary'].get('datasets_available', 0)}")
            print(f"  Records:   {context['summary'].get('human_readable_records', 'Unknown')}")
            print(f"  Size:      {context['summary'].get('human_readable_size', 'Unknown')}")

        print("\n" + "="*70)

    def run_ingestion(self, args: list):
        """Run data ingestion pipeline"""
        script = self.scripts_dir / 'pipeline' / 'run_ingestion.py'

        if not script.exists():
            print(f"❌ Ingestion script not found: {script}")
            return 1

        cmd = ['python', str(script)] + args
        print(f"Running: {' '.join(cmd)}")
        return subprocess.call(cmd)

    def launch_ui(self, tool: str):
        """Launch UI tool"""
        tools = {
            'studio': 'agent_studio.py',
            'runner': 'agent_chat_runner.py',
            'interface': 'agent_chat_interface.py',
            'collaborate': 'agent_studio.py'  # Interactive Agent Studio
        }

        if tool not in tools:
            print(f"[ERROR] Unknown UI tool: {tool}")
            print(f"   Available: {', '.join(tools.keys())}")
            return 1

        script = self.scripts_dir / 'ui' / tools[tool]

        if not script.exists():
            # Try alternate location (src/ui)
            script = self.project_root / 'src' / 'ui' / tools[tool]

        if not script.exists():
            print(f"[ERROR] UI script not found: {tools[tool]}")
            return 1

        # Check for context
        if not PipelineState.is_context_fresh(max_age_hours=48):
            print("[WARNING] No fresh context found")
            print("   Consider running: python launch.py ingest --generate-context")
            response = input("   Continue anyway? (y/N): ")
            if response.lower() != 'y':
                return 0

        print(f"\nLaunching {tool.title()}...")
        print(f"   URL: http://localhost:8501")
        print(f"   Press Ctrl+C to stop\n")

        cmd = ['streamlit', 'run', str(script)]
        return subprocess.call(cmd)

    def interactive_menu(self):
        """Show interactive menu"""
        while True:
            print("\n" + "="*70)
            print("APEX EOR PLATFORM - MAIN MENU")
            print("="*70)
            print("\nData Ingestion:")
            print("  1. Run full ingestion pipeline")
            print("  2. Generate context only")
            print("  3. Run specific phase (download/extract/parse)")

            print("\nUI Tools:")
            print("  4. Launch Agent Studio (Full IDE)")
            print("  5. Launch Agent Runner (Automated)")
            print("  6. Launch Agent Interface (Debug)")
            print("  7. Launch Collaborative Agents (RECOMMENDED - Multi-agent system)")

            print("\nOther:")
            print("  8. Check platform status")
            print("  9. Clear all state")
            print("  0. Exit")

            choice = input("\nSelect option (0-9): ").strip()

            if choice == '0':
                print("Goodbye!")
                return 0
            elif choice == '1':
                return self.run_ingestion(['--all'])
            elif choice == '2':
                return self.run_ingestion(['--generate-context'])
            elif choice == '3':
                print("\nSelect phase:")
                print("  1. Download")
                print("  2. Extract")
                print("  3. Parse")
                phase = input("Choice (1-3): ").strip()
                phases = {'1': '--download', '2': '--extract', '3': '--parse'}
                if phase in phases:
                    return self.run_ingestion([phases[phase]])
            elif choice == '4':
                return self.launch_ui('studio')
            elif choice == '5':
                return self.launch_ui('runner')
            elif choice == '6':
                return self.launch_ui('interface')
            elif choice == '7':
                return self.launch_ui('collaborate')
            elif choice == '8':
                self.check_status()
            elif choice == '9':
                if PipelineState.clear_state():
                    print("[OK] State cleared")
                else:
                    print("[ERROR] Failed to clear state")
            else:
                print("Invalid choice")


def main():
    """Main entry point"""
    launcher = APEXLauncher()

    parser = argparse.ArgumentParser(
        description='APEX EOR Platform Launcher',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launch.py                        # Interactive menu
  python launch.py status                  # Check platform status
  python launch.py ingest --all            # Run full pipeline
  python launch.py ingest --generate-context  # Generate context only
  python launch.py ui studio                # Launch Agent Studio
  python launch.py ui runner                # Launch automated runner
  python launch.py ui interface             # Launch debug interface
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Status command
    status_parser = subparsers.add_parser('status', help='Check platform status')

    # Ingestion command - accept all remaining arguments
    ingest_parser = subparsers.add_parser('ingest', help='Run data ingestion')

    # UI command
    ui_parser = subparsers.add_parser('ui', help='Launch UI tool')
    ui_parser.add_argument('tool', choices=['studio', 'runner', 'interface'],
                          help='UI tool to launch')

    # Parse known args, allow unknown for ingest command
    args, unknown = parser.parse_known_args()

    # Handle commands
    if args.command == 'status':
        launcher.check_status()
        return 0
    elif args.command == 'ingest':
        # Pass through all unknown arguments to ingestion script
        return launcher.run_ingestion(unknown or ['--help'])
    elif args.command == 'ui':
        return launcher.launch_ui(args.tool)
    else:
        # No command - show interactive menu
        return launcher.interactive_menu()


if __name__ == '__main__':
    sys.exit(main())
