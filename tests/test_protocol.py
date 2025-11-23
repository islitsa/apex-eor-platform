"""
Comprehensive tests for Protocol Layer (Phase 1)

Tests the type-safe context passing system that prevents:
- Missing context bugs
- Wrong sources bugs
- Type errors
"""

import pytest
import sys
from pathlib import Path
import uuid

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.agents.context.protocol import (
    SessionContext, DiscoveryContext, UserIntent,
    ExecutionContext, TaskType, OutputFormat,
    validate_scope_consistency, filter_sources_by_scope
)
from src.agents.react_developer import ReactDeveloperAgent
from src.agents.ux_designer import UXDesignerAgent
from src.agents.ui_orchestrator import UICodeOrchestrator


class TestProtocolTypes:
    """Test protocol type creation and validation"""

    def test_discovery_context_creation(self):
        """Test creating DiscoveryContext with valid data"""
        ctx = DiscoveryContext(
            sources=["fracfocus", "rrc"],
            record_counts={"fracfocus": 239059, "rrc": 18200},
            discovery_confidence=0.95,
            rationale="User requested petroleum data"
        )

        assert len(ctx.sources) == 2
        assert ctx.record_counts["fracfocus"] == 239059
        assert ctx.discovery_confidence == 0.95
        assert "petroleum" in ctx.rationale

    def test_discovery_context_validation_confidence(self):
        """Test that confidence must be 0.0-1.0"""
        with pytest.raises(ValueError, match="Confidence must be 0.0-1.0"):
            DiscoveryContext(
                sources=["test"],
                record_counts={"test": 100},
                discovery_confidence=1.5,  # Invalid!
                rationale="Test"
            )

    def test_discovery_context_validation_sources(self):
        """Test that sources list cannot be empty"""
        with pytest.raises(ValueError, match="at least one source"):
            DiscoveryContext(
                sources=[],  # Empty!
                record_counts={},
                discovery_confidence=0.9,
                rationale="Test"
            )

    def test_discovery_context_validation_record_counts(self):
        """Test that record_counts must match sources"""
        with pytest.raises(ValueError, match="missing from record_counts"):
            DiscoveryContext(
                sources=["fracfocus", "rrc"],
                record_counts={"fracfocus": 100},  # Missing rrc!
                discovery_confidence=0.9,
                rationale="Test"
            )

    def test_user_intent_with_scope(self):
        """Test creating UserIntent with scope"""
        intent = UserIntent(
            original_query="show fracfocus data",
            parsed_intent="generate_dashboard",
            scope=["fracfocus"],
            task_type=TaskType.DASHBOARD,
            output_format=OutputFormat.REACT
        )

        assert intent.scope == ["fracfocus"]
        assert intent.task_type == TaskType.DASHBOARD
        assert intent.output_format == OutputFormat.REACT

    def test_user_intent_validation_empty_query(self):
        """Test that original_query cannot be empty"""
        with pytest.raises(ValueError, match="cannot be empty"):
            UserIntent(
                original_query="",  # Empty!
                parsed_intent="test",
                scope=["test"],
                task_type=TaskType.DASHBOARD,
                output_format=OutputFormat.REACT
            )

    def test_user_intent_validation_empty_scope(self):
        """Test that scope cannot be empty"""
        with pytest.raises(ValueError, match="at least one source"):
            UserIntent(
                original_query="test",
                parsed_intent="test",
                scope=[],  # Empty!
                task_type=TaskType.DASHBOARD,
                output_format=OutputFormat.REACT
            )

    def test_execution_context_defaults(self):
        """Test ExecutionContext default values"""
        ctx = ExecutionContext()

        assert ctx.max_iterations == 5
        assert ctx.require_validation == True
        assert ctx.trace_decisions == True

    def test_execution_context_validation(self):
        """Test that max_iterations must be >= 1"""
        with pytest.raises(ValueError, match="max_iterations must be"):
            ExecutionContext(max_iterations=0)

    def test_session_context_creation(self):
        """Test creating complete SessionContext"""
        ctx = SessionContext(
            session_id=str(uuid.uuid4()),
            discovery=DiscoveryContext(
                sources=["fracfocus"],
                record_counts={"fracfocus": 239059},
                discovery_confidence=0.95,
                rationale="Test"
            ),
            intent=UserIntent(
                original_query="show fracfocus data",
                parsed_intent="generate_dashboard",
                scope=["fracfocus"],
                task_type=TaskType.DASHBOARD,
                output_format=OutputFormat.REACT
            ),
            execution=ExecutionContext()
        )

        assert ctx.session_id
        assert len(ctx.discovery.sources) == 1
        assert ctx.intent.scope == ["fracfocus"]

    def test_session_context_validation_scope_consistency(self):
        """Test that scope must be subset of discovered sources"""
        with pytest.raises(ValueError, match="undiscovered sources"):
            SessionContext(
                session_id="test",
                discovery=DiscoveryContext(
                    sources=["fracfocus"],  # Only fracfocus discovered
                    record_counts={"fracfocus": 1000},
                    discovery_confidence=0.9,
                    rationale="Test"
                ),
                intent=UserIntent(
                    original_query="test",
                    parsed_intent="test",
                    scope=["fracfocus", "rrc"],  # RRC not discovered!
                    task_type=TaskType.DASHBOARD,
                    output_format=OutputFormat.REACT
                ),
                execution=ExecutionContext()
            )

    def test_session_context_serialization(self):
        """Test SessionContext.to_dict() serialization"""
        ctx = SessionContext(
            session_id="test-123",
            discovery=DiscoveryContext(
                sources=["fracfocus"],
                record_counts={"fracfocus": 239059},
                discovery_confidence=0.95,
                rationale="Test"
            ),
            intent=UserIntent(
                original_query="test query",
                parsed_intent="test",
                scope=["fracfocus"],
                task_type=TaskType.DASHBOARD,
                output_format=OutputFormat.REACT
            ),
            execution=ExecutionContext()
        )

        serialized = ctx.to_dict()

        assert serialized["session_id"] == "test-123"
        assert "fracfocus" in serialized["discovery"]["sources"]
        assert serialized["intent"]["scope"] == ["fracfocus"]
        assert serialized["intent"]["task_type"] == "dashboard"


class TestHelperFunctions:
    """Test helper functions from protocol module"""

    def test_validate_scope_consistency_valid(self):
        """Test that validation passes for valid scope"""
        ctx = SessionContext(
            session_id="test",
            discovery=DiscoveryContext(
                sources=["fracfocus", "rrc"],
                record_counts={"fracfocus": 1000, "rrc": 2000},
                discovery_confidence=0.9,
                rationale="Test"
            ),
            intent=UserIntent(
                original_query="test",
                parsed_intent="test",
                scope=["fracfocus"],  # Subset is OK
                task_type=TaskType.DASHBOARD,
                output_format=OutputFormat.REACT
            ),
            execution=ExecutionContext()
        )

        # Should not raise
        validate_scope_consistency(ctx)

    def test_validate_scope_consistency_invalid(self):
        """Test that validation fails for invalid scope"""
        # Note: Validation happens during SessionContext creation,
        # so this test verifies the exception is raised correctly
        with pytest.raises(ValueError, match="undiscovered sources"):
            SessionContext(
                session_id="test",
                discovery=DiscoveryContext(
                    sources=["fracfocus"],
                    record_counts={"fracfocus": 1000},
                    discovery_confidence=0.9,
                    rationale="Test"
                ),
                intent=UserIntent(
                    original_query="test",
                    parsed_intent="test",
                    scope=["fracfocus", "undiscovered"],  # Invalid!
                    task_type=TaskType.DASHBOARD,
                    output_format=OutputFormat.REACT
                ),
                execution=ExecutionContext()
            )

    def test_filter_sources_by_scope(self):
        """Test filtering sources dict by scope"""
        sources = {
            "fracfocus": {"records": 1000},
            "rrc": {"records": 2000},
            "usgs": {"records": 500}
        }
        scope = ["fracfocus", "rrc"]

        filtered = filter_sources_by_scope(sources, scope)

        assert len(filtered) == 2
        assert "fracfocus" in filtered
        assert "rrc" in filtered
        assert "usgs" not in filtered


class TestContextAwareAgents:
    """Test that agents implement ContextAware protocol"""

    def test_react_agent_requires_context(self):
        """Test that ReactDeveloperAgent requires context"""
        agent = ReactDeveloperAgent()

        with pytest.raises(ValueError, match="Context not provided"):
            agent.execute()

    def test_ux_agent_requires_context(self):
        """Test that UXDesignerAgent requires context"""
        agent = UXDesignerAgent()

        with pytest.raises(ValueError, match="Context not provided"):
            agent.execute()

    def test_react_agent_with_context(self):
        """Test that ReactDeveloperAgent accepts context"""
        agent = ReactDeveloperAgent()

        ctx = SessionContext(
            session_id=str(uuid.uuid4()),
            discovery=DiscoveryContext(
                sources=["fracfocus"],
                record_counts={"fracfocus": 1000},
                discovery_confidence=0.9,
                rationale="Test"
            ),
            intent=UserIntent(
                original_query="test",
                parsed_intent="test",
                scope=["fracfocus"],
                task_type=TaskType.DASHBOARD,
                output_format=OutputFormat.REACT
            ),
            execution=ExecutionContext()
        )

        agent_with_ctx = agent.with_context(ctx)

        assert agent.ctx is not None
        assert agent.ctx.discovery.sources == ["fracfocus"]
        assert agent.ctx.intent.scope == ["fracfocus"]

    def test_ux_agent_with_context(self):
        """Test that UXDesignerAgent accepts context"""
        agent = UXDesignerAgent()

        ctx = SessionContext(
            session_id=str(uuid.uuid4()),
            discovery=DiscoveryContext(
                sources=["fracfocus"],
                record_counts={"fracfocus": 1000},
                discovery_confidence=0.9,
                rationale="Test"
            ),
            intent=UserIntent(
                original_query="test",
                parsed_intent="test",
                scope=["fracfocus"],
                task_type=TaskType.DASHBOARD,
                output_format=OutputFormat.REACT
            ),
            execution=ExecutionContext()
        )

        agent_with_ctx = agent.with_context(ctx)

        assert agent.ctx is not None
        assert agent.ctx.intent.scope == ["fracfocus"]


class TestScopeFiltering:
    """Test that scope filtering works correctly"""

    def test_react_agent_filters_by_scope(self):
        """Test that ReactDeveloperAgent filters sources by scope"""
        agent = ReactDeveloperAgent()

        ctx = SessionContext(
            session_id="test",
            discovery=DiscoveryContext(
                sources=["fracfocus", "rrc"],  # Discovered both
                record_counts={"fracfocus": 1000, "rrc": 2000},
                discovery_confidence=0.9,
                rationale="Test"
            ),
            intent=UserIntent(
                original_query="show fracfocus data",
                parsed_intent="generate_dashboard",
                scope=["fracfocus"],  # But scope is only fracfocus!
                task_type=TaskType.DASHBOARD,
                output_format=OutputFormat.REACT
            ),
            execution=ExecutionContext()
        )

        agent.with_context(ctx)

        # Get legacy dict to check scope
        legacy_dict = agent._context_to_legacy_dict()

        assert "fracfocus" in legacy_dict["scope"]
        assert len(legacy_dict["scope"]) == 1
        # Verify data_sources matches scope
        assert "fracfocus" in legacy_dict["data_sources"]


class TestOrchestrator:
    """Test UICodeOrchestrator context building"""

    def test_orchestrator_builds_context(self):
        """Test that orchestrator creates valid SessionContext"""
        orch = UICodeOrchestrator()

        requirements = {
            "intent": "show fracfocus data",
            "screen_type": "dashboard",
            "data_sources": {
                "fracfocus": {"row_count": 239059}
            }
        }

        ctx = orch._build_session_context(requirements, {}, {})

        assert ctx.discovery.sources == ["fracfocus"]
        assert ctx.intent.scope == ["fracfocus"]
        assert ctx.intent.task_type == TaskType.DASHBOARD
        assert ctx.discovery.record_counts["fracfocus"] == 239059

    def test_orchestrator_infers_task_types(self):
        """Test that orchestrator correctly infers task types"""
        orch = UICodeOrchestrator()

        assert orch._infer_task_type("dashboard") == TaskType.DASHBOARD
        assert orch._infer_task_type("data_dashboard") == TaskType.DASHBOARD
        assert orch._infer_task_type("analysis_view") == TaskType.ANALYSIS
        assert orch._infer_task_type("report") == TaskType.REPORT
        assert orch._infer_task_type("unknown") == TaskType.DASHBOARD  # Default


class TestEnumTypes:
    """Test TaskType and OutputFormat enums"""

    def test_task_type_values(self):
        """Test TaskType enum values"""
        assert TaskType.DASHBOARD.value == "dashboard"
        assert TaskType.ANALYSIS.value == "analysis"
        assert TaskType.REPORT.value == "report"

    def test_output_format_values(self):
        """Test OutputFormat enum values"""
        assert OutputFormat.REACT.value == "react"
        assert OutputFormat.STREAMLIT.value == "streamlit"
        assert OutputFormat.JUPYTER.value == "jupyter"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
