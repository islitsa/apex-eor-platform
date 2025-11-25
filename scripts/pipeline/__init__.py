"""
Data ingestion pipeline orchestration

This package contains the main pipeline orchestration logic for:
- Extraction (unzipping, decompressing archives)
- Parsing (converting to structured formats)
- Validation (data quality checks)
"""

from .extract import ExtractionOrchestrator
from .parse import ParsingOrchestrator

__all__ = ['ExtractionOrchestrator', 'ParsingOrchestrator']
