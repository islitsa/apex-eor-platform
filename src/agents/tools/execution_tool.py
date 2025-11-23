"""
Execution Tool - Phase 3 Step 4

Responsibility: UX/React protocol execution with retry/fallback/correction logic.
Depends on: All previous tools (DataShaping, ContextAssembly, KnowledgeAssembly)

This tool handles:
1. Bounded iteration loops for UX and React execution
2. Evaluation of agent outputs
3. Decision-making for retry/fallback
4. Fallback to legacy methods when protocol fails
"""

from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class OrchestratorState(Enum):
    """Orchestrator state enum (copied for execution tool)"""
    IDLE = "idle"
    PARSING_REQUIREMENTS = "parsing_requirements"
    DISCOVERING_DATA = "discovering_data"
    FETCHING_KNOWLEDGE = "fetching_knowledge"
    ANALYZING_GRADIENT = "analyzing_gradient"
    DESIGNING_UX = "designing_ux"
    BUILDING_SESSION = "building_session"
    GENERATING_CODE = "generating_code"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class EvaluationResult:
    """
    Structured evaluation result for decision-making.
    (Copied from orchestrator for execution tool)
    """
    satisfactory: bool
    issues: list
    can_retry: bool
    suggested_action: Optional[str]


class ExecutionTool:
    """
    Phase 3: Extract execution and retry logic from orchestrator.

    This tool encapsulates the complex iteration and fallback logic,
    making the orchestrator smaller and easier to understand.
    """

    def __init__(self):
        """Initialize the execution tool."""
        self.MAX_UX_ITERATIONS = 3
        self.MAX_REACT_ATTEMPTS = 2

    def execute_ux_with_retry(
        self,
        ux_designer,
        session_ctx,
        design_knowledge: Dict,
        requirements: Dict,
        data_context: Dict,
        evaluate_fn: Callable,
        decide_fn: Callable,
        state_transition_fn: Callable = None,
        shared_memory: Optional['SharedSessionMemory'] = None
    ) -> tuple[Any, Optional[str]]:
        """
        Execute UX Designer with bounded retry logic.

        Args:
            ux_designer: UX Designer agent instance
            session_ctx: SessionContext for protocol execution
            design_knowledge: Knowledge bundle for UX Designer
            requirements: User requirements
            data_context: Real data from API
            evaluate_fn: Function to evaluate UX output
            decide_fn: Function to decide next action
            state_transition_fn: Optional state transition callback
            shared_memory: Optional SharedSessionMemory for Phase 6.2 integration

        Returns:
            (design_spec, last_error) tuple
        """
        design_spec = None
        last_error = None

        for iteration in range(self.MAX_UX_ITERATIONS):
            if iteration > 0:
                print(f"\n[ExecutionTool] UX retry iteration {iteration + 1}/{self.MAX_UX_ITERATIONS}")

            # State transition
            if state_transition_fn:
                state_transition_fn(OrchestratorState.DESIGNING_UX)

            # Try protocol execution first
            try:
                print("[ExecutionTool] Using protocol-aware UX execution...")
                design_result = ux_designer.with_context(session_ctx).execute(shared_memory=shared_memory)

                # Convert dict back to DesignSpec for backward compatibility
                from src.agents.ux_designer import DesignSpec
                design_spec = DesignSpec(
                    screen_type=design_result.get('screen_type', 'dashboard'),
                    intent=design_result.get('intent', ''),
                    components=design_result.get('components', []),
                    interactions=design_result.get('interactions', []),
                    patterns=design_result.get('patterns', []),
                    styling=design_result.get('styling', {}),
                    data_sources=design_result.get('data_sources', {})
                )
                last_error = None

            except Exception as e:
                print(f"[ExecutionTool] Protocol execution failed: {e}")
                last_error = f"UX protocol error: {str(e)}"

                if state_transition_fn:
                    state_transition_fn(OrchestratorState.ERROR)

                # Decide next action based on error
                next_action = decide_fn(
                    OrchestratorState.ERROR,
                    ux_eval=None,
                    react_eval=None,
                    last_error=last_error
                )

                if next_action == "fallback_to_ux_legacy":
                    print("[ExecutionTool] Falling back to legacy design()...")
                    design_spec = ux_designer.design(requirements, design_knowledge)
                    last_error = None
                else:
                    print(f"[ExecutionTool] WARNING: Cannot recover from UX error")
                    continue

            # Evaluate UX output
            print("\n[ExecutionTool] Evaluating UX design specification...")
            ux_eval = evaluate_fn(design_spec, data_context)

            if not ux_eval.satisfactory:
                print(f"[ExecutionTool] WARNING: UX evaluation failed:")
                for issue in ux_eval.issues:
                    print(f"  - {issue}")

                next_action = decide_fn(
                    OrchestratorState.DESIGNING_UX,
                    ux_eval=ux_eval,
                    react_eval=None,
                    last_error=last_error
                )

                if next_action == "retry_ux_protocol" and iteration < self.MAX_UX_ITERATIONS - 1:
                    print(f"[ExecutionTool] Retrying UX Designer")
                    continue
                elif next_action == "fallback_to_ux_legacy":
                    print("[ExecutionTool] Falling back to legacy design()...")
                    design_spec = ux_designer.design(requirements, design_knowledge)
                    # Re-evaluate after fallback
                    ux_eval = evaluate_fn(design_spec, data_context)
                else:
                    print(f"[ExecutionTool] WARNING: UX issues detected but continuing")
            else:
                print("[ExecutionTool] SUCCESS: UX design specification validated")

            # If we got here, UX passed or we're continuing anyway
            break

        # Final fallback if no valid design_spec
        if not design_spec or not hasattr(design_spec, 'components'):
            print("[ExecutionTool] WARNING: No valid design_spec after iterations, using legacy fallback")
            design_spec = ux_designer.design(requirements, design_knowledge)

        return design_spec, last_error

    def execute_react_with_retry(
        self,
        react_developer,
        session_ctx,
        design_spec,
        enhanced_context: Dict,
        evaluate_fn: Callable,
        decide_fn: Callable,
        state_transition_fn: Callable = None,
        shared_memory: Optional['SharedSessionMemory'] = None
    ) -> tuple[Any, Optional[str]]:
        """
        Execute React Developer with bounded retry logic.

        Args:
            react_developer: React Developer agent instance
            session_ctx: SessionContext for protocol execution
            design_spec: Design specification from UX Designer
            enhanced_context: Enhanced context with knowledge and data
            evaluate_fn: Function to evaluate React output
            decide_fn: Function to decide next action
            state_transition_fn: Optional state transition callback
            shared_memory: Optional SharedSessionMemory for Phase 6.2 integration

        Returns:
            (react_files, last_error) tuple
        """
        react_files = None
        last_error = None

        if state_transition_fn:
            state_transition_fn(OrchestratorState.GENERATING_CODE)

        for react_attempt in range(self.MAX_REACT_ATTEMPTS):
            if react_attempt > 0:
                print(f"\n[ExecutionTool] React retry attempt {react_attempt + 1}/{self.MAX_REACT_ATTEMPTS}")

            # Try protocol execution first
            try:
                print("[ExecutionTool] Using protocol-aware React execution...")
                react_files = react_developer.with_context(session_ctx).execute(
                    shared_memory=shared_memory,
                    design_spec=design_spec
                )
                last_error = None

            except Exception as e:
                print(f"[ExecutionTool] Protocol execution failed: {e}")
                last_error = f"React protocol error: {str(e)}"

                if state_transition_fn:
                    state_transition_fn(OrchestratorState.ERROR)

                # Decide next action
                next_action = decide_fn(
                    OrchestratorState.ERROR,
                    ux_eval=None,
                    react_eval=None,
                    last_error=last_error
                )

                if next_action == "fallback_to_react_legacy":
                    print("[ExecutionTool] Falling back to legacy build()...")
                    react_files = react_developer.build(design_spec, enhanced_context)
                    last_error = None
                else:
                    print(f"[ExecutionTool] WARNING: Cannot recover from React error")
                    if react_attempt < self.MAX_REACT_ATTEMPTS - 1:
                        continue
                    else:
                        # Use legacy as final fallback
                        react_files = react_developer.build(design_spec, enhanced_context)

            # Evaluate React output
            print("\n[ExecutionTool] Evaluating React code output...")
            react_eval = evaluate_fn(react_files)

            if not react_eval.satisfactory:
                print(f"[ExecutionTool] WARNING: React evaluation failed:")
                for issue in react_eval.issues:
                    print(f"  - {issue}")

                next_action = decide_fn(
                    OrchestratorState.GENERATING_CODE,
                    ux_eval=None,
                    react_eval=react_eval,
                    last_error=last_error
                )

                if next_action == "regenerate_react" and react_attempt < self.MAX_REACT_ATTEMPTS - 1:
                    print(f"[ExecutionTool] Regenerating React code")
                    continue
                elif next_action == "fallback_to_react_legacy":
                    print("[ExecutionTool] Falling back to legacy build()...")
                    react_files = react_developer.build(design_spec, enhanced_context)
                    # Re-evaluate after fallback
                    react_eval = evaluate_fn(react_files)
                else:
                    print(f"[ExecutionTool] WARNING: React issues detected but continuing")
            else:
                print("[ExecutionTool] SUCCESS: React code output validated")

            # If we got here, React passed or we're continuing anyway
            break

        # Final fallback if no valid react_files
        if not react_files:
            print("[ExecutionTool] WARNING: No valid React output, using legacy fallback")
            react_files = react_developer.build(design_spec, enhanced_context)

        return react_files, last_error
