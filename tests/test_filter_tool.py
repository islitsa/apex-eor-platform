"""
Tests for DataFilterTool - Phase 1.0

These tests verify that the centralized filtering tool behaves exactly like
the original scattered filtering logic in the orchestrator.
"""

import pytest
from src.agents.tools.filter_tool import DataFilterTool


class TestFilterByPrompt:
    """Test prompt-based source detection"""

    def test_basic_source_detection(self):
        """Should detect sources mentioned in prompt"""
        tool = DataFilterTool()
        intent = "Create a dashboard for fracfocus and rrc"
        all_sources = ["fracfocus", "rrc", "usgs"]

        selected = tool.filter_by_prompt(intent, all_sources)
        assert selected == ["fracfocus", "rrc"]

    def test_case_insensitive_matching(self):
        """Should match sources case-insensitively"""
        tool = DataFilterTool()
        intent = "Show me FRACFOCUS data"
        all_sources = ["fracfocus", "rrc"]

        selected = tool.filter_by_prompt(intent, all_sources)
        assert selected == ["fracfocus"]

    def test_no_matches_returns_none(self):
        """Should return None when no sources mentioned (meaning 'show all')"""
        tool = DataFilterTool()
        intent = "Create a generic dashboard"
        all_sources = ["fracfocus", "rrc"]

        selected = tool.filter_by_prompt(intent, all_sources)
        assert selected is None

    def test_empty_intent_returns_none(self):
        """Should return None for empty intent"""
        tool = DataFilterTool()
        intent = ""
        all_sources = ["fracfocus", "rrc"]

        selected = tool.filter_by_prompt(intent, all_sources)
        assert selected is None

    def test_empty_sources_returns_none(self):
        """Should return None when no sources available"""
        tool = DataFilterTool()
        intent = "Show fracfocus data"
        all_sources = []

        selected = tool.filter_by_prompt(intent, all_sources)
        assert selected is None

    def test_substring_matching(self):
        """Should match sources as substrings (current behavior)"""
        tool = DataFilterTool()
        intent = "production data"
        all_sources = ["fracfocus", "production", "rrc"]

        selected = tool.filter_by_prompt(intent, all_sources)
        assert "production" in selected


class TestFilterPipelines:
    """Test pipeline filtering by source IDs"""

    def test_basic_pipeline_filtering(self):
        """Should filter pipelines by ID"""
        tool = DataFilterTool()
        pipelines = [
            {"id": "fracfocus", "metrics": {}},
            {"id": "rrc", "metrics": {}},
            {"id": "usgs", "metrics": {}},
        ]
        selected = ["rrc", "usgs"]

        filtered = tool.filter_pipelines(pipelines, selected)
        ids = [p["id"] for p in filtered]
        assert set(ids) == {"rrc", "usgs"}

    def test_preserves_pipeline_order(self):
        """Should preserve original pipeline order"""
        tool = DataFilterTool()
        pipelines = [
            {"id": "fracfocus"},
            {"id": "rrc"},
            {"id": "usgs"},
        ]
        selected = ["usgs", "fracfocus"]  # Different order

        filtered = tool.filter_pipelines(pipelines, selected)
        ids = [p["id"] for p in filtered]
        # Should maintain original order: fracfocus, usgs
        assert ids == ["fracfocus", "usgs"]

    def test_none_sources_returns_all(self):
        """Should return all pipelines when selected_sources is None"""
        tool = DataFilterTool()
        pipelines = [
            {"id": "fracfocus"},
            {"id": "rrc"},
        ]

        filtered = tool.filter_pipelines(pipelines, None)
        assert filtered == pipelines

    def test_empty_sources_returns_all(self):
        """Should return all pipelines when selected_sources is empty"""
        tool = DataFilterTool()
        pipelines = [
            {"id": "fracfocus"},
            {"id": "rrc"},
        ]

        filtered = tool.filter_pipelines(pipelines, [])
        assert filtered == pipelines


class TestFilterDesignSpec:
    """Test design_spec.data_sources filtering"""

    def test_basic_design_spec_filtering(self):
        """Should filter design_spec.data_sources by pipeline IDs"""
        class DummySpec:
            def __init__(self):
                self.data_sources = {
                    "fracfocus": {"records": 1000},
                    "rrc": {"records": 2000},
                    "usgs": {"records": 3000},
                }

        tool = DataFilterTool()
        spec = DummySpec()

        tool.filter_design_spec(spec, ["rrc", "usgs"])
        assert set(spec.data_sources.keys()) == {"rrc", "usgs"}

    def test_empty_pipeline_ids_clears_sources(self):
        """Should clear data_sources when no pipelines survive"""
        class DummySpec:
            def __init__(self):
                self.data_sources = {"fracfocus": {}}

        tool = DataFilterTool()
        spec = DummySpec()

        tool.filter_design_spec(spec, [])
        assert spec.data_sources == {}

    def test_no_data_sources_returns_unchanged(self):
        """Should return spec unchanged if no data_sources attribute"""
        class DummySpec:
            def __init__(self):
                self.other_field = "value"

        tool = DataFilterTool()
        spec = DummySpec()

        result = tool.filter_design_spec(spec, ["rrc"])
        assert result == spec
        assert not hasattr(result, "data_sources")

    def test_returns_same_object(self):
        """Should mutate and return the same design_spec object"""
        class DummySpec:
            def __init__(self):
                self.data_sources = {"fracfocus": {}}

        tool = DataFilterTool()
        spec = DummySpec()

        result = tool.filter_design_spec(spec, ["fracfocus"])
        assert result is spec  # Same object


class TestFilterContextSources:
    """Test context['data_sources'] filtering"""

    def test_basic_context_filtering(self):
        """Should filter context['data_sources'] by pipeline IDs"""
        tool = DataFilterTool()
        ctx = {
            "data_sources": {
                "fracfocus": {"records": 1000},
                "rrc": {"records": 2000},
                "usgs": {"records": 3000},
            },
            "user_prompt": "test"
        }

        new_ctx = tool.filter_context_sources(ctx, ["rrc"])
        assert set(new_ctx["data_sources"].keys()) == {"rrc"}
        assert new_ctx["user_prompt"] == "test"  # Other fields preserved

    def test_empty_pipeline_ids_clears_sources(self):
        """Should clear data_sources when no pipelines survive"""
        tool = DataFilterTool()
        ctx = {"data_sources": {"fracfocus": {}}}

        new_ctx = tool.filter_context_sources(ctx, [])
        assert new_ctx["data_sources"] == {}

    def test_no_data_sources_returns_unchanged(self):
        """Should return context unchanged if no data_sources"""
        tool = DataFilterTool()
        ctx = {"user_prompt": "test"}

        new_ctx = tool.filter_context_sources(ctx, ["rrc"])
        assert new_ctx == ctx

    def test_returns_same_object(self):
        """Should mutate and return the same context dict"""
        tool = DataFilterTool()
        ctx = {"data_sources": {"fracfocus": {}}}

        result = tool.filter_context_sources(ctx, ["fracfocus"])
        assert result is ctx  # Same object

    def test_preserves_other_fields(self):
        """Should only modify data_sources, not other fields"""
        tool = DataFilterTool()
        ctx = {
            "data_sources": {
                "fracfocus": {},
                "rrc": {},
            },
            "user_prompt": "test",
            "gradient_context": {},
            "knowledge": {}
        }

        tool.filter_context_sources(ctx, ["rrc"])
        assert ctx["user_prompt"] == "test"
        assert "gradient_context" in ctx
        assert "knowledge" in ctx


class TestIntegration:
    """Integration tests combining multiple filter operations"""

    def test_full_filtering_workflow(self):
        """Test complete filtering workflow as used in orchestrator"""
        tool = DataFilterTool()

        # Step 1: Parse prompt for sources
        intent = "Show production data from rrc"
        all_sources = ["fracfocus", "rrc", "production", "usgs"]
        filter_sources = tool.filter_by_prompt(intent, all_sources)
        assert set(filter_sources) == {"rrc", "production"}

        # Step 2: Filter API pipelines
        pipelines = [
            {"id": "fracfocus", "metrics": {}},
            {"id": "rrc", "metrics": {}},
            {"id": "production", "metrics": {}},
            {"id": "usgs", "metrics": {}},
        ]
        filtered_pipelines = tool.filter_pipelines(pipelines, filter_sources)
        assert len(filtered_pipelines) == 2

        # Step 3: Filter design spec
        class DummySpec:
            def __init__(self):
                self.data_sources = {
                    "fracfocus": {},
                    "rrc": {},
                    "production": {},
                    "usgs": {},
                }

        spec = DummySpec()
        pipeline_ids = [p["id"] for p in filtered_pipelines]
        tool.filter_design_spec(spec, pipeline_ids)
        assert set(spec.data_sources.keys()) == {"rrc", "production"}

        # Step 4: Filter context
        ctx = {
            "data_sources": {
                "fracfocus": {},
                "rrc": {},
                "production": {},
                "usgs": {},
            }
        }
        tool.filter_context_sources(ctx, pipeline_ids)
        assert set(ctx["data_sources"].keys()) == {"rrc", "production"}


class TestFilterPipelinesByDesignSpec:
    """Test pipeline filtering by discovered source names (Issue 2 fix - Phase 1.1)"""

    def test_basic_filtering_by_source_names(self):
        """Should filter pipelines by discovered source names"""
        tool = DataFilterTool()
        pipelines = [
            {"id": "fracfocus", "display_name": "FracFocus"},
            {"id": "rrc", "display_name": "RRC"},
            {"id": "usgs", "display_name": "USGS"},
        ]
        discovered_sources = ["rrc", "fracfocus"]

        filtered = tool.filter_pipelines_by_design_spec(pipelines, discovered_sources)
        ids = [p["id"] for p in filtered]
        assert set(ids) == {"rrc", "fracfocus"}

    def test_case_insensitive_matching(self):
        """Should match case-insensitively"""
        tool = DataFilterTool()
        pipelines = [
            {"id": "fracfocus", "display_name": "FRACFOCUS"},
            {"id": "rrc", "display_name": "RRC"},
        ]
        discovered_sources = ["fracfocus"]  # lowercase

        filtered = tool.filter_pipelines_by_design_spec(pipelines, discovered_sources)
        assert len(filtered) == 1
        assert filtered[0]["id"] == "fracfocus"

    def test_substring_matching_in_display_name(self):
        """Should match if source name is substring of display_name"""
        tool = DataFilterTool()
        pipelines = [
            {"id": "rrc_prod", "display_name": "RRC Production Data"},
            {"id": "usgs", "display_name": "USGS"},
        ]
        discovered_sources = ["rrc"]

        filtered = tool.filter_pipelines_by_design_spec(pipelines, discovered_sources)
        assert len(filtered) == 1
        assert filtered[0]["id"] == "rrc_prod"

    def test_fallback_to_id_when_no_display_name(self):
        """Should use id when display_name is missing"""
        tool = DataFilterTool()
        pipelines = [
            {"id": "fracfocus"},  # No display_name
            {"id": "rrc"},
        ]
        discovered_sources = ["fracfocus"]

        filtered = tool.filter_pipelines_by_design_spec(pipelines, discovered_sources)
        assert len(filtered) == 1
        assert filtered[0]["id"] == "fracfocus"

    def test_empty_discovered_sources_returns_all(self):
        """Should return all pipelines when discovered_sources is empty"""
        tool = DataFilterTool()
        pipelines = [
            {"id": "fracfocus", "display_name": "FracFocus"},
            {"id": "rrc", "display_name": "RRC"},
        ]

        filtered = tool.filter_pipelines_by_design_spec(pipelines, [])
        assert filtered == pipelines

    def test_none_discovered_sources_returns_all(self):
        """Should return all pipelines when discovered_sources is None"""
        tool = DataFilterTool()
        pipelines = [
            {"id": "fracfocus", "display_name": "FracFocus"},
            {"id": "rrc", "display_name": "RRC"},
        ]

        filtered = tool.filter_pipelines_by_design_spec(pipelines, None)
        assert filtered == pipelines

    def test_no_matches_returns_empty(self):
        """Should return empty list when no pipelines match"""
        tool = DataFilterTool()
        pipelines = [
            {"id": "fracfocus", "display_name": "FracFocus"},
            {"id": "rrc", "display_name": "RRC"},
        ]
        discovered_sources = ["usgs"]  # Not in pipelines

        filtered = tool.filter_pipelines_by_design_spec(pipelines, discovered_sources)
        assert filtered == []

    def test_preserves_pipeline_order(self):
        """Should preserve original pipeline order"""
        tool = DataFilterTool()
        pipelines = [
            {"id": "fracfocus", "display_name": "FracFocus"},
            {"id": "rrc", "display_name": "RRC"},
            {"id": "production", "display_name": "Production"},
        ]
        discovered_sources = ["production", "fracfocus"]  # Different order

        filtered = tool.filter_pipelines_by_design_spec(pipelines, discovered_sources)
        ids = [p["id"] for p in filtered]
        # Should maintain original order: fracfocus, production
        assert ids == ["fracfocus", "production"]

    def test_multiple_source_matching(self):
        """Should match pipelines that contain any of the source names"""
        tool = DataFilterTool()
        pipelines = [
            {"id": "fracfocus", "display_name": "FracFocus"},
            {"id": "rrc", "display_name": "RRC"},
            {"id": "production", "display_name": "Production"},
            {"id": "usgs", "display_name": "USGS"},
        ]
        discovered_sources = ["rrc", "production"]

        filtered = tool.filter_pipelines_by_design_spec(pipelines, discovered_sources)
        ids = [p["id"] for p in filtered]
        assert set(ids) == {"rrc", "production"}
