"""
Petroleum Domain Intent Router

This module provides deterministic rule-based routing for petroleum-specific queries.
It runs BEFORE the LLM filtering step to ensure petroleum domain queries are correctly
mapped to the RRC pipeline.

Key Features:
- Keyword-based petroleum context detection
- Prevents "production data" ambiguity (generic vs petroleum production)
- Falls back to LLM filtering when no petroleum context detected
- Logs routing decisions for debugging
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class PetroleumIntentRouter:
    """
    Routes petroleum-specific queries to the correct data pipeline.

    This router solves the problem where:
    - "production data" is ambiguous (could be manufacturing, software, or petroleum)
    - "well data" should map to RRC, not a generic "wells" folder
    - Petroleum terminology needs domain-aware routing
    """

    # Core petroleum/RRC keywords that indicate petroleum domain
    PETROLEUM_KEYWORDS = {
        # Regulatory & Organizations
        'rrc', 'railroad commission', 'texas rrc', 'trrc',

        # Well & Field Operations
        'well', 'wells', 'wellbore', 'drilling', 'completion',
        'oil well', 'gas well', 'injection well', 'disposal well',
        'horizontal well', 'vertical well', 'directional well',
        'field', 'oilfield', 'oil field', 'gas field',

        # Production Operations (context-dependent)
        'oil production', 'gas production', 'petroleum production',
        'producing well', 'producing wells', 'well production',
        'production data from wells', 'production from rrc',
        'hydrocarbon production', 'crude production',

        # Reservoir & Geology
        'reservoir', 'formation', 'permian', 'eagle ford', 'barnett',
        'haynesville', 'bakken', 'marcellus', 'zone', 'pay zone',

        # Petroleum Products
        'crude', 'crude oil', 'natural gas', 'condensate', 'ngls',
        'oil', 'gas', 'petroleum', 'hydrocarbon', 'hydrocarbons',
        'boe', 'barrel', 'mcf', 'mmcf', 'bcf',

        # Operations
        'operator', 'lease', 'permit', 'drilling permit',
        'completion', 'fracturing', 'fracing', 'stimulation',
        'workover', 'recompletion', 'plugging', 'abandonment',

        # Data Types
        'proration', 'allowable', 'g-1', 'g1', 'w-2', 'w2',
        'production report', 'drilling report', 'completion report'
    }

    # Generic "production" phrases that should NOT automatically map to RRC
    # unless petroleum context is present
    AMBIGUOUS_PRODUCTION_TERMS = {
        'production', 'production data', 'prod data', 'production metrics',
        'production stats', 'production statistics', 'production info'
    }

    # Non-petroleum contexts that should prevent RRC routing
    EXCLUSION_KEYWORDS = {
        'software production', 'manufacturing', 'factory', 'assembly line',
        'production deployment', 'production environment', 'prod server',
        'production build', 'production release'
    }

    def __init__(self):
        """Initialize the petroleum intent router."""
        self.route_count = 0
        self.rrc_route_count = 0

    def has_petroleum_context(self, prompt: str) -> bool:
        """
        Check if the prompt contains petroleum/RRC context.

        Args:
            prompt: User's natural language query

        Returns:
            True if petroleum context detected, False otherwise
        """
        prompt_lower = prompt.lower()

        # Check for exclusion keywords first
        for exclusion in self.EXCLUSION_KEYWORDS:
            if exclusion in prompt_lower:
                logger.info(f"[PETROLEUM_ROUTER] Exclusion keyword detected: '{exclusion}'")
                return False

        # Check for petroleum-specific keywords
        for keyword in self.PETROLEUM_KEYWORDS:
            if keyword in prompt_lower:
                logger.info(f"[PETROLEUM_ROUTER] Petroleum keyword detected: '{keyword}'")
                return True

        return False

    def is_ambiguous_production_query(self, prompt: str) -> bool:
        """
        Check if prompt contains ambiguous "production" terminology without
        petroleum context.

        Args:
            prompt: User's natural language query

        Returns:
            True if ambiguous production term found, False otherwise
        """
        prompt_lower = prompt.lower()

        # Check if any ambiguous term is present
        has_ambiguous = any(term in prompt_lower for term in self.AMBIGUOUS_PRODUCTION_TERMS)

        if has_ambiguous:
            # Check if petroleum context exists
            has_petroleum = self.has_petroleum_context(prompt)

            if not has_petroleum:
                logger.warning(
                    f"[PETROLEUM_ROUTER] Ambiguous production query without petroleum context: '{prompt}'"
                )
                return True

        return False

    def route(
        self,
        prompt: str,
        available_sources: List[Dict[str, Any]]
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Route the query to appropriate data sources based on petroleum domain detection.

        Args:
            prompt: User's natural language query
            available_sources: List of available data source dictionaries
                              (must have 'id' field)

        Returns:
            List of source dicts if petroleum routing applied, None if should fall back to LLM
        """
        self.route_count += 1

        # Check for petroleum context
        if not self.has_petroleum_context(prompt):
            logger.info(
                f"[PETROLEUM_ROUTER] No petroleum context detected. "
                f"Falling back to LLM filtering."
            )
            return None

        # Petroleum context detected - route to RRC pipeline
        rrc_sources = [
            source for source in available_sources
            if source.get('id', '').lower() in ['rrc', 'rrc_data', 'texas_rrc']
        ]

        if rrc_sources:
            self.rrc_route_count += 1
            logger.info(
                f"[PETROLEUM_ROUTER] ✓ Petroleum context detected. "
                f"Routing to RRC pipeline. (Route {self.rrc_route_count}/{self.route_count})"
            )
            logger.info(f"[PETROLEUM_ROUTER] Routed sources: {[s.get('id') for s in rrc_sources]}")
            return rrc_sources
        else:
            logger.warning(
                f"[PETROLEUM_ROUTER] Petroleum context detected but RRC source not available. "
                f"Available sources: {[s.get('id') for s in available_sources]}"
            )
            return None

    def validate_routing_decision(self, prompt: str, sources: List[str]) -> Dict[str, Any]:
        """
        Validate a routing decision and provide diagnostic information.

        Args:
            prompt: User's query
            sources: List of source IDs that were routed to

        Returns:
            Dictionary with validation results and diagnostics
        """
        has_petroleum = self.has_petroleum_context(prompt)
        is_ambiguous = self.is_ambiguous_production_query(prompt)

        # Check if RRC was routed
        rrc_routed = any('rrc' in s.lower() for s in sources)

        # Determine if routing was correct
        correct_routing = True
        issues = []

        if has_petroleum and not rrc_routed:
            correct_routing = False
            issues.append("Petroleum context detected but RRC not routed")

        if is_ambiguous and rrc_routed:
            correct_routing = False
            issues.append("Ambiguous production query incorrectly routed to RRC")

        if not has_petroleum and rrc_routed:
            correct_routing = False
            issues.append("No petroleum context but RRC was routed")

        return {
            'correct': correct_routing,
            'has_petroleum_context': has_petroleum,
            'is_ambiguous': is_ambiguous,
            'rrc_routed': rrc_routed,
            'routed_sources': sources,
            'issues': issues
        }

    def get_stats(self) -> Dict[str, Any]:
        """
        Get routing statistics for monitoring.

        Returns:
            Dictionary with routing statistics
        """
        rrc_percentage = (
            (self.rrc_route_count / self.route_count * 100)
            if self.route_count > 0 else 0
        )

        return {
            'total_routes': self.route_count,
            'rrc_routes': self.rrc_route_count,
            'rrc_percentage': round(rrc_percentage, 1),
            'llm_fallback_routes': self.route_count - self.rrc_route_count
        }


# Global instance
_router = None

def get_petroleum_router() -> PetroleumIntentRouter:
    """
    Get the global petroleum intent router instance.

    Returns:
        PetroleumIntentRouter instance
    """
    global _router
    if _router is None:
        _router = PetroleumIntentRouter()
    return _router


def route_petroleum_query(
    prompt: str,
    available_sources: List[Dict[str, Any]]
) -> Optional[List[Dict[str, Any]]]:
    """
    Convenience function for routing petroleum queries.

    Args:
        prompt: User's natural language query
        available_sources: List of available data source dictionaries

    Returns:
        List of source dicts if petroleum routing applied, None if should fall back to LLM
    """
    router = get_petroleum_router()
    return router.route(prompt, available_sources)
