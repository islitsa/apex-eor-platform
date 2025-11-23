"""
Shared Session Memory - Phase 6.1

This is the communication bus for multi-agent collaboration.

All agents (Orchestrator, UX, React) read and write to this shared memory,
enabling true multi-agent negotiation and conflict resolution.

Phase 6.1 additions:
- AgentMessage: Directed communication between agents
- ConflictPatch: Proposed fixes for conflicts
- ChangeRequest: Agent-to-agent change requests
- Enhanced conflict types for consistency checking
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import time


class ConflictType(Enum):
    """Types of conflicts that can occur between agents"""
    # Original Phase 5 conflicts
    DESIGN_SCHEMA_MISMATCH = "design_schema_mismatch"
    MISSING_DESIGN_FIELD = "missing_design_field"
    IMPLEMENTATION_TYPE_ERROR = "implementation_type_error"
    INVALID_IMPORT = "invalid_import"
    MISSING_COMPONENT = "missing_component"
    DATA_SOURCE_MISMATCH = "data_source_mismatch"
    STAGE_MISMATCH = "stage_mismatch"
    FILE_PATH_ERROR = "file_path_error"

    # Phase 6.1 - Design/Code consistency conflicts
    COMPONENT_NAME_MISMATCH = "component_name_mismatch"
    PROP_LIST_MISMATCH = "prop_list_mismatch"
    ATTRIBUTE_MISMATCH = "attribute_mismatch"
    DATA_BINDING_INCORRECT = "data_binding_incorrect"
    INTERACTIVE_MISMATCH = "interactive_mismatch"
    NESTED_COMPONENT_INCONSISTENCY = "nested_component_inconsistency"

    # Phase 6.1 - Schema alignment conflicts
    SCHEMA_FIELD_NONEXISTENT = "schema_field_nonexistent"
    TYPE_MISMATCH = "type_mismatch"
    NUMERIC_VS_CATEGORICAL_ERROR = "numeric_vs_categorical_error"

    # Phase 6.1 - Knowledge conflicts
    INVALID_DOMAIN_ASSUMPTION = "invalid_domain_assumption"
    DANGEROUS_AFFORDANCE = "dangerous_affordance"
    INCORRECT_LABELING = "incorrect_labeling"
    OUT_OF_DOMAIN_PATTERN = "out_of_domain_pattern"

    # Phase 6.1 - Component compatibility conflicts
    DEPENDENCY_ERROR = "dependency_error"
    REQUIRED_PROP_MISSING = "required_prop_missing"
    EVENT_CONTRACT_INVALID = "event_contract_invalid"


@dataclass
class Conflict:
    """
    A conflict detected by an agent or consistency tool.

    Conflicts are written to shared memory so other agents can respond.
    Phase 6.1: Enhanced with target information for negotiation.
    """
    conflict_type: ConflictType
    source_agent: str  # Which agent/tool detected this
    description: str
    affected_component: Optional[str] = None
    suggested_resolution: Optional[str] = None
    severity: str = "medium"  # low, medium, high, critical
    target: str = "UNKNOWN"  # Phase 6.1: "UX_SPEC" | "REACT_IMPL" | "BOTH"
    path: Optional[str] = None  # Phase 6.1: JSON pointer to affected element


@dataclass
class Question:
    """
    A question one agent has for another.

    Agents can ask questions when they need clarification.
    """
    asking_agent: str
    target_agent: str
    question: str
    context: Dict[str, Any] = field(default_factory=dict)
    answer: Optional[str] = None
    answered: bool = False


@dataclass
class AgentMessage:
    """
    Phase 6.1: Directed message from one agent to another.

    Used for negotiation when agents need to coordinate changes.
    """
    from_agent: str
    to_agent: str
    message: str
    proposed_fix: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConflictPatch:
    """
    Phase 6.1: A proposed patch to resolve a conflict.

    These accumulate in memory but are not applied automatically.
    In Phase 6.2, OrchestratorAgent will decide whether to apply them.
    """
    target: str  # "UX_SPEC" | "REACT_IMPL"
    operation: str  # "add" | "delete" | "modify"
    path: str  # JSON pointer to affected element
    value: Any = None
    conflict_id: Optional[str] = None
    proposed_by: str = "TOOL"  # Which tool/agent proposed this
    timestamp: float = field(default_factory=time.time)


@dataclass
class ChangeRequest:
    """
    Phase 6.1: A request from one agent to another to make a change.

    This is the heart of negotiation.
    Agents ask each other for changes rather than directly mutating outputs.
    """
    from_agent: str
    to_agent: str
    description: str
    suggested_action: str
    priority: str = "medium"  # low, medium, high, critical
    accepted: Optional[bool] = None
    response: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class SharedSessionMemory:
    """
    Shared memory bus for multi-agent collaboration.

    This is the single source of truth that all agents read and write to.
    Replaces individual agent memory with a collaborative memory space.

    Phase 5 innovation: Agents communicate through memory, not method calls.
    """
    # Session metadata
    session_id: str
    iteration: int = 0

    # User requirements (read-only after init)
    user_requirements: Dict[str, Any] = field(default_factory=dict)
    user_context: Dict[str, Any] = field(default_factory=dict)

    # Discovered data (populated by orchestrator)
    data_context: Optional[Dict] = None
    knowledge: Optional[Dict] = None
    session_ctx: Any = None  # SessionContext object

    # UX Designer outputs
    ux_spec: Any = None  # DesignSpec object
    ux_spec_version: int = 0  # Increments when UX refines
    ux_history: List[Dict] = field(default_factory=list)
    ux_reasoning_trace: List[str] = field(default_factory=list)

    # Fix #8: Cache canonical component IDs for stability across iterations
    canonical_component_ids: List[str] = field(default_factory=list)

    # React Developer outputs
    react_files: Optional[Dict[str, str]] = None
    react_version: int = 0  # Increments when React regenerates
    react_history: List[Dict] = field(default_factory=list)
    react_reasoning_trace: List[str] = field(default_factory=list)

    # Conflicts (agents write here when they detect issues)
    design_conflicts: List[Conflict] = field(default_factory=list)
    implementation_conflicts: List[Conflict] = field(default_factory=list)
    resolved_conflicts: List[Conflict] = field(default_factory=list)

    # Inter-agent questions
    questions: List[Question] = field(default_factory=list)
    unanswered_questions: List[Question] = field(default_factory=list)

    # Evaluation results
    ux_evaluations: List[Dict] = field(default_factory=list)
    react_evaluations: List[Dict] = field(default_factory=list)

    # Agent status
    ux_status: str = "idle"  # idle, planning, designing, refining, done
    react_status: str = "idle"  # idle, planning, generating, fixing, done
    orchestrator_status: str = "idle"

    # Success flags
    ux_satisfactory: bool = False
    react_satisfactory: bool = False
    goal_achieved: bool = False

    # Negotiation log (for debugging multi-agent conversations)
    negotiation_log: List[Dict] = field(default_factory=list)

    # ========================================
    # Phase 6.1: Negotiation Layer
    # ========================================

    # Agent-to-agent messages (directed communication)
    agent_messages: List[AgentMessage] = field(default_factory=list)

    # Proposed patches to resolve conflicts (not applied automatically)
    conflict_patches: List[ConflictPatch] = field(default_factory=list)

    # Change requests between agents (heart of negotiation)
    change_requests: List[ChangeRequest] = field(default_factory=list)

    # Convergence watchdog (used in Phase 6.3)
    iterations_since_last_change: int = 0
    consecutive_agreements: int = 0

    def log_negotiation(self, from_agent: str, to_agent: str, message: str, metadata: Dict = None):
        """
        Log a negotiation message between agents.

        This creates an audit trail of multi-agent communication.
        """
        entry = {
            "iteration": self.iteration,
            "from": from_agent,
            "to": to_agent,
            "message": message,
            "timestamp": self.iteration,
            "metadata": metadata or {}
        }
        self.negotiation_log.append(entry)

    def add_conflict(self, conflict: Conflict, is_design: bool = True):
        """Add a conflict to shared memory"""
        if is_design:
            self.design_conflicts.append(conflict)
        else:
            self.implementation_conflicts.append(conflict)

    def resolve_conflict(self, conflict: Conflict):
        """Mark a conflict as resolved"""
        if conflict in self.design_conflicts:
            self.design_conflicts.remove(conflict)
            self.resolved_conflicts.append(conflict)
        elif conflict in self.implementation_conflicts:
            self.implementation_conflicts.remove(conflict)
            self.resolved_conflicts.append(conflict)

    def ask_question(self, asking_agent: str, target_agent: str, question: str, context: Dict = None):
        """One agent asks another a question"""
        q = Question(
            asking_agent=asking_agent,
            target_agent=target_agent,
            question=question,
            context=context or {}
        )
        self.questions.append(q)
        self.unanswered_questions.append(q)

    def answer_question(self, question: Question, answer: str):
        """Agent answers a question"""
        question.answer = answer
        question.answered = True
        if question in self.unanswered_questions:
            self.unanswered_questions.remove(question)

    def get_unresolved_conflicts(self, is_design: bool = True) -> List[Conflict]:
        """Get conflicts that still need resolution"""
        return self.design_conflicts if is_design else self.implementation_conflicts

    def get_questions_for_agent(self, agent_name: str) -> List[Question]:
        """Get all unanswered questions directed at this agent"""
        return [q for q in self.unanswered_questions if q.target_agent == agent_name]

    def update_ux_spec(self, new_spec, reasoning: str = ""):
        """UX agent updates its spec in shared memory"""
        self.ux_spec = new_spec
        self.ux_spec_version += 1
        self.ux_history.append({
            "version": self.ux_spec_version,
            "iteration": self.iteration,
            "spec": new_spec,
            "reasoning": reasoning
        })

    def update_react_files(self, new_files: Dict[str, str], reasoning: str = ""):
        """React agent updates its files in shared memory"""
        self.react_files = new_files
        self.react_version += 1
        self.react_history.append({
            "version": self.react_version,
            "iteration": self.iteration,
            "files": new_files,
            "reasoning": reasoning
        })

    def get_current_state_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current state for agent planning.

        Agents use this to understand what's happened so far.
        """
        return {
            "iteration": self.iteration,
            "has_data": self.data_context is not None,
            "has_knowledge": self.knowledge is not None,
            "has_ux_spec": self.ux_spec is not None,
            "ux_version": self.ux_spec_version,
            "has_react_files": self.react_files is not None,
            "react_version": self.react_version,
            "ux_status": self.ux_status,
            "react_status": self.react_status,
            "ux_satisfactory": self.ux_satisfactory,
            "react_satisfactory": self.react_satisfactory,
            "design_conflicts": len(self.design_conflicts),
            "implementation_conflicts": len(self.implementation_conflicts),
            "unanswered_questions": len(self.unanswered_questions),
            "goal_achieved": self.goal_achieved
        }

    # ========================================
    # Phase 6.1: Negotiation Methods
    # ========================================

    def send_message(self, from_agent: str, to_agent: str, message: str,
                     proposed_fix: Optional[str] = None, metadata: Dict = None):
        """
        Send a directed message from one agent to another.

        Phase 6.1: Enables agent-to-agent communication.
        """
        msg = AgentMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            message=message,
            proposed_fix=proposed_fix,
            metadata=metadata or {}
        )
        self.agent_messages.append(msg)

    def add_conflict_patch(self, patch: ConflictPatch):
        """
        Add a proposed patch to resolve a conflict.

        Phase 6.1: Patches are not applied automatically.
        They accumulate in memory for Phase 6.2 orchestrator to handle.
        """
        self.conflict_patches.append(patch)

    def add_change_request(self, request: ChangeRequest):
        """
        Add a change request from one agent to another.

        Phase 6.1: Heart of negotiation system.
        """
        self.change_requests.append(request)

    def update_conflicts(self, conflicts: List[Conflict]):
        """
        Update conflicts from consistency tools.

        Phase 6.1: Replace existing conflicts with new analysis.
        Separates design vs implementation conflicts by target.
        """
        # Clear existing conflicts
        self.design_conflicts.clear()
        self.implementation_conflicts.clear()

        # Categorize new conflicts
        for conflict in conflicts:
            if conflict.target == "UX_SPEC":
                self.design_conflicts.append(conflict)
            elif conflict.target == "REACT_IMPL":
                self.implementation_conflicts.append(conflict)
            elif conflict.target == "BOTH":
                # Conflicts affecting both go to both lists
                self.design_conflicts.append(conflict)
                self.implementation_conflicts.append(conflict)
            else:
                # Unknown target - default to design
                self.design_conflicts.append(conflict)

    def get_messages_for_agent(self, agent_name: str) -> List[AgentMessage]:
        """
        Get all messages directed at this agent.

        Phase 6.1: Agents check this to see what other agents want.
        """
        return [msg for msg in self.agent_messages if msg.to_agent == agent_name]

    def get_change_requests_for_agent(self, agent_name: str) -> List[ChangeRequest]:
        """
        Get all change requests directed at this agent.

        Phase 6.1: Agents check this to see what changes are requested.
        """
        return [req for req in self.change_requests
                if req.to_agent == agent_name and req.accepted is None]

    def has_design_conflicts(self) -> bool:
        """
        Check if there are any design conflicts (targeting UX_SPEC).

        Phase 6.2: Used by convergence loop to decide if UX should regenerate.
        """
        return len(self.design_conflicts) > 0

    def has_implementation_conflicts(self) -> bool:
        """
        Check if there are any implementation conflicts (targeting REACT_IMPL).

        Phase 6.2: Used by convergence loop to decide if React should regenerate.
        """
        return len(self.implementation_conflicts) > 0

    def has_high_severity_conflicts(self) -> bool:
        """
        Check if there are any high-severity conflicts.

        Phase 6.2: Used by convergence loop for quality thresholds.
        """
        all_conflicts = self.design_conflicts + self.implementation_conflicts
        return any(c.severity == "high" for c in all_conflicts)
