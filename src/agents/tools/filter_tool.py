"""
DataFilterTool - Centralized filtering logic for the orchestrator

This tool consolidates ALL filtering logic that was previously scattered across
the UICodeOrchestrator (5 different locations). It ensures that prompt-based
filtering, pipeline filtering, design spec filtering, context filtering, and
design-spec-based pipeline filtering all happen consistently through a single interface.

Phase: 1.0 (Behavior-preserving extraction)
Phase 1.1: Issue 2 fix - Extracted remaining inline filtering block
Phase 1.6: Semantic intent parsing fix - distinguish source vs domain
"""

from __future__ import annotations

import re
from typing import List, Optional, Dict, Any


class DataFilterTool:
    """
    Consolidates ALL filtering logic for the orchestrator.

    Responsibilities (mapped to old orchestrator locations):
    - filter_by_prompt                    ← prompt-based source detection (lines ~697–715)
    - filter_pipelines                    ← API pipeline filtering by selected sources (lines ~296–309)
    - filter_design_spec                  ← align design_spec.data_sources with pipelines (lines ~799–808)
    - filter_context_sources              ← align context['data_sources'] with pipelines (lines ~822–834)
    - filter_pipelines_by_design_spec     ← filter pipelines by discovered sources (Issue 2 fix - Phase 1.1)

    Design Principles:
    - Behavior-preserving: Matches existing orchestrator logic exactly
    - Single responsibility: Each method handles one filtering concern
    - Testable: Small, focused methods with clear inputs/outputs
    - 100% externalized: No filtering logic remains in orchestrator (as of Phase 1.1)
    - Phase 1.6: Semantic intent parsing to distinguish source vs domain
    """

    # ------------------------------------------------------------------
    # 0) Semantic Intent Parser (Phase 1.6)
    # ------------------------------------------------------------------
    def parse_intent(self, prompt: str, all_sources: List[str]) -> Dict[str, Any]:
        """
        Parse user prompt to distinguish between data SOURCE and data DOMAIN.

        CRITICAL FIX: "production data from rrc" should map to:
            source: "rrc"
            domain: "production"
        NOT to sources: ["rrc", "production"]

        The word "production" in natural language refers to the DOMAIN/TYPE of data,
        not necessarily the pipeline named "production".

        Args:
            prompt: User's natural language request
            all_sources: List of available pipeline source IDs

        Returns:
            {
                "source": str | None,        # Primary data source (pipeline ID)
                "domain": str | None,        # Domain/context (e.g., "production", "chemicals")
                "is_multi_source": bool      # True if user explicitly wants multiple sources
            }

        Examples:
            "production data from rrc" → source="rrc", domain="production"
            "fracfocus chemicals" → source="fracfocus", domain="chemicals"
            "rrc and production pipelines" → sources=["rrc", "production"], is_multi_source=True
            "show all sources" → source=None (no filter)
        """
        prompt_lower = prompt.lower()

        # Domain keywords that are NOT pipeline sources
        domain_keywords = {
            "production": ["production data", "production metrics", "production records"],
            "chemicals": ["chemical", "fracfocus"],
            "injection": ["injection data", "injection records"],
            "allocation": ["allocation", "allocations"]
        }

        # 1. Check for explicit multi-source requests
        multi_source_patterns = [
            r"\band\b",           # "rrc and production"
            r",",                 # "rrc, production"
            r"multiple",          # "multiple sources"
            r"all.*sources",      # "all sources"
            r"both"               # "both sources"
        ]

        is_multi_source = any(re.search(pattern, prompt_lower) for pattern in multi_source_patterns)

        # 2. Detect domain intent (context clues, not necessarily source)
        domain = None
        for domain_name, patterns in domain_keywords.items():
            for pattern in patterns:
                if pattern in prompt_lower:
                    domain = domain_name
                    break
            if domain:
                break

        # 3. Detect primary source
        # Use word boundaries to avoid false matches
        source = None
        for src in all_sources:
            # Build pattern: must match as whole word or be preceded by "from"/"in"
            # This prevents "production" the word from matching "production" the pipeline
            # unless user explicitly says "production pipeline"

            # Special handling for "production" - only match if explicitly a pipeline reference
            if src == "production":
                if re.search(r"production\s+(pipeline|source|dataset)", prompt_lower):
                    source = src
                    break
                # If "from" or "in" precedes production, skip it (likely domain context)
                elif re.search(r"(from|in|of)\s+\w+.*production", prompt_lower):
                    continue
                # If we already have another source and production appears, it's likely domain
                elif domain == "production":
                    continue

            # For all other sources, use word boundary matching
            if re.search(rf"\b{src}\b", prompt_lower):
                source = src
                break

        # 4. If multi-source request, return all mentioned sources
        if is_multi_source:
            mentioned_sources = [
                src for src in all_sources
                if re.search(rf"\b{src}\b", prompt_lower)
            ]
            return {
                "sources": mentioned_sources if mentioned_sources else None,
                "domain": domain,
                "is_multi_source": True
            }

        # 5. Single source request
        return {
            "source": source,
            "domain": domain,
            "is_multi_source": False
        }

    # ------------------------------------------------------------------
    # 1) Prompt → source list
    # ------------------------------------------------------------------
    def filter_by_prompt(
        self,
        intent: str,
        all_sources: List[str],
    ) -> Optional[List[str]]:
        """
        Given the user prompt (intent) and list of available source IDs,
        return the subset of sources explicitly mentioned in the prompt.

        Phase 1.6: NOW USES SEMANTIC INTENT PARSING
        - Distinguishes between SOURCE (pipeline ID) and DOMAIN (data context)
        - "production data from rrc" → source="rrc", NOT ["rrc", "production"]
        - "rrc and production pipelines" → sources=["rrc", "production"]
        - Returns None if nothing is explicitly mentioned (meaning "no filter")

        Args:
            intent: User's prompt/request text
            all_sources: List of all available source IDs (e.g., ['fracfocus', 'rrc', 'usgs'])

        Returns:
            List of source IDs mentioned in prompt, or None if no specific sources mentioned

        Example:
            intent = "production data from rrc"
            all_sources = ["fracfocus", "rrc", "production"]
            -> ["rrc"]  # NOT ["rrc", "production"]

            intent = "rrc and production pipelines"
            all_sources = ["fracfocus", "rrc", "production"]
            -> ["rrc", "production"]

            intent = "Create a generic dashboard"
            all_sources = ["fracfocus", "rrc"]
            -> None (no specific sources mentioned)
        """
        if not intent or not all_sources:
            return None

        # Use semantic intent parser (Phase 1.6)
        parsed = self.parse_intent(intent, all_sources)

        # Multi-source request
        if parsed["is_multi_source"]:
            return parsed.get("sources")

        # Single source request
        if parsed.get("source"):
            return [parsed["source"]]

        # No specific source mentioned
        return None

    # ------------------------------------------------------------------
    # 2) Filter pipelines by selected sources
    # ------------------------------------------------------------------
    def filter_pipelines(
        self,
        pipelines: List[Dict[str, Any]],
        selected_sources: Optional[List[str]],
    ) -> List[Dict[str, Any]]:
        """
        Filter API `pipelines` based on selected source IDs.

        This encapsulates the behavior currently in _fetch_data_context when
        `filter_sources` is provided.

        Rules:
        - If selected_sources is None or empty → return pipelines unchanged
        - Otherwise, only keep pipelines whose `id` is in selected_sources

        Args:
            pipelines: List of pipeline dicts from API
            selected_sources: List of source IDs to keep, or None for no filtering

        Returns:
            Filtered list of pipelines

        Example:
            pipelines = [
                {"id": "fracfocus", "metrics": {...}},
                {"id": "rrc", "metrics": {...}},
                {"id": "usgs", "metrics": {...}}
            ]
            selected_sources = ["rrc", "fracfocus"]
            -> [{"id": "fracfocus", ...}, {"id": "rrc", ...}]
        """
        if not pipelines or not selected_sources:
            return pipelines

        selected_set = set(selected_sources)
        filtered = [p for p in pipelines if p.get("id") in selected_set]

        return filtered

    # ------------------------------------------------------------------
    # 3) Filter design_spec.data_sources to match pipeline ids
    # ------------------------------------------------------------------
    def filter_design_spec(
        self,
        design_spec: Any,
        pipeline_ids: List[str],
    ) -> Any:
        """
        Filter design_spec.data_sources so that it only contains entries
        whose keys are present in `pipeline_ids`.

        This is the safe, centralized version of the logic that lived in
        the orchestrator after pipeline filtering.

        Behavior:
        - If design_spec has no data_sources → return as-is
        - Otherwise, keep only entries with keys in pipeline_ids
        - Mutates design_spec.data_sources in-place AND returns design_spec

        Args:
            design_spec: UX Designer's design spec object
            pipeline_ids: List of pipeline IDs that survived filtering

        Returns:
            The same design_spec object (mutated)

        Example:
            design_spec.data_sources = {
                "fracfocus": {...},
                "rrc": {...},
                "usgs": {...}
            }
            pipeline_ids = ["rrc"]
            -> design_spec.data_sources = {"rrc": {...}}
        """
        if not hasattr(design_spec, "data_sources") or not design_spec.data_sources:
            return design_spec

        if not pipeline_ids:
            # No pipelines survived → clear data_sources entirely
            design_spec.data_sources = {}
            return design_spec

        allowed = set(pipeline_ids)
        filtered_sources = {
            k: v for k, v in design_spec.data_sources.items()
            if k in allowed
        }

        design_spec.data_sources = filtered_sources
        return design_spec

    # ------------------------------------------------------------------
    # 4) Filter context['data_sources'] to match pipeline ids
    # ------------------------------------------------------------------
    def filter_context_sources(
        self,
        context: Dict[str, Any],
        pipeline_ids: List[str],
    ) -> Dict[str, Any]:
        """
        Filter context['data_sources'] so that it only includes entries whose
        keys are present in `pipeline_ids`.

        This corresponds to the final step in the orchestrator where the
        builder context was aligned with the filtered pipelines.

        Behavior:
        - If context has no 'data_sources' → return unchanged
        - If pipeline_ids is empty → data_sources becomes {}
        - Otherwise, keep only entries with keys in pipeline_ids

        Args:
            context: Context dict passed to builder
            pipeline_ids: List of pipeline IDs that survived filtering

        Returns:
            The same context dict (mutated)

        Example:
            context = {
                "data_sources": {
                    "fracfocus": {...},
                    "rrc": {...},
                    "usgs": {...}
                },
                "user_prompt": "..."
            }
            pipeline_ids = ["rrc"]
            -> context = {
                "data_sources": {"rrc": {...}},
                "user_prompt": "..."
            }
        """
        if not context:
            return context

        data_sources = context.get("data_sources")
        if not isinstance(data_sources, dict) or not data_sources:
            return context

        if not pipeline_ids:
            context["data_sources"] = {}
            return context

        allowed = set(pipeline_ids)
        filtered_sources = {
            k: v for k, v in data_sources.items()
            if k in allowed
        }

        context["data_sources"] = filtered_sources
        return context

    # ------------------------------------------------------------------
    # 5) Filter pipelines by discovered source names from design spec
    # ------------------------------------------------------------------
    def filter_pipelines_by_design_spec(
        self,
        pipelines: List[Dict[str, Any]],
        discovered_source_names: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Filter pipelines based on source names discovered in design_spec.

        This filters pipelines to only include those whose display_name or id
        contains one of the discovered source names. This is the behavior that
        was previously inline in the orchestrator (Issue 2).

        Behavior:
        - Matches if any discovered source name appears in pipeline's display_name or id
        - Case-insensitive matching
        - Returns all pipelines if discovered_source_names is empty

        Args:
            pipelines: List of pipeline dicts from data_context
            discovered_source_names: List of source names from design_spec.data_sources.keys()

        Returns:
            Filtered list of pipelines

        Example:
            pipelines = [
                {"id": "fracfocus", "display_name": "FracFocus"},
                {"id": "rrc", "display_name": "RRC"},
                {"id": "usgs", "display_name": "USGS"}
            ]
            discovered_source_names = ["rrc", "fracfocus"]
            -> [{"id": "fracfocus", ...}, {"id": "rrc", ...}]
        """
        if not pipelines or not discovered_source_names:
            return pipelines

        filtered = [
            p for p in pipelines
            if any(
                source_name.lower() in p.get('display_name', p.get('id', '')).lower()
                for source_name in discovered_source_names
            )
        ]

        return filtered
