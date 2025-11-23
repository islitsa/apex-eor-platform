"""
UI Code Orchestrator - Coordinates UX Designer + React Developer

This is the coordination layer that:
1. Receives user requirements
2. Has UX Designer create design specification
3. Has React Developer implement the design
4. Returns working React + TypeScript code

This implements Opus's recommendation: separate concerns like physics validators.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import sys
import requests
from enum import Enum
from dataclasses import dataclass

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.agents.ux_designer import UXDesignerAgent, DesignSpec
from src.agents.react_developer import ReactDeveloperAgent
from src.knowledge.design_kb_pinecone import DesignKnowledgeBasePinecone
from src.agents.context.protocol import (
    SessionContext, DiscoveryContext, UserIntent,
    ExecutionContext, TaskType, OutputFormat
)
from src.agents.tools.filter_tool import DataFilterTool
from src.agents.tools.discovery_tool import DataDiscoveryTool
from src.agents.tools.knowledge_tool import KnowledgeTool
# Phase 3: Business logic extraction tools
from src.agents.tools.data_shaping_tool import DataShapingTool
from src.agents.tools.context_assembly_tool import ContextAssemblyTool
from src.agents.tools.knowledge_assembly_tool import KnowledgeAssemblyTool
from src.agents.tools.execution_tool import ExecutionTool
from src.agents.tools.pipeline_assembly_tool import PipelineAssemblyTool


class UICodeOrchestrator:
    """
    Coordinates two specialized agents:
    - UX Designer Agent: Designs WHAT to build
    - React Developer Agent: Implements HOW to build with React + TypeScript

    This orchestrator owns knowledge retrieval - queries Pinecone ONCE
    and passes knowledge to both agents.
    """

    def __init__(self, trace_collector=None, enable_gradient=False, use_agent_mode=False):
        # FIX: Prevent double initialization
        if hasattr(self, 'initialized') and self.initialized:
            return

        print("\n" + "="*80)
        print("TWO-AGENT UI CODE GENERATION SYSTEM")
        print("="*80)
        print("Architecture: UX Designer (Visionary) + React Developer (Implementer)")
        if enable_gradient:
            print("Enhancement: Gradient Context Field enabled (domain-aware pattern boosting)")
        if use_agent_mode:
            print("Mode: AUTONOMOUS AGENT (Phase 4 - LLM-backed reasoning)")
        else:
            print("Mode: Procedural Coordination (Phase 3)")
        print("="*80 + "\n")

        # Mark as initialized
        self.initialized = True

        # Phase 4: Agent mode flag
        self.use_agent_mode = use_agent_mode

        # Initialize knowledge base (orchestrator owns this)
        self.design_kb = DesignKnowledgeBasePinecone()

        # Initialize filter tool (centralized filtering - Phase 1.0)
        self.filter_tool = DataFilterTool()

        # Initialize discovery tool (centralized data fetching - Phase 1.5)
        self.discovery_tool = DataDiscoveryTool(
            filter_tool=self.filter_tool,
            trace_collector=trace_collector
        )

        # Trace collector (optional - for capturing reasoning)
        self.trace_collector = trace_collector

        # Initialize knowledge tool (centralized knowledge retrieval - Phase 1.6)
        # Note: Initialized after gradient_system setup (see below)
        self.knowledge_tool = None

        # Store and initialize gradient system
        self.enable_gradient = enable_gradient
        self.gradient_system = None

        if enable_gradient:
            try:
                # Check if design_kb already has gradient system
                if hasattr(self.design_kb, 'gradient_system'):
                    self.gradient_system = self.design_kb.gradient_system
                    print("[Orchestrator] Using existing Gradient System from KB")
                else:
                    # Initialize new gradient system
                    from src.agents.context.gradient_context import GradientContextSystem
                    self.gradient_system = GradientContextSystem(
                        embedding_model="text-embedding-3-small"
                    )
                    print("[Orchestrator] Initialized new Gradient Context System")
            except Exception as e:
                print(f"[Orchestrator] Warning: Gradient system failed to initialize: {e}")
                print("[Orchestrator] Continuing without gradient context (graceful degradation)")
                self.enable_gradient = False

        # Initialize knowledge tool (Phase 1.6) - after gradient_system is ready
        self.knowledge_tool = KnowledgeTool(
            design_kb=self.design_kb,
            gradient_system=self.gradient_system,
            trace_collector=trace_collector
        )

        # Phase 3: Initialize business logic tools
        self.shaping_tool = DataShapingTool()
        self.context_assembly_tool = ContextAssemblyTool(shaping_tool=self.shaping_tool)
        self.knowledge_assembly_tool = KnowledgeAssemblyTool(knowledge_tool=self.knowledge_tool)
        self.execution_tool = ExecutionTool()

        # Pipeline Assembly Tool (MANDATORY before UX/React generation)
        self.pipeline_assembly_tool = PipelineAssemblyTool(
            data_root="data/raw",
            trace_collector=trace_collector
        )
        print("[Pipeline Assembly] PipelineAssemblyTool initialized")

        # Initialize both agents with trace collector
        # Phase 5: Enable autonomous mode with internal planning loops
        self.ux_designer = UXDesignerAgent(
            trace_collector=trace_collector,
            use_autonomous_mode=True  # Phase 5: Enable autonomous UX agent
        )
        self.react_developer = ReactDeveloperAgent(
            trace_collector=trace_collector,
            styling_framework="tailwind",
            use_autonomous_mode=True  # Phase 5: Enable autonomous React agent
        )

        # Knowledge cache (for potential reuse between iterations)
        self.knowledge_cache = None

        # Phase 6.1: Initialize consistency tools
        from src.agents.tools.design_code_consistency_tool import DesignCodeConsistencyTool
        from src.agents.tools.schema_alignment_tool import SchemaAlignmentTool
        from src.agents.tools.knowledge_conflict_tool import KnowledgeConflictTool
        from src.agents.tools.component_compatibility_tool import ComponentCompatibilityTool

        self.design_code_tool = DesignCodeConsistencyTool()
        self.schema_tool = SchemaAlignmentTool()
        self.knowledge_tool_consistency = KnowledgeConflictTool()
        self.component_tool = ComponentCompatibilityTool()
        print("[Phase 6.1] Consistency tools initialized")

        # Phase 7.1: Build OrchestratorTools bundle for clean dependency injection
        from src.agents.orchestrator_tools_bundle import OrchestratorTools
        self.tools_bundle = OrchestratorTools(
            # Phase 1-2: Data discovery and filtering
            data_discovery=self.discovery_tool,
            data_filter=self.filter_tool,
            data_shaping=self.shaping_tool,
            pipeline_assembly=self.pipeline_assembly_tool,
            # Phase 3: Context and knowledge assembly
            context_assembly=self.context_assembly_tool,
            knowledge=self.knowledge_tool,
            knowledge_assembly=self.knowledge_assembly_tool,
            execution=self.execution_tool,
            # Phase 6.1: Consistency checking
            design_code_consistency=self.design_code_tool,
            schema_alignment=self.schema_tool,
            knowledge_conflict=self.knowledge_tool_consistency,
            component_compatibility=self.component_tool,
            # Optional: trace collector
            trace_collector=trace_collector
        )
        self.tools_bundle.validate()
        print("[Phase 7.1] OrchestratorTools bundle created and validated")

        # Phase 7.3 FIX: Initialize orchestrator agent ONCE here (not in generate_ui_code)
        # This eliminates double initialization bug
        from src.agents.orchestrator_agent import OrchestratorAgent
        self.agent = OrchestratorAgent(
            tools=self.tools_bundle,
            ux_agent=self.ux_designer,
            react_agent=self.react_developer,
            enable_gradient=enable_gradient,
            trace_collector=trace_collector
        )

        if use_agent_mode:
            print("[Orchestrator] Initialized in AUTONOMOUS mode (LLM-backed planning)\n")
        else:
            print("[Orchestrator] Initialized in PROCEDURAL mode (fixed sequence)\n")

    def run_consistency_checks(self, shared_memory, data_context=None, knowledge=None):
        """
        Phase 6.1: Run all 4 consistency tools and update conflicts in memory.

        Args:
            shared_memory: SharedSessionMemory instance
            data_context: Data context from discovery
            knowledge: Knowledge from KB

        Returns:
            Total number of conflicts detected
        """
        print("\n[Phase 6.1] Running consistency checks...")

        all_conflicts = []

        # Tool 1: Design/Code consistency
        print("  [1/4] DesignCodeConsistencyTool...")
        design_code_conflicts = self.design_code_tool.run(
            ux_spec=shared_memory.ux_spec,
            react_files=shared_memory.react_files
        )
        all_conflicts.extend(design_code_conflicts)
        print(f"        Found {len(design_code_conflicts)} conflicts")

        # Tool 2: Schema alignment
        print("  [2/4] SchemaAlignmentTool...")
        schema_conflicts = self.schema_tool.run(
            data_context=data_context or {},
            ux_spec=shared_memory.ux_spec,
            react_files=shared_memory.react_files
        )
        all_conflicts.extend(schema_conflicts)
        print(f"        Found {len(schema_conflicts)} conflicts")

        # Tool 3: Knowledge conflicts
        print("  [3/4] KnowledgeConflictTool...")
        knowledge_conflicts = self.knowledge_tool_consistency.run(
            knowledge=knowledge or {},
            ux_spec=shared_memory.ux_spec,
            react_files=shared_memory.react_files
        )
        all_conflicts.extend(knowledge_conflicts)
        print(f"        Found {len(knowledge_conflicts)} conflicts")

        # Tool 4: Component compatibility
        print("  [4/4] ComponentCompatibilityTool...")
        component_conflicts = self.component_tool.run(
            ux_spec=shared_memory.ux_spec,
            react_files=shared_memory.react_files
        )
        all_conflicts.extend(component_conflicts)
        print(f"        Found {len(component_conflicts)} conflicts")

        # Update SharedMemory with all conflicts
        shared_memory.update_conflicts(all_conflicts)

        print(f"[Phase 6.1] Total conflicts detected: {len(all_conflicts)}")

        # Log conflicts by severity
        by_severity = {}
        for conflict in all_conflicts:
            severity = conflict.severity
            by_severity[severity] = by_severity.get(severity, 0) + 1

        if by_severity:
            print(f"[Phase 6.1] By severity: {by_severity}")

        return len(all_conflicts)

    def generate_ui_code(
        self,
        requirements: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """
        Phase 7.3: Thin wrapper that delegates to existing OrchestratorAgent.

        FIX: NO INITIALIZATION happens here - agent already created in __init__().

        Args:
            requirements: Dict with screen_type, intent, user needs
            context: Additional context (data sources, etc.)

        Returns:
            Generated React files (Dict[str, str])
        """
        print("\n" + "="*80)
        print("UI CODE GENERATION (Phase 7.3 - Delegating to Orchestrator Agent)")
        print("="*80)

        # Step 1: Create shared memory
        from src.agents.shared_memory import SharedSessionMemory
        import uuid
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        shared_memory = SharedSessionMemory(session_id=session_id)
        shared_memory.user_requirements = requirements
        shared_memory.user_context = context
        print(f"[Setup] SharedSessionMemory initialized ({session_id})")

        # Step 2: Emit trace (if enabled)
        if self.trace_collector:
            intent = requirements.get('intent', 'Generate UI')
            self.trace_collector.trace_thinking(
                agent="Orchestrator",
                method="generate_ui_code",
                thought=f"🎯 Starting UI code generation: {intent}"
            )

        # Step 3: Delegate to EXISTING agent (no re-initialization)
        if self.use_agent_mode:
            print("[Delegation] -> OrchestratorAgent.generate_ui_code() (LLM planning)")
            print("[Note] Using existing agent instance (no re-initialization)")
            print("="*80 + "\n")
            return self.agent.generate_ui_code(requirements, context)
        else:
            print("[Delegation] -> OrchestratorAgent.run() (fixed sequence)")
            print("[Note] Using existing agent instance (no re-initialization)")
            print("="*80 + "\n")
            return self.agent.run(requirements, context, shared_memory)

    def generate_navigation_code(
        self,
        base_dashboard_code: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Compatibility method for existing code

        This matches the interface of the old UXCodeGenerator
        """
        # Convert to requirements format
        requirements = {
            'screen_type': 'dashboard_navigation',
            'intent': 'Navigate through data pipeline hierarchy',
            'data_sources': context.get('data_sources', {})
        }

        # Use two-agent system
        navigation_code = self.generate_ui_code(requirements, context)

        # Inject into base code (same as before)
        return self._inject_navigation(base_dashboard_code, navigation_code)

    def _inject_navigation(self, base_code: str, navigation_code: str) -> str:
        """Inject navigation code at placeholder"""
        placeholder = "# NAVIGATION_HANDLER_PLACEHOLDER"

        if placeholder in base_code:
            enhanced_code = base_code.replace(placeholder, navigation_code)
            print("[Orchestrator] Injected navigation code at placeholder")
            return enhanced_code
        else:
            print("[Orchestrator] WARNING: No placeholder found, appending code")
            return base_code + "\n\n" + navigation_code


# Backwards compatibility: Make orchestrator available as UXCodeGenerator
class UXCodeGeneratorV2(UICodeOrchestrator):
    """
    Backwards compatible wrapper for two-agent system

    Existing code can import this as UXCodeGenerator and it will use
    the new two-agent architecture transparently.
    """
    pass


# For testing
if __name__ == "__main__":
    print("Testing Two-Agent System...")

    orchestrator = UICodeOrchestrator()

    # Test requirements
    requirements = {
        'screen_type': 'data_dashboard',
        'intent': 'Monitor petroleum pipeline status',
        'user_goals': ['view data', 'drill down', 'execute pipelines']
    }

    context = {
        'data_sources': {
            'fracfocus': {'datasets': 5},
            'rrc': {'datasets': 3},
            'usgs': {'datasets': 2}
        }
    }

    # Generate code
    code = orchestrator.generate_ui_code(requirements, context)

    print(f"\n\nGenerated {len(code)} characters of code")
    print("\nFirst 500 chars:")
    print(code[:500])