"""
UX Designer Autonomous Mode - Phase 5 Planning Loop

Extracted from ux_designer.py for maintainability.
This mixin provides autonomous planning and skill execution.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class Plan:
    """Structured plan for next UX action."""
    skill: str
    reasoning: str
    arguments: Dict[str, Any] = field(default_factory=dict)
    expected_outcome: str = ""


@dataclass
class UXEvaluationResult:
    """Structured evaluation result from UX Agent."""
    satisfactory: bool
    issues: List[str] = field(default_factory=list)
    next_action: str = "finish"
    conflicts_detected: List[Any] = field(default_factory=list)
    reasoning: str = ""


class AutonomousUXMixin:
    """
    Mixin providing autonomous planning capabilities for UXDesignerAgent.
    
    Provides:
    - run() - Main autonomous loop
    - Skill registry and execution
    - LLM-backed planning
    - Self-evaluation
    """

    def _build_skill_registry(self):
        """Build skill registry for autonomous mode."""
        self.skills = {
            "generate_initial_spec": {
                "fn": self._skill_generate_initial_spec,
                "description": "Generate initial design specification from requirements"
            },
            "refine_spec": {
                "fn": self._skill_refine_spec,
                "description": "Refine existing spec based on feedback"
            },
            "address_conflicts": {
                "fn": self._skill_address_conflicts,
                "description": "Fix schema/component conflicts"
            },
            "finish": {
                "fn": self._skill_finish,
                "description": "Mark design as complete"
            }
        }
        print(f"  [UX Agent] Registered {len(self.skills)} skills")

    def run(self, shared_memory, max_steps: int = 3):
        """
        Autonomous planning loop.
        
        Returns:
            Final design spec from shared_memory.ux_spec
        """
        print(f"\n[UX Agent] Starting autonomous mode (max {max_steps} steps)...")
        shared_memory.ux_status = "planning"

        for step in range(max_steps):
            print(f"\n[UX Agent] === Step {step + 1}/{max_steps} ===")

            # 1. Plan next action
            plan = self._plan_next_step(shared_memory)
            print(f"[UX Agent] Planned: {plan.skill}")

            # 2. Execute skill
            try:
                shared_memory.ux_status = f"executing_{plan.skill}"
                result = self._execute_skill(plan, shared_memory)
            except Exception as e:
                print(f"[UX Agent] ERROR: {e}")
                shared_memory.ux_reasoning_trace.append(f"ERROR: {str(e)}")
                continue

            # 3. Evaluate
            evaluation = self._evaluate_design(shared_memory)
            shared_memory.ux_evaluations.append({
                "step": step + 1,
                "satisfactory": evaluation.satisfactory,
                "issues": evaluation.issues
            })

            # 4. Check termination
            if evaluation.satisfactory or plan.skill == "finish":
                shared_memory.ux_satisfactory = True
                shared_memory.ux_status = "done"
                print(f"\n[UX Agent] Design complete after {step + 1} steps!")
                return shared_memory.ux_spec

        shared_memory.ux_status = "max_steps_reached"
        return shared_memory.ux_spec

    def _plan_next_step(self, shared_memory) -> Plan:
        """LLM-backed planning: decide what to do next."""
        # Build state summary
        has_spec = shared_memory.ux_spec is not None
        has_conflicts = len(shared_memory.design_conflicts) > 0
        has_feedback = shared_memory.user_requirements.get("user_feedback")

        # Simple heuristic planning (can be LLM-backed for complex cases)
        if not has_spec:
            return Plan(
                skill="generate_initial_spec",
                reasoning="No spec exists, need to generate initial design",
                expected_outcome="Design spec created"
            )
        
        if has_conflicts:
            return Plan(
                skill="address_conflicts",
                reasoning=f"Found {len(shared_memory.design_conflicts)} conflicts to resolve",
                expected_outcome="Conflicts resolved"
            )
        
        if has_feedback:
            return Plan(
                skill="refine_spec",
                reasoning="User feedback received, refining design",
                expected_outcome="Refined spec"
            )

        return Plan(
            skill="finish",
            reasoning="Spec complete, no conflicts, no pending feedback",
            expected_outcome="Design finalized"
        )

    def _execute_skill(self, plan: Plan, shared_memory) -> Dict[str, Any]:
        """Execute a skill from the registry."""
        if plan.skill not in self.skills:
            return {"success": False, "error": f"Unknown skill: {plan.skill}"}
        
        skill_fn = self.skills[plan.skill]["fn"]
        return skill_fn(shared_memory, plan.arguments)

    def _evaluate_design(self, shared_memory) -> UXEvaluationResult:
        """Evaluate current design state."""
        issues = []
        
        if not shared_memory.ux_spec:
            issues.append("No design spec generated")
        
        if shared_memory.design_conflicts:
            issues.append(f"{len(shared_memory.design_conflicts)} unresolved conflicts")
        
        if not shared_memory.ux_spec or not getattr(shared_memory.ux_spec, 'components', None):
            issues.append("No components defined")

        return UXEvaluationResult(
            satisfactory=len(issues) == 0,
            issues=issues,
            next_action="finish" if not issues else "refine_spec"
        )

    # === SKILLS ===

    def _skill_generate_initial_spec(self, shared_memory, args: Dict) -> Dict[str, Any]:
        """Generate initial design specification."""
        print("[UX Agent] Executing: generate_initial_spec")

        requirements = shared_memory.user_requirements
        knowledge = {
            "data_context": shared_memory.data_context,
            "gradient_context": shared_memory.knowledge.get("gradient_context") if shared_memory.knowledge else None
        }

        # Use main design() method
        design_spec = self.design(requirements, knowledge)

        # Update shared memory
        shared_memory.update_ux_spec(design_spec, reasoning="Initial design generated")

        # Cache component IDs
        if design_spec.components:
            canonical_ids = [
                comp.get('name') if isinstance(comp, dict) else getattr(comp, 'name', None)
                for comp in design_spec.components
            ]
            shared_memory.canonical_component_ids = [cid for cid in canonical_ids if cid]

        return {"success": True, "spec_version": shared_memory.ux_spec_version}

    def _skill_refine_spec(self, shared_memory, args: Dict) -> Dict[str, Any]:
        """Refine existing spec based on feedback."""
        print("[UX Agent] Executing: refine_spec")

        if not shared_memory.ux_spec:
            return {"success": False, "error": "No spec to refine"}

        feedback = shared_memory.user_requirements.get("user_feedback", "")
        refined_spec = self._refine_design_partial(
            current_spec=shared_memory.ux_spec,
            feedback=feedback,
            shared_memory=shared_memory
        )

        shared_memory.update_ux_spec(refined_spec, reasoning=f"Refined: {feedback[:100]}")
        return {"success": True, "spec_version": shared_memory.ux_spec_version}

    def _skill_address_conflicts(self, shared_memory, args: Dict) -> Dict[str, Any]:
        """Address schema/component conflicts."""
        print("[UX Agent] Executing: address_conflicts")

        from src.agents.shared_memory import ConflictType

        conflicts = shared_memory.design_conflicts
        if not conflicts:
            return {"success": True, "message": "No conflicts"}

        spec = shared_memory.ux_spec
        if not spec:
            return {"success": False, "error": "No spec to modify"}

        modifications = []
        for conflict in conflicts:
            if conflict.conflict_type == ConflictType.MISSING_COMPONENT:
                spec.components.append({
                    "name": conflict.affected_component,
                    "type": "data_display",
                    "intent": f"Added to resolve conflict",
                    "pattern": "default",
                    "features": []
                })
                modifications.append(f"Added: {conflict.affected_component}")

        shared_memory.update_ux_spec(spec, reasoning=f"Resolved {len(conflicts)} conflicts")
        
        for conflict in conflicts[:]:
            shared_memory.resolve_conflict(conflict)

        return {"success": True, "resolved": len(conflicts), "modifications": modifications}

    def _skill_finish(self, shared_memory, args: Dict) -> Dict[str, Any]:
        """Mark design as complete."""
        print("[UX Agent] Executing: finish")
        shared_memory.ux_satisfactory = True
        shared_memory.ux_status = "done"
        return {"success": True}

    def _refine_design_partial(self, current_spec, feedback: str, shared_memory) -> 'DesignSpec':
        """Partially refine design based on feedback."""
        # For now, regenerate with feedback in requirements
        requirements = shared_memory.user_requirements.copy()
        requirements['user_feedback'] = feedback
        
        knowledge = {
            "data_context": shared_memory.data_context,
            "gradient_context": shared_memory.knowledge.get("gradient_context") if shared_memory.knowledge else None
        }
        
        return self.design(requirements, knowledge)

    def detect_conflicts(self, shared_memory) -> List:
        """Detect conflicts in current design."""
        conflicts = []
        
        if not shared_memory.ux_spec:
            return conflicts

        # Check for missing data sources
        spec_sources = set(shared_memory.ux_spec.data_sources.keys()) if shared_memory.ux_spec.data_sources else set()
        context_sources = set(shared_memory.data_context.keys()) if shared_memory.data_context else set()
        
        missing = context_sources - spec_sources
        if missing:
            from src.agents.shared_memory import Conflict, ConflictType
            for source in missing:
                conflicts.append(Conflict(
                    conflict_type=ConflictType.DESIGN_SCHEMA_MISMATCH,
                    description=f"Data source '{source}' not in design",
                    severity="warning",
                    source_agent="UXDesigner"
                ))

        return conflicts
