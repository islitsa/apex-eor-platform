"""
Orchestrator Agent - Phase 4

This is the LLM-backed meta-agent that supervises UI code generation.

Instead of a procedural workflow, this agent:
1. Plans what to do next based on current state
2. Chooses skills to execute (tools + sub-agents)
3. Evaluates results
4. Iterates until goal is satisfied
5. Self-corrects when things go wrong

This is the "mind" of the orchestrator.
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import anthropic
import os
import json

# Petroleum domain routing
from src.agents.domain.petroleum_intent_router import route_petroleum_query


class OrchestratorGoal(Enum):
    """High-level goals the orchestrator can pursue"""
    GENERATE_UI = "generate_ui"
    REFINE_UX = "refine_ux"
    FIX_REACT = "fix_react"
    VALIDATE_OUTPUT = "validate_output"
    COMPLETE = "complete"


@dataclass
class SessionMemory:
    """
    Memory structure for the orchestrator agent.

    This tracks everything the orchestrator has done, seen, and decided
    during a UI generation session.
    """
    # Session metadata
    session_id: str
    iteration: int = 0

    # User input
    user_requirements: Dict[str, Any] = field(default_factory=dict)
    user_context: Dict[str, Any] = field(default_factory=dict)

    # Discovered data
    data_context: Optional[Dict] = None
    knowledge: Optional[Dict] = None
    session_ctx: Any = None  # SessionContext object

    # Agent outputs
    design_spec: Any = None  # DesignSpec from UX
    react_files: Any = None  # Dict of files from React

    # Evaluation history
    evaluation_history: List[Dict] = field(default_factory=list)

    # Action history
    actions_taken: List[str] = field(default_factory=list)
    skills_used: List[str] = field(default_factory=list)

    # Error tracking
    errors: List[str] = field(default_factory=list)
    last_error: Optional[str] = None

    # Planning trace
    planning_trace: List[Dict] = field(default_factory=list)

    # Current goal
    current_goal: OrchestratorGoal = OrchestratorGoal.GENERATE_UI

    # Success flags
    ux_satisfactory: bool = False
    react_satisfactory: bool = False
    goal_achieved: bool = False


@dataclass
class Plan:
    """
    A planned action from the orchestrator's reasoning.
    """
    skill: str  # Which skill to call
    reasoning: str  # Why this skill
    arguments: Dict[str, Any] = field(default_factory=dict)
    expected_outcome: str = ""


class OrchestratorAgent:
    """
    Phase 4: LLM-backed meta-agent that supervises UI code generation.

    This agent:
    - Plans what to do next based on current state
    - Chooses from a registry of skills (tools + sub-agents)
    - Evaluates results after each step
    - Iterates until goal is satisfied
    - Self-corrects when things go wrong

    The agent uses chain-of-thought reasoning to decide its next action,
    making the orchestrator truly autonomous and adaptive.
    """

    # Maximum reasoning iterations to prevent infinite loops
    MAX_ITERATIONS = 4

    def __init__(
        self,
        tools: 'OrchestratorTools',
        ux_agent: 'UXDesignerAgent',
        react_agent: 'ReactDeveloperAgent',
        enable_gradient: bool = False,
        model: str = "claude-sonnet-4-20250514",
        trace_collector = None
    ):
        """
        Initialize the orchestrator agent.

        Phase 7.2: Refactored to accept tools bundle and agents directly instead of
        coupling to UICodeOrchestrator. This enables clean dependency injection.

        Args:
            tools: OrchestratorTools bundle with all 11 tools
            ux_agent: UXDesignerAgent instance
            react_agent: ReactDeveloperAgent instance
            enable_gradient: Whether gradient context is enabled
            model: Claude model to use for reasoning
            trace_collector: Optional trace collector for logging
        """
        self.tools = tools
        self.ux_agent = ux_agent
        self.react_agent = react_agent
        self.enable_gradient = enable_gradient
        self.model = model
        self.trace_collector = trace_collector

        # Initialize Claude client
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = anthropic.Anthropic(api_key=api_key)

        # Session memory (reset for each generation request)
        self.memory: Optional[SessionMemory] = None

        # Phase 6.1: Consistency tools are in tools bundle (no need to reinitialize)
        # Phase 7.2: Use tools from bundle instead of creating new instances
        print("[Phase 7.2] Using consistency tools from OrchestratorTools bundle")

        # Build skill registry from tools bundle
        self._build_skill_registry()

        print("[OrchestratorAgent] Initialized with LLM-backed reasoning")
        print(f"  Model: {self.model}")
        print(f"  Skills: {len(self.skills)} available")
        print(f"  Phase 6.1: Consistency tools enabled")
        print(f"  Phase 7.2: Tools injected via OrchestratorTools bundle")


    def _build_skill_registry(self):
        """
        Build the skill registry from Phase 3 tools and agents.

        Skills are callable actions the orchestrator can choose from:
        - Data discovery
        - Knowledge retrieval
        - Context building
        - UX design
        - React generation
        - Validation
        - Filtering
        - etc.
        """
        self.skills = {
            # Data discovery & filtering
            "discover_data": {
                "fn": self._skill_discover_data,
                "description": "Fetch real data from API for specified sources"
            },
            "filter_sources": {
                "fn": self._skill_filter_sources,
                "description": "Filter data sources based on user intent"
            },
            "assemble_pipelines": {
                "fn": self._skill_assemble_pipelines,
                "description": "MANDATORY: Assemble pipelines with stage detection (MUST run before UX/React)"
            },

            # Knowledge & context
            "retrieve_knowledge": {
                "fn": self._skill_retrieve_knowledge,
                "description": "Retrieve UX patterns and knowledge from vector DB"
            },
            "build_session_context": {
                "fn": self._skill_build_session_context,
                "description": "Build SessionContext from requirements and data"
            },
            "prepare_builder_context": {
                "fn": self._skill_prepare_builder_context,
                "description": "Prepare enhanced context for React Developer"
            },

            # UX design
            "generate_ux": {
                "fn": self._skill_generate_ux,
                "description": "Call UX Designer to create design specification"
            },
            "refine_ux": {
                "fn": self._skill_refine_ux,
                "description": "Refine UX design based on evaluation feedback"
            },
            "validate_ux": {
                "fn": self._skill_validate_ux,
                "description": "Evaluate UX design specification for correctness"
            },

            # React generation
            "generate_react": {
                "fn": self._skill_generate_react,
                "description": "Call React Developer to generate code"
            },
            "regenerate_react": {
                "fn": self._skill_regenerate_react,
                "description": "Regenerate React code with corrections"
            },
            "validate_react": {
                "fn": self._skill_validate_react,
                "description": "Evaluate React code output for correctness"
            },

            # Meta-actions
            "evaluate_progress": {
                "fn": self._skill_evaluate_progress,
                "description": "Evaluate overall progress toward goal"
            },
            "finish": {
                "fn": self._skill_finish,
                "description": "Mark goal as achieved and return final output"
            }
        }

    # ========================================
    # SKILL IMPLEMENTATIONS
    # ========================================

    def _skill_discover_data(self, **kwargs) -> Dict:
        """
        Discover data from API.

        Phase 7.2: Uses tools.data_discovery instead of orchestrator.discovery_tool
        """
        filter_sources = kwargs.get('filter_sources', None)
        self.memory.data_context = self.tools.data_discovery.fetch_data_context(
            filter_sources=filter_sources
        )
        return {"success": self.memory.data_context.get('success', False)}

    def _skill_assemble_pipelines(self, **kwargs) -> Dict:
        """
        Assemble pipelines with stage detection.

        CRITICAL: This MUST run after discovery and BEFORE UX/React generation.

        This skill:
        1. Takes data_context from discovery
        2. Calls PipelineAssemblyTool to detect stages from filesystem
        3. Updates data_context with assembled pipelines
        4. Propagates to shared_memory for UX/React agents

        Without this step, React Developer will receive incomplete data!
        """
        if not self.memory.data_context:
            error = "No data_context available for pipeline assembly"
            print(f"  [ERROR] {error}")
            return {"success": False, "error": error}

        # Call PipelineAssemblyTool to assemble pipelines with stage detection
        pipelines = self.tools.pipeline_assembly.assemble_pipelines(
            data_context=self.memory.data_context
        )

        # Update data_context with assembled pipelines
        self.memory.data_context = self.tools.pipeline_assembly.update_data_context_with_pipelines(
            data_context=self.memory.data_context,
            pipelines=pipelines
        )

        # CRITICAL: Propagate to shared_memory so UX/React agents can access it
        if hasattr(self, 'shared_memory') and self.shared_memory:
            self.shared_memory.data_context = self.memory.data_context
            print(f"  [OK] Pipelines propagated to shared_memory for UX/React agents")

        print(f"  [OK] Pipeline assembly complete: {len(pipelines)} pipelines with stages")

        return {
            "success": True,
            "pipelines_count": len(pipelines)
        }

    def _skill_filter_sources(self, **kwargs) -> Dict:
        """
        Filter data sources based on intent.

        Phase 7.2: Uses tools.data_filter instead of orchestrator.filter_tool
        """
        intent = self.memory.user_requirements.get('intent', '')
        all_sources = list(self.memory.user_context.get('data_sources', {}).keys())
        filtered = self.tools.data_filter.filter_by_prompt(intent, all_sources)
        return {"filtered_sources": filtered}

    def _skill_retrieve_knowledge(self, **kwargs) -> Dict:
        """
        Retrieve knowledge from vector DB.

        Phase 7.2: Uses tools.knowledge_assembly instead of orchestrator.knowledge_assembly_tool
        """
        self.memory.knowledge = self.tools.knowledge_assembly.retrieve_and_assemble_knowledge(
            data_context=self.memory.data_context or {},
            enable_gradient=self.enable_gradient
        )
        return {"success": self.memory.knowledge is not None}

    def _skill_build_session_context(self, **kwargs) -> Dict:
        """
        Build SessionContext.

        Phase 7.2: Uses tools.context_assembly instead of orchestrator.context_assembly_tool
        """
        self.memory.session_ctx = self.tools.context_assembly.build_session_context(
            requirements=self.memory.user_requirements,
            data_context=self.memory.data_context or {},
            knowledge=self.memory.knowledge or {}
        )
        return {"success": self.memory.session_ctx is not None}

    def _skill_prepare_builder_context(self, **kwargs) -> Dict:
        """
        Prepare builder context for React.

        Phase 7.2: Uses tools.context_assembly and tools.data_filter
        """
        enhanced_context = self.tools.context_assembly.prepare_builder_context(
            requirements=self.memory.user_requirements,
            context=self.memory.user_context,
            data_context=self.memory.data_context or {},
            filter_tool=self.tools.data_filter
        )
        return {"enhanced_context": enhanced_context}

    def _skill_generate_ux(self, **kwargs) -> Dict:
        """
        Generate UX design specification.

        Phase 5: Uses SharedSessionMemory and autonomous UX agent.
        Phase 6.2: Uses single shared memory instance across all agents.
        Phase 7.2: Uses self.ux_agent and self.tools.knowledge_assembly
        """
        # Phase 6.2: Use the single SharedSessionMemory instance
        shared_memory = self.shared_memory

        # Populate data context if available
        if self.memory.data_context:
            shared_memory.data_context = self.memory.data_context

        # Phase 6.2: Populate knowledge from tools.knowledge_assembly
        if self.memory.knowledge:
            design_knowledge = self.tools.knowledge_assembly.assemble_ux_knowledge(
                knowledge=self.memory.knowledge,
                data_context=self.memory.data_context or {}
            )
            shared_memory.knowledge = design_knowledge
            print("[Phase 6.2] Knowledge propagated to UX agent")

        # Call autonomous UX agent (Phase 5)
        try:
            design_spec = self.ux_agent.run(shared_memory, max_steps=3)

            # Update orchestrator memory
            self.memory.design_spec = design_spec
            self.memory.ux_satisfactory = shared_memory.ux_satisfactory

            print(f"[Phase 6.2] UX spec written to shared memory (version {shared_memory.ux_spec_version})")

            return {"success": design_spec is not None, "error": None}
        except Exception as e:
            error = f"UX generation error: {str(e)}"
            self.memory.errors.append(error)
            self.memory.last_error = error
            return {"success": False, "error": error}

    def _skill_refine_ux(self, **kwargs) -> Dict:
        """Refine UX design with feedback"""
        # TODO: Implement UX refinement with specific feedback
        return self._skill_generate_ux(**kwargs)

    def _skill_validate_ux(self, **kwargs) -> Dict:
        """
        Validate UX design specification.

        Phase 7.2: Validation logic simplified (UX agent already validates internally)
        """
        # Phase 7.2: UX agent validates internally during run()
        # We can check shared_memory.ux_satisfactory flag
        satisfactory = self.shared_memory.ux_satisfactory if hasattr(self, 'shared_memory') else False

        self.memory.evaluation_history.append({
            "type": "ux",
            "iteration": self.memory.iteration,
            "satisfactory": satisfactory,
            "issues": []
        })

        self.memory.ux_satisfactory = satisfactory

        return {
            "satisfactory": satisfactory,
            "issues": []
        }

    def _skill_generate_react(self, **kwargs) -> Dict:
        """
        Generate React code.

        Phase 5: Uses SharedSessionMemory and autonomous React agent.
        Phase 6.1: Runs consistency checks after generation.
        Phase 6.2: Uses single shared memory instance (UX spec already available).
        """
        # Phase 6.2: Use the single SharedSessionMemory instance
        shared_memory = self.shared_memory

        # Phase 6.2: UX spec should already be in shared memory from UX agent
        if not shared_memory.ux_spec:
            error = "No UX design spec available in shared memory for React generation"
            self.memory.errors.append(error)
            return {"success": False, "error": error}

        print(f"[Phase 6.2] React agent reading UX spec from shared memory (version {shared_memory.ux_spec_version})")

        # --- SAFETY CHECK A3: UX interaction_model must exist ---
        interaction_model = getattr(shared_memory.ux_spec, "interaction_model", None)
        if not interaction_model:
            error = "UX Designer produced empty interaction_model — cannot generate React code"
            self.memory.errors.append(error)
            print(f"[HARD FAIL] {error}")
            return {"success": False, "error": error}

        # Prepare React-specific knowledge
        # Phase 7.2: Use self.tools.knowledge_assembly instead of orchestrator.knowledge_assembly_tool
        if self.memory.knowledge:
            enhanced_context = self.tools.knowledge_assembly.assemble_react_knowledge(
                knowledge=self.memory.knowledge,
                data_context=self.memory.data_context or {},
                enhanced_context=self.memory.user_context
            )
            shared_memory.knowledge = enhanced_context
            print("[Phase 6.2] Knowledge propagated to React agent")

        # Call autonomous React agent (Phase 5)
        # Phase 7.2: Use self.react_agent instead of orchestrator.react_developer
        try:
            react_files = self.react_agent.run(shared_memory, max_steps=3)

            # Update orchestrator memory
            self.memory.react_files = react_files
            self.memory.react_satisfactory = shared_memory.react_satisfactory

            print(f"[Phase 6.2] React files written to shared memory (version {shared_memory.react_version})")

            # --- SAFETY CHECK A2: HARD FAIL ON MOCK DATA ---
            if react_files and self._contains_mock_data(react_files):
                # Erase bad output so next iteration doesn't use it
                shared_memory.react_files = None
                self.memory.react_files = None
                error = "Mock data detected in React output — regeneration required"
                self.memory.errors.append(error)
                print(f"[HARD FAIL] {error}")
                return {"success": False, "error": error}

            # --- SAFETY CHECK A4: STRUCTURAL + BEHAVIORAL VALIDATION ---
            if react_files:
                validation_errors = self._validate_react_output(react_files)
                if validation_errors:
                    print(f"\n[VALIDATION] Found {len(validation_errors)} issues in React output:")
                    for err in validation_errors:
                        print(f"  - {err}")

                    # Log but don't hard-fail (let consistency checks handle severity)
                    for err in validation_errors:
                        self.memory.errors.append(f"[VALIDATION] {err}")

                    # For critical issues, hard-fail
                    critical_patterns = [
                        "Wrong endpoint",
                        "Wrong parameter",
                        "Missing onFileSelect",
                    ]
                    critical_errors = [e for e in validation_errors
                                       if any(p in e for p in critical_patterns)]

                    if critical_errors:
                        shared_memory.react_files = None
                        self.memory.react_files = None
                        error = f"Critical validation errors in React output: {critical_errors[0]}"
                        print(f"[HARD FAIL] {error}")
                        return {"success": False, "error": error}
                else:
                    print("[VALIDATION] React output passed structural + behavioral checks")

            # --- SAFETY CHECK A5: TYPESCRIPT COMPILATION GATE ---
            # This catches type errors that static analysis misses
            if react_files:
                ts_errors = self._typecheck_react_output(react_files)
                if ts_errors:
                    print(f"\n[TYPECHECK] Found {len(ts_errors)} TypeScript errors:")
                    for err in ts_errors[:5]:
                        print(f"  - {err}")

                    # Log errors but don't hard-fail (allow user to fix)
                    for err in ts_errors[:10]:
                        self.memory.errors.append(f"[TYPECHECK] {err}")

                    # Hard-fail on critical type errors
                    critical_ts_patterns = [
                        "Cannot read properties of undefined",
                        "is not assignable to type",
                        "Property .* does not exist on type",
                    ]
                    import re
                    critical_ts_errors = [
                        e for e in ts_errors
                        if any(re.search(p, e) for p in critical_ts_patterns)
                    ]

                    if critical_ts_errors:
                        shared_memory.react_files = None
                        self.memory.react_files = None
                        error = f"TypeScript errors in React output: {critical_ts_errors[0][:100]}"
                        print(f"[HARD FAIL] {error}")
                        return {"success": False, "error": error}

            # Phase 6.1: Run consistency checks now that we have both UX and React
            if react_files and shared_memory.ux_spec:
                print("\n[Phase 6.1] Running consistency checks after React generation...")
                num_conflicts = self.run_consistency_checks(shared_memory)

                # Phase 6.2: If conflicts detected, run convergence loop
                if num_conflicts > 0:
                    print(f"[Phase 6.1] Detected {num_conflicts} conflicts - logged to memory")
                    print(f"[Phase 6.2] Starting mediator convergence loop...")

                    convergence_result = self._run_convergence_loop(shared_memory, max_iterations=3)

                    if convergence_result["converged"]:
                        print(f"[Phase 6.2] CONVERGENCE ACHIEVED: {convergence_result['reason']}")
                        print(f"  Iterations: {convergence_result['iterations']}")
                        print(f"  Final conflicts: {convergence_result['final_conflict_count']}")
                    else:
                        print(f"[Phase 6.2] CONVERGENCE FAILED: {convergence_result['reason']}")
                        print(f"  Iterations: {convergence_result['iterations']}")
                        print(f"  Remaining conflicts: {convergence_result['final_conflict_count']}")
                else:
                    print("[Phase 6.1] No conflicts detected - output is consistent!")

            return {"success": react_files is not None, "error": None}
        except Exception as e:
            error = f"React generation error: {str(e)}"
            self.memory.errors.append(error)
            self.memory.last_error = error
            return {"success": False, "error": error}

    def _skill_regenerate_react(self, **kwargs) -> Dict:
        """Regenerate React code with corrections"""
        # TODO: Implement React regeneration with specific fixes
        return self._skill_generate_react(**kwargs)

    def _skill_validate_react(self, **kwargs) -> Dict:
        """
        Validate React code output.

        Phase 7.2: Validation logic simplified (React agent already validates internally)
        """
        # Phase 7.2: React agent validates internally during run()
        # We can check shared_memory.react_satisfactory flag
        satisfactory = self.shared_memory.react_satisfactory if hasattr(self, 'shared_memory') else False

        self.memory.evaluation_history.append({
            "type": "react",
            "iteration": self.memory.iteration,
            "satisfactory": satisfactory,
            "issues": []
        })

        self.memory.react_satisfactory = satisfactory

        return {
            "satisfactory": satisfactory,
            "issues": []
        }

    def _skill_evaluate_progress(self, **kwargs) -> Dict:
        """Evaluate overall progress toward goal"""
        progress = {
            "has_data": self.memory.data_context is not None,
            "has_knowledge": self.memory.knowledge is not None,
            "has_session_context": self.memory.session_ctx is not None,
            "has_ux": self.memory.design_spec is not None,
            "has_react": self.memory.react_files is not None,
            "ux_valid": self.memory.ux_satisfactory,
            "react_valid": self.memory.react_satisfactory,
            "iteration": self.memory.iteration,
            "errors": len(self.memory.errors)
        }

        # Determine if goal is achieved
        goal_achieved = (
            progress["has_data"] and
            progress["has_ux"] and
            progress["has_react"] and
            progress["ux_valid"] and
            progress["react_valid"]
        )

        self.memory.goal_achieved = goal_achieved

        return progress

    def _skill_finish(self, **kwargs) -> Dict:
        """Mark goal as achieved"""
        self.memory.goal_achieved = True
        self.memory.current_goal = OrchestratorGoal.COMPLETE
        return {"finished": True}

    # ========================================
    # SAFETY HELPERS
    # ========================================

    def _contains_mock_data(self, files: Dict[str, str]) -> bool:
        """
        Detect mock/hardcoded data in React output.

        Returns True if any file contains patterns indicating mock data.
        This is a HARD FAIL condition - mock data must never ship.

        NOTE: Be careful not to flag legitimate patterns like:
        - Stage/status configuration arrays
        - Menu items and navigation config
        - Column definitions for tables
        - Default state with empty arrays
        """
        import re

        # Patterns that ALWAYS indicate mock data
        mock_patterns = [
            r"\bMOCK\b",                             # explicit MOCK keyword (word boundary)
            r"\bfake\w*\b",                          # fake, fakeData, etc.
            r"\bdummy\w*\b",                         # dummy, dummyData, etc.
            r"sample\s*(data|records|rows|items)",   # sample data/records/rows
            r"\bhardcode[d]?\b",                     # hardcode/hardcoded
            r"const\s+(mock|fake|dummy|test)\w*\s*=",  # explicit mock variable names
            r"(mock|fake|dummy|test)(Data|Items|Records|List)\s*=",  # mockData, fakeItems, etc.
            r"TODO.*real\s*data",                    # TODO: replace with real data
            r"//.*mock",                             # comments mentioning mock
        ]

        # Patterns that are ALLOWED (legitimate config/state)
        # These are NOT mock data:
        # - const stages = [{ id: 'raw', ... }]  <- stage config
        # - const columns = [{ field: 'name', ... }] <- table config
        # - useState<Pipeline[]>([]) <- empty default state
        # - const menuItems = [{ label: 'Home', ... }] <- nav config

        for filename, content in files.items():
            # Skip non-code files
            if not filename.endswith(('.tsx', '.ts', '.jsx', '.js')):
                continue

            for pattern in mock_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    print(f"[MOCK DETECTED] Pattern '{pattern}' found in {filename}")
                    return True

        return False

    def _validate_react_output(self, files: Dict[str, str]) -> List[str]:
        """
        Validate generated React code for structural and behavioral correctness.

        This catches common LLM hallucination issues:
        - Wrong API endpoints
        - Wrong parameter names
        - Missing component wiring
        - Unused hooks

        Returns:
            List of error messages (empty if valid)
        """
        import re
        errors = []

        # ========================================
        # STRUCTURAL VALIDATION
        # ========================================

        # Check dataHooks.tsx has correct endpoint
        data_hooks_files = [f for f in files if 'dataHooks' in f or 'hooks' in f.lower()]
        for fname in data_hooks_files:
            content = files[fname]

            # Check for wrong preview endpoint
            if '/preview?' in content and '/files/preview?' not in content:
                errors.append(f"{fname}: Wrong endpoint - using /preview instead of /files/preview")

            # Check for wrong parameter name
            if 'limit=' in content or 'limit:' in content:
                if 'page_size' not in content:
                    errors.append(f"{fname}: Wrong parameter - using 'limit' instead of 'page_size'")

            # Check for wrong response property (snake_case vs camelCase)
            if 'total_rows' in content and 'totalRows' not in content:
                errors.append(f"{fname}: Wrong property - using 'total_rows' instead of 'totalRows'")

        # Check FileExplorer components have onFileSelect
        for fname, content in files.items():
            if 'FileExplorer' in fname or 'FileTree' in fname:
                if 'onFileSelect' not in content:
                    errors.append(f"{fname}: Missing onFileSelect callback prop")

        # ========================================
        # BEHAVIORAL VALIDATION
        # ========================================

        # Check that file selection is wired to preview
        for fname, content in files.items():
            if not fname.endswith(('.tsx', '.ts')):
                continue

            # If component uses FileExplorerTree, it should also use useFilePreview or handle selection
            if 'FileExplorerTree' in content or '<FileExplorer' in content:
                has_file_select_handler = 'onFileSelect' in content and ('setSelectedFile' in content or 'handleFileSelect' in content)
                has_preview_hook = 'useFilePreview' in content

                if has_file_select_handler and not has_preview_hook:
                    # Only warn if there's selection but no preview
                    if 'selectedFile' in content:
                        errors.append(f"{fname}: Has file selection state but doesn't use useFilePreview hook")

            # Check for unused hooks (defined but return value not used)
            if 'usePipelines()' in content:
                if '{ data' not in content and '{data' not in content:
                    errors.append(f"{fname}: usePipelines() called but return value not destructured")

        # ========================================
        # API CONTRACT VALIDATION
        # ========================================

        # Check for common wrong endpoints
        wrong_endpoints = [
            (r'/api/pipelines/[^/]+/data\b', '/api/pipelines/{id}/data does not exist'),
            (r'/api/pipelines/[^/]+/preview\?', '/api/pipelines/{id}/preview should be /files/preview'),
        ]

        for fname, content in files.items():
            if not fname.endswith(('.tsx', '.ts')):
                continue

            for pattern, msg in wrong_endpoints:
                if re.search(pattern, content):
                    errors.append(f"{fname}: {msg}")

        return errors

    def _typecheck_react_output(self, files: Dict[str, str], base_dir: str = None) -> List[str]:
        """
        Layer 5: Run TypeScript compiler to catch type errors.

        This catches errors that static validation misses:
        - Missing optional chaining (?.)
        - Accessing non-existent properties
        - Type mismatches between files
        - Unused imports

        Args:
            files: Dict of filename -> content
            base_dir: Optional base directory with tsconfig.json and node_modules

        Returns:
            List of TypeScript error messages (empty if clean)
        """
        import subprocess
        import os
        import tempfile
        import shutil
        from pathlib import Path

        # Use existing generated_react_dashboard if it exists (has node_modules)
        project_root = Path(__file__).parent.parent.parent
        existing_dir = project_root / "generated_react_dashboard"

        if existing_dir.exists() and (existing_dir / "node_modules").exists():
            output_dir = str(existing_dir)
            use_temp = False
            print(f"  [TypeCheck] Using existing project at {output_dir}")
        elif base_dir and Path(base_dir).exists():
            output_dir = base_dir
            use_temp = False
        else:
            # No existing project, skip typecheck
            print("  [TypeCheck] No existing project with node_modules, skipping")
            return []

        # Write generated files to the directory
        try:
            print(f"  [TypeCheck] Writing {len(files)} files for type checking...")
            for filename, content in files.items():
                filepath = Path(output_dir) / filename
                filepath.parent.mkdir(parents=True, exist_ok=True)
                filepath.write_text(content, encoding='utf-8')

            # Check if tsconfig.json exists
            tsconfig_path = os.path.join(output_dir, "tsconfig.json")
            if not os.path.exists(tsconfig_path):
                print(f"  [TypeCheck] No tsconfig.json found, skipping")
                return []

            print(f"  [TypeCheck] Running tsc --noEmit...")

            result = subprocess.run(
                ["npx", "tsc", "--noEmit"],
                cwd=output_dir,
                capture_output=True,
                text=True,
                timeout=60,
                shell=True  # Required for Windows
            )

            if result.returncode == 0:
                print("  [TypeCheck] ✅ No TypeScript errors")
                return []

            # Parse errors from stdout (tsc outputs errors to stdout, not stderr)
            output = result.stdout + result.stderr
            errors = []

            for line in output.split('\n'):
                line = line.strip()
                # TypeScript errors look like: "src/App.tsx(77,30): error TS2339: ..."
                if 'error TS' in line or 'Error:' in line:
                    errors.append(line)

            print(f"  [TypeCheck] ❌ Found {len(errors)} TypeScript errors")
            for err in errors[:5]:  # Show first 5
                print(f"    - {err[:100]}...")

            return errors

        except subprocess.TimeoutExpired:
            print("  [TypeCheck] ⚠️ TypeScript check timed out")
            return ["TypeScript check timed out after 60s"]
        except FileNotFoundError:
            print("  [TypeCheck] ⚠️ npx/tsc not found, skipping typecheck")
            return []
        except Exception as e:
            print(f"  [TypeCheck] ⚠️ TypeScript check failed: {e}")
            return [f"TypeScript check failed: {str(e)}"]

    # ========================================
    # PHASE 6.1: CONSISTENCY CHECKING
    # ========================================

    def run_consistency_checks(self, shared_memory: 'SharedSessionMemory'):
        """
        Phase 6.1: Run all 4 consistency tools and update conflicts in memory.

        This method:
        1. Runs all consistency tools
        2. Collects all conflicts
        3. Updates SharedMemory with new conflicts
        4. Logs conflicts for debugging

        Args:
            shared_memory: SharedSessionMemory instance

        Returns:
            Total number of conflicts detected
        """
        print("\n[Phase 6.1] Running consistency checks...")

        all_conflicts = []

        # Tool 1: Design/Code consistency
        # Phase 7.2: Use tools from bundle instead of self.design_code_tool
        print("  [1/4] DesignCodeConsistencyTool...")
        design_code_conflicts = self.tools.design_code_consistency.run(
            ux_spec=shared_memory.ux_spec,
            react_files=shared_memory.react_files
        )
        all_conflicts.extend(design_code_conflicts)
        print(f"        Found {len(design_code_conflicts)} conflicts")

        # Tool 2: Schema alignment
        print("  [2/4] SchemaAlignmentTool...")
        schema_conflicts = self.tools.schema_alignment.run(
            data_context=shared_memory.data_context or {},
            ux_spec=shared_memory.ux_spec,
            react_files=shared_memory.react_files
        )
        all_conflicts.extend(schema_conflicts)
        print(f"        Found {len(schema_conflicts)} conflicts")

        # Tool 3: Knowledge conflicts
        print("  [3/4] KnowledgeConflictTool...")
        knowledge_conflicts = self.tools.knowledge_conflict.run(
            knowledge=shared_memory.knowledge or {},
            ux_spec=shared_memory.ux_spec,
            react_files=shared_memory.react_files
        )
        all_conflicts.extend(knowledge_conflicts)
        print(f"        Found {len(knowledge_conflicts)} conflicts")

        # Tool 4: Component compatibility
        print("  [4/4] ComponentCompatibilityTool...")
        component_conflicts = self.tools.component_compatibility.run(
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

    # ========================================
    # PHASE 6.2: MEDIATOR CONVERGENCE LOGIC
    # ========================================

    def _run_convergence_loop(self, shared_memory: 'SharedSessionMemory', max_iterations: int = 3):
        """
        Phase 6.2: Mediator convergence loop.

        After initial React generation, if conflicts exist, this loop:
        1. Asks agents to address conflicts
        2. Re-runs consistency checks
        3. Continues until convergence or max iterations

        Convergence criteria:
        - No high-severity conflicts remain, OR
        - Consecutive iterations with same conflict count (stalemate), OR
        - Max iterations reached

        Args:
            shared_memory: SharedSessionMemory instance
            max_iterations: Maximum negotiation iterations (default 3)

        Returns:
            Dict with convergence status
        """
        print("\n" + "="*80)
        print("[Phase 6.2] MEDIATOR CONVERGENCE LOOP")
        print("="*80)

        iteration = 0
        previous_conflict_count = len(shared_memory.design_conflicts) + len(shared_memory.implementation_conflicts)

        # Track convergence
        stalemate_count = 0
        max_stalemate = 2  # If conflict count doesn't change for 2 iterations, stop

        while iteration < max_iterations:
            iteration += 1
            print(f"\n[Phase 6.2] Convergence iteration {iteration}/{max_iterations}")

            # Get current conflicts
            total_conflicts = len(shared_memory.design_conflicts) + len(shared_memory.implementation_conflicts)
            high_severity = sum(1 for c in (shared_memory.design_conflicts + shared_memory.implementation_conflicts)
                              if c.severity == "high")

            print(f"  Current state: {total_conflicts} total conflicts, {high_severity} high-severity")

            # Check convergence criteria
            if total_conflicts == 0:
                print("[Phase 6.2] CONVERGED: No conflicts remaining")
                shared_memory.consecutive_agreements += 1
                return {
                    "converged": True,
                    "reason": "no_conflicts",
                    "iterations": iteration,
                    "final_conflict_count": 0
                }

            if high_severity == 0 and total_conflicts <= 3:
                print("[Phase 6.2] CONVERGED: Only low-severity conflicts remain")
                shared_memory.consecutive_agreements += 1
                return {
                    "converged": True,
                    "reason": "acceptable_quality",
                    "iterations": iteration,
                    "final_conflict_count": total_conflicts
                }

            # Check for stalemate (conflict count not changing)
            if total_conflicts == previous_conflict_count:
                stalemate_count += 1
                print(f"  Stalemate detected ({stalemate_count}/{max_stalemate}): conflict count unchanged")
                if stalemate_count >= max_stalemate:
                    print("[Phase 6.2] STALEMATE: Conflict count not decreasing")
                    return {
                        "converged": False,
                        "reason": "stalemate",
                        "iterations": iteration,
                        "final_conflict_count": total_conflicts
                    }
            else:
                stalemate_count = 0  # Reset if progress is made

            # Attempt resolution: Ask agents to address conflicts
            print(f"\n  [Phase 6.2] Attempting conflict resolution...")

            # Identify which agent should address conflicts
            design_conflicts = len(shared_memory.design_conflicts)
            impl_conflicts = len(shared_memory.implementation_conflicts)

            if impl_conflicts > 0:
                # React agent should fix implementation conflicts
                print(f"    Asking React agent to address {impl_conflicts} implementation conflicts")

                # Create a change request for React agent
                from src.agents.shared_memory import ChangeRequest
                change_req = ChangeRequest(
                    from_agent="Mediator",
                    to_agent="ReactDeveloper",
                    description=f"Fix {impl_conflicts} implementation conflicts",
                    suggested_action="Review conflicts and regenerate components",
                    priority="high"
                )
                shared_memory.add_change_request(change_req)

                # FIX: Don't call run() again - just execute conflict resolution skill
                # Phase 7.2: Use self.react_agent instead of orchestrator.react_developer
                try:
                    print("    Asking React agent to resolve conflicts (not regenerate)...")

                    # Call the resolve_conflicts skill directly instead of full run()
                    # This prevents duplicate initialization and generation
                    if hasattr(self.react_agent, '_skill_resolve_conflicts'):
                        result = self.react_agent._skill_resolve_conflicts(shared_memory, {})
                        if result.get('success'):
                            shared_memory.react_version += 1
                            print(f"    Conflicts resolved (React version {shared_memory.react_version})")
                        else:
                            print(f"    Conflict resolution returned no changes")
                    else:
                        # Fallback for older React agent versions
                        print("    Warning: resolve_conflicts skill not available, skipping")
                except Exception as e:
                    print(f"    Conflict resolution failed: {e}")
                    # Continue to next iteration

            elif design_conflicts > 0:
                # UX agent should fix design conflicts
                print(f"    Asking UX agent to address {design_conflicts} design conflicts")

                from src.agents.shared_memory import ChangeRequest
                change_req = ChangeRequest(
                    from_agent="Mediator",
                    to_agent="UXDesigner",
                    description=f"Fix {design_conflicts} design conflicts",
                    suggested_action="Review conflicts and refine spec",
                    priority="high"
                )
                shared_memory.add_change_request(change_req)

                # FIX: Don't call run() again - just execute conflict resolution skill
                # Phase 7.2: Use self.ux_agent instead of orchestrator.ux_designer
                try:
                    print("    Asking UX agent to refine design (not regenerate)...")

                    # Call the address_conflicts skill directly instead of full run()
                    if hasattr(self.ux_agent, '_skill_address_conflicts'):
                        result = self.ux_agent._skill_address_conflicts(shared_memory, {})
                        if result.get('success'):
                            shared_memory.ux_spec_version += 1
                            print(f"    Design refined (UX version {shared_memory.ux_spec_version})")
                        else:
                            print(f"    Design refinement returned no changes")
                    else:
                        # Fallback for older UX agent versions
                        print("    Warning: address_conflicts skill not available, skipping")
                except Exception as e:
                    print(f"    Design refinement failed: {e}")

            # Re-run consistency checks
            print(f"\n  Re-running consistency checks after iteration {iteration}...")
            new_conflict_count = self.run_consistency_checks(shared_memory)

            # Update tracking
            previous_conflict_count = new_conflict_count
            shared_memory.iterations_since_last_change += 1

            # Log progress
            if new_conflict_count < total_conflicts:
                print(f"  [OK] Progress: {total_conflicts} -> {new_conflict_count} conflicts")
                shared_memory.iterations_since_last_change = 0  # Reset since we made progress
            else:
                print(f"  [WARN] No progress: still {new_conflict_count} conflicts")

        # Max iterations reached
        print(f"\n[Phase 6.2] MAX ITERATIONS REACHED ({max_iterations})")
        final_count = len(shared_memory.design_conflicts) + len(shared_memory.implementation_conflicts)
        return {
            "converged": False,
            "reason": "max_iterations",
            "iterations": iteration,
            "final_conflict_count": final_count
        }

    # ========================================
    # PLANNING MODULE (LLM REASONING)
    # ========================================

    def _plan_next_action(self) -> Plan:
        """
        Use LLM to decide the next action based on current state.

        This is the "brain" of the orchestrator agent.
        """
        # Build planning prompt
        prompt = self._build_planning_prompt()

        # Call Claude for reasoning
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            temperature=0.0,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # Parse response
        response_text = response.content[0].text

        # Log planning trace
        self.memory.planning_trace.append({
            "iteration": self.memory.iteration,
            "prompt": prompt[:500] + "...",  # Truncate for logging
            "response": response_text
        })

        # Extract plan from response
        plan = self._parse_plan(response_text)

        # Trace the decision
        if self.trace_collector:
            self.trace_collector.trace_thinking(
                agent="OrchestratorAgent",
                method="Planning",
                thought=f"[PLAN] {plan.skill}: {plan.reasoning}"
            )

        print(f"\n[OrchestratorAgent] Planning iteration {self.memory.iteration}")
        print(f"  Chosen skill: {plan.skill}")
        print(f"  Reasoning: {plan.reasoning}")

        return plan

    def _build_planning_prompt(self) -> str:
        """
        Build the planning prompt for the LLM.

        This prompt gives the LLM all the context it needs to decide
        what to do next.
        """
        # Build state summary
        state_summary = {
            "iteration": self.memory.iteration,
            "goal": self.memory.current_goal.value,
            "has_data": self.memory.data_context is not None,
            "has_knowledge": self.memory.knowledge is not None,
            "has_session_context": self.memory.session_ctx is not None,
            "has_ux_design": self.memory.design_spec is not None,
            "has_react_code": self.memory.react_files is not None,
            "ux_validated": self.memory.ux_satisfactory,
            "react_validated": self.memory.react_satisfactory,
            "recent_errors": self.memory.errors[-3:] if self.memory.errors else [],
            "actions_taken": self.memory.actions_taken[-5:] if self.memory.actions_taken else []
        }

        # Get recent evaluation
        recent_eval = self.memory.evaluation_history[-1] if self.memory.evaluation_history else None

        # Build skill descriptions
        skill_descriptions = "\n".join([
            f"- {name}: {info['description']}"
            for name, info in self.skills.items()
        ])

        prompt = f"""You are the OrchestratorAgent supervising UI code generation.

**Your Goal:** {self.memory.current_goal.value}

**Current State:**
{json.dumps(state_summary, indent=2)}

**Recent Evaluation:**
{json.dumps(recent_eval, indent=2) if recent_eval else "None"}

**Available Skills:**
{skill_descriptions}

**Instructions:**
1. Analyze the current state
2. Determine what needs to happen next to achieve the goal
3. Choose the most appropriate skill to call
4. Provide clear reasoning for your choice

**Decision Rules:**
- If no data context: call "discover_data"
- If no knowledge: call "retrieve_knowledge"
- If no session context: call "build_session_context"
- If no UX design: call "generate_ux"
- If UX invalid: call "refine_ux" or "generate_ux" again
- If no React code: call "generate_react"
- If React invalid: call "regenerate_react"
- If both UX and React valid: call "finish"
- Max {self.MAX_ITERATIONS} iterations

**Your response MUST be valid JSON in this exact format:**
{{
  "skill": "<skill_name>",
  "reasoning": "<why this skill is needed now>",
  "arguments": {{}},
  "expected_outcome": "<what should happen>"
}}

Return ONLY the JSON, no other text."""

        return prompt

    def _parse_plan(self, response_text: str) -> Plan:
        """Parse the LLM's response into a Plan object"""
        try:
            # Try to extract JSON from response
            response_text = response_text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1])

            plan_dict = json.loads(response_text)

            return Plan(
                skill=plan_dict.get("skill", "evaluate_progress"),
                reasoning=plan_dict.get("reasoning", "No reasoning provided"),
                arguments=plan_dict.get("arguments", {}),
                expected_outcome=plan_dict.get("expected_outcome", "")
            )
        except json.JSONDecodeError as e:
            print(f"[OrchestratorAgent] WARNING: Failed to parse plan: {e}")
            print(f"  Response: {response_text}")

            # Fallback: evaluate progress
            return Plan(
                skill="evaluate_progress",
                reasoning="Failed to parse LLM response, evaluating current state",
                arguments={},
                expected_outcome="Understand current progress"
            )

    # ========================================
    # SIMPLE PROCEDURAL RUN (MAIN ENTRY POINT)
    # ========================================

    def run(
        self,
        requirements: Dict[str, Any],
        context: Dict[str, Any],
        shared_memory: 'SharedSessionMemory'
    ) -> Any:
        """
        Phase 7.3: Simple procedural run without LLM planning.

        This is the main entry point for procedural mode (non-agent).
        It follows a fixed sequence: Discovery -> Knowledge -> UX -> React -> Consistency.

        Args:
            requirements: User requirements (screen_type, intent, etc.)
            context: Additional context (data_sources, etc.)
            shared_memory: SharedSessionMemory instance (created by orchestrator)

        Returns:
            Generated React files
        """
        print("\n" + "="*80)
        print("PROCEDURAL ORCHESTRATOR (Phase 7.3)")
        print("="*80)
        print("Fixed sequence: Filter -> Discovery -> Pipeline Assembly -> Knowledge -> UX -> React -> Consistency")
        print("="*80 + "\n")

        # Store shared_memory on self for skills to access
        self.shared_memory = shared_memory

        # Initialize session memory for skills
        import uuid
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        self.memory = SessionMemory(
            session_id=session_id,
            user_requirements=requirements,
            user_context=context
        )

        # Step 0: Filter sources based on user intent
        print("\n[Step 0/7] Filtering data sources based on intent...")

        # Try domain-specific routing first (petroleum, chemical, etc.)
        intent = self.memory.user_requirements.get('intent', '')
        all_source_ids = list(self.memory.user_context.get('data_sources', {}).keys())

        # Format sources for petroleum router (needs list of dicts with 'id' field)
        available_sources = [{'id': source_id} for source_id in all_source_ids]

        # Try petroleum domain routing
        petroleum_routed = route_petroleum_query(intent, available_sources)

        if petroleum_routed is not None:
            # Petroleum domain routing succeeded
            filtered_sources = [source['id'] for source in petroleum_routed]
            print(f"  [PETROLEUM_ROUTER] Domain-specific routing applied")
            print(f"  Filtered to: {filtered_sources}")
        else:
            # Fall back to LLM-based filtering
            print(f"  [PETROLEUM_ROUTER] No domain routing applied, using LLM filtering")
            filter_result = self._skill_filter_sources()
            filtered_sources = filter_result.get('filtered_sources', None)
            print(f"  Filtered to: {filtered_sources}")

        # CRITICAL: Update shared_memory.user_requirements with filtered sources
        # This ensures UX Designer only sees filtered data sources
        if filtered_sources and shared_memory:
            original_sources = shared_memory.user_requirements.get('data_sources', {})
            filtered_data_sources = {
                source_id: source_data
                for source_id, source_data in original_sources.items()
                if source_id in filtered_sources
            }
            shared_memory.user_requirements['data_sources'] = filtered_data_sources
            print(f"  [PROPAGATED] Updated shared_memory with {len(filtered_data_sources)} filtered sources")

        # Step 1: Discover data (using filtered sources)
        print("\n[Step 1/7] Discovering data...")
        self._skill_discover_data(filter_sources=filtered_sources)

        # --- DEBUG: Dump raw discovery output ---
        import json
        from pathlib import Path
        debug_path = Path("debug_discovery.json")
        try:
            with debug_path.open("w", encoding="utf-8") as f:
                json.dump(self.memory.data_context, f, indent=2, default=str)
            print(f"[DEBUG] Discovery output written to {debug_path.resolve()}")
        except Exception as e:
            print(f"[DEBUG] Failed to write discovery debug file: {e}")
        # --- END DEBUG ---

        # Step 1.5: MANDATORY Pipeline Assembly (MUST run before UX/React!)
        print("\n[Step 2/7] Assembling pipelines with stage detection...")
        print("  [CRITICAL] This step MUST complete before UX/React generation")
        self._skill_assemble_pipelines()

        # --- DEBUG: Dump POST-assembly output ---
        debug_path_post = Path("debug_post_assembly.json")
        try:
            with debug_path_post.open("w", encoding="utf-8") as f:
                json.dump(self.memory.data_context, f, indent=2, default=str)
            print(f"[DEBUG] POST-assembly output written to {debug_path_post.resolve()}")
        except Exception as e:
            print(f"[DEBUG] Failed to write post-assembly debug file: {e}")
        # --- END DEBUG ---

        # Step 2: Retrieve knowledge
        print("\n[Step 3/7] Retrieving knowledge...")
        self._skill_retrieve_knowledge()

        # Step 3: Build session context
        print("\n[Step 4/7] Building session context...")
        self._skill_build_session_context()

        # Step 4: Generate UX
        print("\n[Step 5/7] Generating UX design...")
        ux_result = self._skill_generate_ux()
        if not ux_result.get("success"):
            error = ux_result.get("error", "UX generation failed")
            print(f"[ERROR] {error}")
            return None

        # Step 5: Generate React (includes consistency checks and convergence loop)
        print("\n[Step 6/7] Generating React code...")
        react_result = self._skill_generate_react()
        if not react_result.get("success"):
            error = react_result.get("error", "React generation failed")
            print(f"[ERROR] {error}")
            return None

        print(f"\n{'='*80}")
        print("PROCEDURAL ORCHESTRATOR COMPLETE")
        print(f"{'='*80}")
        print(f"  React files generated: {self.shared_memory.react_files is not None}")
        print(f"  UX spec version: {self.shared_memory.ux_spec_version}")
        print(f"  React version: {self.shared_memory.react_version}")
        print(f"{'='*80}\n")

        return self.shared_memory.react_files

    # ========================================
    # REASONING LOOP (LLM-BACKED AGENT MODE)
    # ========================================

    def generate_ui_code(
        self,
        requirements: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Any:
        """
        Generate UI code using autonomous reasoning loop with LLM planning.

        This is the main entry point for autonomous agent mode (use_agent_mode=True).

        Instead of:
          discover -> knowledge -> UX -> React -> done

        We do:
          while not goal_achieved:
              plan next action
              execute skill
              evaluate result
              update memory
              iterate

        Args:
            requirements: User requirements (screen_type, intent, etc.)
            context: Additional context (data_sources, etc.)

        Returns:
            Generated React files
        """
        print("\n" + "="*80)
        print("AUTONOMOUS ORCHESTRATOR AGENT (Phase 4)")
        print("="*80)
        print("Using LLM-backed reasoning to generate UI code")
        print("="*80 + "\n")

        # Initialize session memory
        session_id = f"session_{self.memory.iteration if self.memory else 0}"
        self.memory = SessionMemory(
            session_id=session_id,
            user_requirements=requirements,
            user_context=context
        )

        # Phase 6.2: Create single SharedSessionMemory instance for agent collaboration
        from src.agents.shared_memory import SharedSessionMemory
        self.shared_memory = SharedSessionMemory(session_id=session_id)
        self.shared_memory.user_requirements = requirements
        self.shared_memory.user_context = context

        print("[Phase 6.2] SharedSessionMemory initialized for multi-agent collaboration")

        # Reasoning loop
        for iteration in range(self.MAX_ITERATIONS):
            self.memory.iteration = iteration

            print(f"\n{'='*80}")
            print(f"REASONING ITERATION {iteration + 1}/{self.MAX_ITERATIONS}")
            print(f"{'='*80}")

            # 1. Plan next action
            plan = self._plan_next_action()

            # 2. Execute planned skill
            result = self._execute_skill(plan)

            # 3. Update memory
            self.memory.actions_taken.append(plan.skill)
            self.memory.skills_used.append(plan.skill)

            # 4. Check if goal achieved
            if self.memory.goal_achieved or plan.skill == "finish":
                print(f"\n{'='*80}")
                print("GOAL ACHIEVED!")
                print(f"{'='*80}")
                break

            # 5. Safety check: max iterations
            if iteration >= self.MAX_ITERATIONS - 1:
                print(f"\n{'='*80}")
                print("WARNING: Reached max iterations, finishing now")
                print(f"{'='*80}")
                break

        # Return final output
        print(f"\n{'='*80}")
        print("AUTONOMOUS ORCHESTRATOR COMPLETE")
        print(f"{'='*80}")
        print(f"  Total iterations: {self.memory.iteration + 1}")
        print(f"  Skills used: {', '.join(set(self.memory.skills_used))}")
        print(f"  Errors encountered: {len(self.memory.errors)}")
        print(f"  Goal achieved: {self.memory.goal_achieved}")
        print(f"{'='*80}\n")

        return self.memory.react_files

    def _execute_skill(self, plan: Plan) -> Dict:
        """
        Execute a planned skill.

        Args:
            plan: The plan containing skill name and arguments

        Returns:
            Result dict from skill execution
        """
        skill_info = self.skills.get(plan.skill)

        if not skill_info:
            print(f"[OrchestratorAgent] ERROR: Unknown skill '{plan.skill}'")
            return {"error": f"Unknown skill: {plan.skill}"}

        print(f"\n[OrchestratorAgent] Executing skill: {plan.skill}")

        try:
            # Call the skill function
            result = skill_info["fn"](**plan.arguments)

            print(f"[OrchestratorAgent] Skill completed: {plan.skill}")
            if "error" in result and result["error"]:
                print(f"  Error: {result['error']}")

            return result

        except Exception as e:
            error_msg = f"Skill execution failed: {e}"
            print(f"[OrchestratorAgent] ERROR: {error_msg}")
            self.memory.errors.append(error_msg)
            self.memory.last_error = str(e)

            return {"error": error_msg}
