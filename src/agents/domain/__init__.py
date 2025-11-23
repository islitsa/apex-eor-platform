"""
Domain-specific intent routing modules.

This package contains specialized routers that handle domain-specific
terminology and intent before falling back to LLM-based filtering.
"""

from .petroleum_intent_router import (
    PetroleumIntentRouter,
    get_petroleum_router,
    route_petroleum_query
)

__all__ = [
    'PetroleumIntentRouter',
    'get_petroleum_router',
    'route_petroleum_query'
]
