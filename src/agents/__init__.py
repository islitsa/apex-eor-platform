"""
APEX EOR Platform - AI Agents

Collection of specialized AI agents for the APEX platform.
"""

# Import only if modules exist
try:
    from .ui_agent import UIAgent, create_ui
    __all__ = ['UIAgent', 'create_ui']
except ImportError:
    __all__ = []

__version__ = '0.1.0'
