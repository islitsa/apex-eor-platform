
"""
APEX EOR Scientific Discovery Platform
"""

__version__ = "1.0.0"

from .attribution.attribution_engine import AttributionEngine
from .validation.multi_agent_validator import MultiAgentValidator
from .hypothesis.hypothesis_generator import HypothesisGenerator
from .linear_inflow.inflow_calculator import LinearInflowAnalyzer

__all__ = [
    'AttributionEngine',
    'MultiAgentValidator',
    'HypothesisGenerator',
    'LinearInflowAnalyzer'
]

