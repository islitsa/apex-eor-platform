"""
Protocol Layer - Type-safe context passing for Agent Studio

This module defines the core protocol types that ensure type-safe
context passing between agents. It prevents common bugs like:
- Missing context (agents executing without knowing what was discovered)
- Wrong sources (agents using undiscovered data)
- Type errors (mixed types in data structures)

Architecture:
- DiscoveryContext: What was discovered (sources, counts, confidence)
- UserIntent: What user wants (query, scope, task type)
- ExecutionContext: How agents should behave (iterations, validation)
- SessionContext: Complete context for agent execution
- ContextAware: Protocol that all agents must implement

Usage:
    from src.agents.context.protocol import SessionContext, ContextAware

    class MyAgent(ContextAware):
        def with_context(self, ctx: SessionContext) -> "MyAgent":
            self.ctx = ctx
            return self

        def execute(self) -> Dict[str, Any]:
            if not self.ctx:
                raise ValueError("Context not provided")
            # Use self.ctx.discovery.sources, etc.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Protocol, Optional, Any


class TaskType(str, Enum):
    """Type of task user wants to perform"""
    DASHBOARD = "dashboard"
    ANALYSIS = "analysis"
    REPORT = "report"


class OutputFormat(str, Enum):
    """Desired output format"""
    REACT = "react"
    STREAMLIT = "streamlit"
    JUPYTER = "jupyter"


@dataclass
class DiscoveryContext:
    """
    What was discovered during context swimming.

    This captures the results of autonomous discovery - what data sources
    the agent found in the repository that are relevant to the user's query.

    Attributes:
        sources: List of discovered source names (e.g., ["fracfocus", "rrc"])
        record_counts: Record count per source (e.g., {"fracfocus": 239059})
        discovery_confidence: Confidence score 0.0-1.0
        rationale: Why these sources were selected
        timestamp: When discovery occurred

    Example:
        discovery = DiscoveryContext(
            sources=["fracfocus", "rrc"],
            record_counts={"fracfocus": 239059, "rrc": 18200},
            discovery_confidence=0.95,
            rationale="User requested petroleum chemical data"
        )
    """
    sources: List[str]
    record_counts: Dict[str, int]
    discovery_confidence: float
    rationale: str
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate discovery context"""
        if not 0.0 <= self.discovery_confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.discovery_confidence}")

        if not self.sources:
            raise ValueError("Discovery context must have at least one source")

        # Ensure record_counts matches sources
        for source in self.sources:
            if source not in self.record_counts:
                raise ValueError(f"Source '{source}' missing from record_counts")


@dataclass
class UserIntent:
    """
    What the user wants to accomplish.

    This captures the parsed user intent, including the critical "scope" field
    that specifies exactly which data sources should be used. This prevents
    the "wrong sources" bug where agents use undiscovered data.

    Attributes:
        original_query: Raw user query ("show fracfocus data")
        parsed_intent: Structured intent ("generate_dashboard")
        scope: CRITICAL - which sources to use (["fracfocus"])
        task_type: Type of task (DASHBOARD, ANALYSIS, REPORT)
        output_format: Desired format (REACT, STREAMLIT, JUPYTER)
        filters: Optional filters ({"state": "TX"})

    Example:
        intent = UserIntent(
            original_query="show fracfocus chemical data",
            parsed_intent="generate_dashboard",
            scope=["fracfocus"],  # Only use fracfocus!
            task_type=TaskType.DASHBOARD,
            output_format=OutputFormat.REACT
        )
    """
    original_query: str
    parsed_intent: str
    scope: List[str]  # CRITICAL: Which sources to use
    task_type: TaskType
    output_format: OutputFormat
    filters: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate user intent"""
        if not self.original_query:
            raise ValueError("original_query cannot be empty")

        if not self.scope:
            raise ValueError("scope must specify at least one source")


@dataclass
class ExecutionContext:
    """
    How agents should behave during execution.

    This controls agent behavior like iteration limits, validation requirements,
    and tracing. Used for debugging and production tuning.

    Attributes:
        max_iterations: Maximum iterations for iterative agents
        require_validation: Whether to validate outputs
        trace_decisions: Whether to trace agent decisions
    """
    max_iterations: int = 5
    require_validation: bool = True
    trace_decisions: bool = True

    def __post_init__(self):
        """Validate execution context"""
        if self.max_iterations < 1:
            raise ValueError(f"max_iterations must be >= 1, got {self.max_iterations}")


@dataclass
class SessionContext:
    """
    Complete context for agent execution.

    This is the master context object that gets passed to all agents.
    It combines discovery results, user intent, and execution settings
    into a single, type-safe package.

    Attributes:
        session_id: Unique session identifier
        discovery: What was discovered (sources, counts)
        intent: What user wants (query, scope, task type)
        execution: How to execute (iterations, validation)

    Example:
        ctx = SessionContext(
            session_id=str(uuid.uuid4()),
            discovery=DiscoveryContext(...),
            intent=UserIntent(...),
            execution=ExecutionContext()
        )

        # Pass to agents
        design = ux_designer.with_context(ctx).execute()
        code = react_developer.with_context(ctx).execute()
    """
    session_id: str
    discovery: DiscoveryContext
    intent: UserIntent
    execution: ExecutionContext

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize context to dict for logging/debugging.

        Returns:
            Dict representation of context
        """
        return {
            "session_id": self.session_id,
            "discovery": {
                "sources": self.discovery.sources,
                "record_counts": self.discovery.record_counts,
                "confidence": self.discovery.discovery_confidence,
                "rationale": self.discovery.rationale,
                "timestamp": self.discovery.timestamp.isoformat()
            },
            "intent": {
                "query": self.intent.original_query,
                "parsed_intent": self.intent.parsed_intent,
                "scope": self.intent.scope,
                "task_type": self.intent.task_type.value,
                "output_format": self.intent.output_format.value,
                "filters": self.intent.filters
            },
            "execution": {
                "max_iterations": self.execution.max_iterations,
                "require_validation": self.execution.require_validation,
                "trace_decisions": self.execution.trace_decisions
            }
        }

    def __post_init__(self):
        """Validate session context"""
        if not self.session_id:
            raise ValueError("session_id cannot be empty")

        # Validate that intent.scope matches discovery.sources
        discovered_set = set(self.discovery.sources)
        scope_set = set(self.intent.scope)

        if not scope_set.issubset(discovered_set):
            undiscovered = scope_set - discovered_set
            raise ValueError(
                f"Intent scope contains undiscovered sources: {undiscovered}. "
                f"Discovered: {discovered_set}, Scope: {scope_set}"
            )


class ContextAware(Protocol):
    """
    Protocol that all agents must implement for context-aware execution.

    This is a Python typing.Protocol (structural subtyping), not a base class.
    Any class that has these two methods automatically implements this protocol.

    Methods:
        with_context(ctx): Inject context before execution
        execute(): Execute agent with injected context

    Example:
        class MyAgent(ContextAware):
            def __init__(self):
                self.ctx: Optional[SessionContext] = None

            def with_context(self, ctx: SessionContext) -> "MyAgent":
                self.ctx = ctx
                return self

            def execute(self) -> Dict[str, Any]:
                if not self.ctx:
                    raise ValueError("Context not provided. Call with_context() first.")

                # Use context
                sources = self.ctx.discovery.sources
                scope = self.ctx.intent.scope

                # Do work...
                return {"result": "done"}

        # Usage
        agent = MyAgent()
        result = agent.with_context(ctx).execute()
    """

    def with_context(self, ctx: SessionContext) -> "ContextAware":
        """
        Inject context before execution.

        Args:
            ctx: Session context with discovery, intent, execution settings

        Returns:
            Self for method chaining
        """
        ...

    def execute(self) -> Dict[str, Any]:
        """
        Execute agent with injected context.

        Must be called after with_context().

        Returns:
            Agent execution result as dict

        Raises:
            ValueError: If context not provided
        """
        ...


# Helper functions for common context operations

def validate_scope_consistency(ctx: SessionContext) -> None:
    """
    Validate that intent scope is consistent with discovery.

    Raises:
        ValueError: If scope contains undiscovered sources
    """
    discovered = set(ctx.discovery.sources)
    scope = set(ctx.intent.scope)

    undiscovered = scope - discovered
    if undiscovered:
        raise ValueError(
            f"Scope contains undiscovered sources: {undiscovered}. "
            f"Discovered: {discovered}"
        )


def filter_sources_by_scope(
    sources: Dict[str, Any],
    scope: List[str]
) -> Dict[str, Any]:
    """
    Filter sources dict to only include items in scope.

    Args:
        sources: Dict of source_name -> metadata
        scope: List of source names to include

    Returns:
        Filtered dict with only scoped sources

    Example:
        sources = {
            "fracfocus": {"records": 1000},
            "rrc": {"records": 2000},
            "usgs": {"records": 500}
        }
        scope = ["fracfocus", "rrc"]

        filtered = filter_sources_by_scope(sources, scope)
        # Returns: {"fracfocus": {...}, "rrc": {...}}
    """
    return {
        name: metadata
        for name, metadata in sources.items()
        if name in scope
    }


def merge_contexts(ctx1: SessionContext, ctx2: SessionContext) -> SessionContext:
    """
    Merge two session contexts (for multi-turn conversations).

    Uses ctx2's intent and execution, but merges discovery results.

    Args:
        ctx1: Previous session context
        ctx2: New session context

    Returns:
        Merged context
    """
    # Merge sources (union)
    merged_sources = list(set(ctx1.discovery.sources + ctx2.discovery.sources))

    # Merge record counts
    merged_counts = {**ctx1.discovery.record_counts, **ctx2.discovery.record_counts}

    # Use higher confidence
    merged_confidence = max(ctx1.discovery.confidence, ctx2.discovery.confidence)

    # Combine rationales
    merged_rationale = f"{ctx1.discovery.rationale}; {ctx2.discovery.rationale}"

    return SessionContext(
        session_id=ctx2.session_id,  # Use new session ID
        discovery=DiscoveryContext(
            sources=merged_sources,
            record_counts=merged_counts,
            discovery_confidence=merged_confidence,
            rationale=merged_rationale
        ),
        intent=ctx2.intent,  # Use new intent
        execution=ctx2.execution  # Use new execution settings
    )


# Example usage (for testing/documentation)
if __name__ == "__main__":
    import uuid

    # Create discovery context
    discovery = DiscoveryContext(
        sources=["fracfocus", "rrc"],
        record_counts={"fracfocus": 239059, "rrc": 18200},
        discovery_confidence=0.95,
        rationale="User requested petroleum chemical data from Texas"
    )

    # Create user intent
    intent = UserIntent(
        original_query="show fracfocus chemical data",
        parsed_intent="generate_dashboard",
        scope=["fracfocus"],  # Only use fracfocus (subset of discovered)
        task_type=TaskType.DASHBOARD,
        output_format=OutputFormat.REACT,
        filters={"state": "TX"}
    )

    # Create execution context
    execution = ExecutionContext(
        max_iterations=5,
        require_validation=True,
        trace_decisions=True
    )

    # Create session context
    ctx = SessionContext(
        session_id=str(uuid.uuid4()),
        discovery=discovery,
        intent=intent,
        execution=execution
    )

    # Serialize for logging
    print("Session Context:")
    print(f"  Session ID: {ctx.session_id}")
    print(f"  Discovered: {ctx.discovery.sources}")
    print(f"  Scope: {ctx.intent.scope}")
    print(f"  Task: {ctx.intent.task_type.value}")
    print(f"  Format: {ctx.intent.output_format.value}")

    # Validate
    validate_scope_consistency(ctx)
    print("\n✅ Context is valid!")

    # Filter sources by scope
    all_sources = {
        "fracfocus": {"type": "chemical", "records": 239059},
        "rrc": {"type": "production", "records": 18200}
    }

    scoped_sources = filter_sources_by_scope(all_sources, ctx.intent.scope)
    print(f"\nFiltered sources: {list(scoped_sources.keys())}")

    # Serialize
    serialized = ctx.to_dict()
    print(f"\nSerialized context has {len(serialized)} top-level keys")
