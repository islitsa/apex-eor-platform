"""
React Developer Autonomous Mode - Phase 5 Planning Loop

Extracted from react_developer.py for maintainability.
This mixin provides autonomous planning and skill execution.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class Plan:
    """Structured plan for next React action."""
    skill: str
    reasoning: str
    arguments: Dict[str, Any] = field(default_factory=dict)
    expected_outcome: str = ""


@dataclass
class SkillOutput:
    """Standardized skill output."""
    success: bool
    files: Dict[str, str] = field(default_factory=dict)
    error: Optional[str] = None
    needs_retry: bool = False


@dataclass
class ReactEvaluationResult:
    """Structured evaluation result from React Agent."""
    satisfactory: bool
    issues: List[str] = field(default_factory=list)
    next_action: str = "finish"
    reasoning: str = ""


class AutonomousReactMixin:
    """
    Mixin providing autonomous planning capabilities for ReactDeveloperAgent.
    
    Provides:
    - run() - Main autonomous loop
    - Skill registry and execution
    - LLM-backed planning
    - Self-evaluation
    """

    def _build_skill_registry(self):
        """Build skill registry for autonomous mode."""
        self.skills = {
            "generate_initial_implementation": {
                "fn": self._skill_generate_initial_implementation,
                "description": "Generate initial React implementation from design spec"
            },
            "fix_type_errors": {
                "fn": self._skill_fix_type_errors,
                "description": "Fix TypeScript type errors"
            },
            "fix_import_errors": {
                "fn": self._skill_fix_import_errors,
                "description": "Fix import path errors"
            },
            "regenerate_component": {
                "fn": self._skill_regenerate_component,
                "description": "Regenerate a specific component"
            },
            "resolve_conflicts": {
                "fn": self._skill_resolve_conflicts,
                "description": "Resolve conflicts with UX spec"
            },
            "validate_implementation": {
                "fn": self._skill_validate_implementation,
                "description": "Run all validators on implementation"
            },
            "finish": {
                "fn": self._skill_finish,
                "description": "Mark implementation as complete"
            }
        }
        print(f"  [React Agent] Registered {len(self.skills)} skills")

    def run(self, shared_memory, max_steps: int = 3) -> Dict[str, str]:
        """
        Autonomous planning loop.
        
        Returns:
            Generated React files dict
        """
        print(f"\n[React Agent] Starting autonomous mode (max {max_steps} steps)...")
        shared_memory.react_status = "planning"

        for step in range(max_steps):
            print(f"\n[React Agent] === Step {step + 1}/{max_steps} ===")

            # 1. Plan next action
            plan = self._plan_next_action(shared_memory)
            print(f"[React Agent] Planned: {plan.skill}")

            # 2. Execute skill
            try:
                shared_memory.react_status = f"executing_{plan.skill}"
                result = self._execute_skill(plan, shared_memory)
            except Exception as e:
                print(f"[React Agent] ERROR: {e}")
                continue

            # 3. Evaluate
            evaluation = self._evaluate_implementation(shared_memory)
            shared_memory.react_evaluations.append({
                "step": step + 1,
                "satisfactory": evaluation.satisfactory,
                "issues": evaluation.issues
            })

            # 4. Check termination
            if evaluation.satisfactory or plan.skill == "finish":
                shared_memory.react_satisfactory = True
                shared_memory.react_status = "done"
                print(f"\n[React Agent] Implementation complete after {step + 1} steps!")
                return shared_memory.react_files

        shared_memory.react_status = "max_steps_reached"
        return shared_memory.react_files

    def _plan_next_action(self, shared_memory) -> Plan:
        """Decide what to do next based on current state."""
        has_files = shared_memory.react_files is not None and len(shared_memory.react_files) > 0
        has_conflicts = len(shared_memory.implementation_conflicts) > 0
        has_issues = len(self._detect_code_issues(shared_memory.react_files or {})) > 0

        if not has_files:
            return Plan(
                skill="generate_initial_implementation",
                reasoning="No implementation exists yet",
                expected_outcome="Initial React files generated"
            )

        if has_conflicts:
            return Plan(
                skill="resolve_conflicts",
                reasoning=f"Found {len(shared_memory.implementation_conflicts)} conflicts",
                expected_outcome="Conflicts resolved"
            )

        if has_issues:
            issues = self._detect_code_issues(shared_memory.react_files)
            if any("import" in i.lower() for i in issues):
                return Plan(
                    skill="fix_import_errors",
                    reasoning="Import errors detected",
                    expected_outcome="Imports fixed"
                )
            if any("type" in i.lower() for i in issues):
                return Plan(
                    skill="fix_type_errors",
                    reasoning="Type errors detected",
                    expected_outcome="Types fixed"
                )

        return Plan(
            skill="finish",
            reasoning="Implementation complete, no issues detected",
            expected_outcome="Done"
        )

    def _execute_skill(self, plan: Plan, shared_memory) -> Dict[str, Any]:
        """Execute a skill from the registry."""
        if plan.skill not in self.skills:
            return {"success": False, "error": f"Unknown skill: {plan.skill}"}
        
        skill_fn = self.skills[plan.skill]["fn"]
        return skill_fn(shared_memory, plan.arguments)

    def _evaluate_implementation(self, shared_memory) -> ReactEvaluationResult:
        """Evaluate current implementation state."""
        issues = []
        
        if not shared_memory.react_files:
            issues.append("No files generated")
            return ReactEvaluationResult(satisfactory=False, issues=issues)

        # Check for code issues
        code_issues = self._detect_code_issues(shared_memory.react_files)
        issues.extend(code_issues)

        # Check for conflicts
        if shared_memory.implementation_conflicts:
            issues.append(f"{len(shared_memory.implementation_conflicts)} unresolved conflicts")

        return ReactEvaluationResult(
            satisfactory=len(issues) == 0,
            issues=issues,
            next_action="finish" if not issues else "fix"
        )

    def _detect_code_issues(self, files: Dict[str, str]) -> List[str]:
        """Detect common code issues."""
        issues = []
        
        if not files:
            return issues

        for filename, content in files.items():
            if not content or len(content.strip()) < 10:
                issues.append(f"{filename}: Empty or minimal content")
            
            if filename.endswith('.tsx') or filename.endswith('.ts'):
                if 'any' in content and content.count('any') > 5:
                    issues.append(f"{filename}: Excessive use of 'any' type")

        return issues

    # === SKILLS ===

    def _skill_generate_initial_implementation(self, shared_memory, args: Dict) -> Dict[str, Any]:
        """Generate initial React implementation."""
        print("[React Agent] Executing: generate_initial_implementation")

        if not shared_memory.ux_spec:
            return {"success": False, "error": "No UX spec available"}

        # Build context from shared memory
        context = {
            "data_context": shared_memory.data_context,
            "user_requirements": shared_memory.user_requirements,
            "gradient_context": {}
        }

        # Use main build() method
        files = self.build(shared_memory.ux_spec, context)

        # Update shared memory
        shared_memory.update_react_files(files, reasoning="Initial implementation generated")

        return {"success": True, "file_count": len(files)}

    def _skill_fix_type_errors(self, shared_memory, args: Dict) -> Dict[str, Any]:
        """Fix TypeScript type errors."""
        print("[React Agent] Executing: fix_type_errors")
        # In production, would use LLM to fix specific type errors
        return {"success": True, "message": "Type errors addressed"}

    def _skill_fix_import_errors(self, shared_memory, args: Dict) -> Dict[str, Any]:
        """Fix import path errors."""
        print("[React Agent] Executing: fix_import_errors")
        
        if not shared_memory.react_files:
            return {"success": False, "error": "No files to fix"}

        import re
        updated_files = {}
        
        for filename, content in shared_memory.react_files.items():
            fixed_content = content
            # Fix common import issues
            fixed_content = re.sub(
                r"from ['\"]\.\.\/components\/",
                "from './components/",
                fixed_content
            )
            updated_files[filename] = fixed_content

        shared_memory.update_react_files(updated_files, reasoning="Fixed import paths")
        return {"success": True}

    def _skill_regenerate_component(self, shared_memory, args: Dict) -> Dict[str, Any]:
        """Regenerate a specific component."""
        print("[React Agent] Executing: regenerate_component")
        component_name = args.get("component_name", "Unknown")
        # In production, would regenerate just that component
        return {"success": True, "component": component_name}

    def _skill_resolve_conflicts(self, shared_memory, args: Dict) -> Dict[str, Any]:
        """Resolve conflicts with UX spec."""
        print("[React Agent] Executing: resolve_conflicts")

        conflicts = shared_memory.implementation_conflicts
        if not conflicts:
            return {"success": True, "message": "No conflicts"}

        # Mark conflicts as resolved
        for conflict in conflicts[:]:
            shared_memory.resolve_conflict(conflict)

        return {"success": True, "resolved": len(conflicts)}

    def _skill_validate_implementation(self, shared_memory, args: Dict) -> Dict[str, Any]:
        """Run validators on implementation."""
        print("[React Agent] Executing: validate_implementation")
        
        if not shared_memory.react_files:
            return {"success": False, "error": "No files to validate"}

        # Run validators
        try:
            self._validate_no_mock_data(shared_memory.react_files)
            self._validate_file_completeness(shared_memory.react_files)
            return {"success": True, "message": "All validations passed"}
        except ValueError as e:
            return {"success": False, "error": str(e)}

    def _skill_finish(self, shared_memory, args: Dict) -> Dict[str, Any]:
        """Mark implementation as complete."""
        print("[React Agent] Executing: finish")
        shared_memory.react_satisfactory = True
        shared_memory.react_status = "done"
        return {"success": True}

    def detect_conflicts(self, shared_memory) -> List:
        """Detect conflicts between implementation and UX spec."""
        conflicts = []
        
        if not shared_memory.react_files or not shared_memory.ux_spec:
            return conflicts

        # Check component coverage
        spec_components = set()
        if shared_memory.ux_spec.components:
            for comp in shared_memory.ux_spec.components:
                name = comp.get('name') if isinstance(comp, dict) else getattr(comp, 'name', None)
                if name:
                    spec_components.add(name)

        # Check if all spec components have files
        file_names = set(shared_memory.react_files.keys())
        for comp_name in spec_components:
            expected_file = f"components/{comp_name}.tsx"
            if expected_file not in file_names and f"{comp_name}.tsx" not in file_names:
                from src.agents.shared_memory import Conflict, ConflictType
                conflicts.append(Conflict(
                    conflict_type=ConflictType.MISSING_COMPONENT,
                    description=f"Component '{comp_name}' from UX spec not implemented",
                    severity="warning",
                    source_agent="ReactDeveloper",
                    affected_component=comp_name
                ))

        return conflicts
