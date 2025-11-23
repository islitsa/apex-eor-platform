"""
DEPRECATED: This module has been moved to src.analyzers.pipeline_context_analyzer

This file exists for backwards compatibility only.
Please update your imports to:
    from src.analyzers.pipeline_context_analyzer import PipelineContextAnalyzer
"""

import warnings
from src.analyzers.pipeline_context_analyzer import (
    PipelineContextAnalyzer as AutoContextGenerator
)

warnings.warn(
    "src.utils.auto_context_generator is deprecated. "
    "Use src.analyzers.pipeline_context_analyzer instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ['AutoContextGenerator']