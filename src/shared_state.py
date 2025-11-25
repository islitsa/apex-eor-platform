"""
Shared State Manager for APEX EOR Platform

Provides a lightweight state management system for sharing context
between the data ingestion pipeline and UI generation tools.

This module handles:
- Pipeline context persistence
- State freshness checking
- Cross-tool communication
- User preferences storage
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
import os


class PipelineState:
    """
    Shared state manager for pipeline context and UI tools communication.

    Uses a simple file-based approach for maximum compatibility and simplicity.
    State is stored in user home directory to persist across sessions.
    """

    # State file location - in user home for persistence
    STATE_DIR = Path.home() / '.apex_eor'
    STATE_FILE = STATE_DIR / 'pipeline_state.json'
    CONTEXT_FILE = STATE_DIR / 'pipeline_context.json'
    PREFERENCES_FILE = STATE_DIR / 'user_preferences.json'

    # Stale threshold - context older than this is considered stale
    STALE_HOURS = 24

    @classmethod
    def ensure_directories(cls):
        """Ensure state directories exist"""
        cls.STATE_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def save_context(cls, context: Dict) -> bool:
        """
        Save pipeline context for UI tools to consume.

        Args:
            context: Pipeline context dictionary

        Returns:
            True if saved successfully, False otherwise
        """
        cls.ensure_directories()

        try:
            # Add metadata
            state = {
                'context': context,
                'timestamp': datetime.now().isoformat(),
                'version': '2.0'
            }

            # Save to both files for compatibility
            with open(cls.STATE_FILE, 'w') as f:
                json.dump(state, f, indent=2)

            with open(cls.CONTEXT_FILE, 'w') as f:
                json.dump(context, f, indent=2)

            print(f"[OK] Context saved to {cls.STATE_FILE}")
            return True

        except Exception as e:
            print(f"[ERROR] Error saving context: {e}")
            return False

    @classmethod
    def load_context(cls, check_freshness: bool = True) -> Optional[Dict]:
        """
        Load pipeline context for UI tools.

        Args:
            check_freshness: If True, warn about stale context

        Returns:
            Context dictionary or None if not found/error
        """
        if not cls.STATE_FILE.exists():
            # Try legacy location for backward compatibility
            if cls.CONTEXT_FILE.exists():
                try:
                    with open(cls.CONTEXT_FILE, 'r') as f:
                        return json.load(f)
                except:
                    pass
            return None

        try:
            with open(cls.STATE_FILE, 'r') as f:
                state = json.load(f)

            # Check freshness if requested
            if check_freshness:
                timestamp = datetime.fromisoformat(state['timestamp'])
                age = datetime.now() - timestamp

                if age > timedelta(hours=cls.STALE_HOURS):
                    hours_old = int(age.total_seconds() / 3600)
                    print(f"[WARNING] Context is {hours_old} hours old (threshold: {cls.STALE_HOURS} hours)")
                    print(f"   Consider running: python run_ingestion.py --generate-context")
                else:
                    hours_old = int(age.total_seconds() / 3600)
                    print(f"[OK] Context loaded ({hours_old} hours old)")

            return state.get('context')

        except Exception as e:
            print(f"[ERROR] Error loading context: {e}")
            return None

    @classmethod
    def get_context_age(cls) -> Optional[timedelta]:
        """
        Get age of current context.

        Returns:
            Age as timedelta or None if no context exists
        """
        if not cls.STATE_FILE.exists():
            return None

        try:
            with open(cls.STATE_FILE, 'r') as f:
                state = json.load(f)

            timestamp = datetime.fromisoformat(state['timestamp'])
            return datetime.now() - timestamp

        except Exception:
            return None

    @classmethod
    def is_context_fresh(cls, max_age_hours: int = None) -> bool:
        """
        Check if context is fresh enough.

        Args:
            max_age_hours: Maximum age in hours (default: STALE_HOURS)

        Returns:
            True if context exists and is fresh, False otherwise
        """
        if max_age_hours is None:
            max_age_hours = cls.STALE_HOURS

        age = cls.get_context_age()
        if age is None:
            return False

        return age < timedelta(hours=max_age_hours)

    @classmethod
    def save_preferences(cls, preferences: Dict) -> bool:
        """
        Save user preferences.

        Args:
            preferences: User preferences dictionary

        Returns:
            True if saved successfully, False otherwise
        """
        cls.ensure_directories()

        try:
            # Load existing preferences if they exist
            existing = {}
            if cls.PREFERENCES_FILE.exists():
                with open(cls.PREFERENCES_FILE, 'r') as f:
                    existing = json.load(f)

            # Merge with new preferences
            existing.update(preferences)
            existing['last_updated'] = datetime.now().isoformat()

            # Save
            with open(cls.PREFERENCES_FILE, 'w') as f:
                json.dump(existing, f, indent=2)

            return True

        except Exception as e:
            print(f"Error saving preferences: {e}")
            return False

    @classmethod
    def load_preferences(cls) -> Dict:
        """
        Load user preferences.

        Returns:
            Preferences dictionary (empty dict if none exist)
        """
        if not cls.PREFERENCES_FILE.exists():
            return {}

        try:
            with open(cls.PREFERENCES_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    @classmethod
    def clear_state(cls) -> bool:
        """
        Clear all saved state.

        Returns:
            True if cleared successfully, False otherwise
        """
        try:
            if cls.STATE_FILE.exists():
                cls.STATE_FILE.unlink()
            if cls.CONTEXT_FILE.exists():
                cls.CONTEXT_FILE.unlink()
            print("[OK] State cleared")
            return True
        except Exception as e:
            print(f"Error clearing state: {e}")
            return False

    @classmethod
    def get_summary(cls) -> Dict[str, Any]:
        """
        Get a summary of current state.

        Returns:
            Dictionary with state summary
        """
        summary = {
            'has_context': cls.STATE_FILE.exists() or cls.CONTEXT_FILE.exists(),
            'context_age': None,
            'is_fresh': False,
            'has_preferences': cls.PREFERENCES_FILE.exists(),
            'state_directory': str(cls.STATE_DIR)
        }

        age = cls.get_context_age()
        if age:
            summary['context_age'] = str(age).split('.')[0]  # Remove microseconds
            summary['is_fresh'] = cls.is_context_fresh()
            summary['age_hours'] = int(age.total_seconds() / 3600)

        return summary

    @classmethod
    def require_context(cls) -> Dict:
        """
        Load context or raise an error if not available.

        Returns:
            Context dictionary

        Raises:
            RuntimeError: If no context is available
        """
        context = cls.load_context()
        if context is None:
            raise RuntimeError(
                "No pipeline context found.\n"
                "Please run: python run_ingestion.py --generate-context\n"
                "Or: python run_ingestion.py --all"
            )
        return context


class FavoritesManager:
    """
    Manage favorite UI iterations.
    Allows users to save and reload their favorite dashboard designs.
    """

    FAVORITES_FILE = PipelineState.STATE_DIR / 'favorites.json'

    @classmethod
    def save_favorite(cls, name: str, code: str, prompt: str = "", tags: list = None) -> bool:
        """
        Save a favorite UI iteration.

        Args:
            name: Friendly name for this favorite
            code: Generated Gradio code
            prompt: Original prompt used
            tags: Optional tags for organization

        Returns:
            True if saved successfully, False otherwise
        """
        PipelineState.ensure_directories()

        try:
            # Load existing favorites
            favorites = cls.load_favorites()

            # Create favorite entry
            favorite = {
                'name': name,
                'code': code,
                'prompt': prompt,
                'tags': tags or [],
                'saved_at': datetime.now().isoformat(),
                'code_length': len(code)
            }

            # Add to favorites (replace if name exists)
            favorites[name] = favorite

            # Save
            with open(cls.FAVORITES_FILE, 'w') as f:
                json.dump(favorites, f, indent=2)

            return True

        except Exception as e:
            print(f"Error saving favorite: {e}")
            return False

    @classmethod
    def load_favorites(cls) -> Dict[str, Dict]:
        """
        Load all favorites.

        Returns:
            Dictionary of favorites (name -> favorite data)
        """
        if not cls.FAVORITES_FILE.exists():
            return {}

        try:
            with open(cls.FAVORITES_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    @classmethod
    def get_favorite(cls, name: str) -> Optional[Dict]:
        """
        Get a specific favorite by name.

        Args:
            name: Name of the favorite

        Returns:
            Favorite data or None if not found
        """
        favorites = cls.load_favorites()
        return favorites.get(name)

    @classmethod
    def delete_favorite(cls, name: str) -> bool:
        """
        Delete a favorite.

        Args:
            name: Name of the favorite to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            favorites = cls.load_favorites()
            if name in favorites:
                del favorites[name]
                with open(cls.FAVORITES_FILE, 'w') as f:
                    json.dump(favorites, f, indent=2)
                return True
            return False
        except Exception:
            return False

    @classmethod
    def list_favorites(cls) -> List[str]:
        """
        Get list of favorite names.

        Returns:
            List of favorite names sorted by most recent
        """
        favorites = cls.load_favorites()
        # Sort by saved_at timestamp (most recent first)
        sorted_favs = sorted(
            favorites.items(),
            key=lambda x: x[1].get('saved_at', ''),
            reverse=True
        )
        return [name for name, _ in sorted_favs]


class SessionState:
    """
    Manage UI session state that should persist across tool launches.
    Separate from pipeline context for UI-specific data.
    """

    SESSION_FILE = PipelineState.STATE_DIR / 'ui_session.json'

    @classmethod
    def save_session(cls, session_data: Dict) -> bool:
        """Save UI session data"""
        PipelineState.ensure_directories()

        try:
            session_data['timestamp'] = datetime.now().isoformat()

            with open(cls.SESSION_FILE, 'w') as f:
                json.dump(session_data, f, indent=2)

            return True
        except Exception:
            return False

    @classmethod
    def load_session(cls) -> Optional[Dict]:
        """Load UI session data"""
        if not cls.SESSION_FILE.exists():
            return None

        try:
            with open(cls.SESSION_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return None

    @classmethod
    def update_session(cls, **kwargs) -> bool:
        """Update specific session values"""
        session = cls.load_session() or {}
        session.update(kwargs)
        return cls.save_session(session)


def print_state_info():
    """Print current state information (useful for debugging)"""
    print("\n" + "="*60)
    print("APEX EOR Platform - State Information")
    print("="*60)

    summary = PipelineState.get_summary()

    print(f"State Directory: {summary['state_directory']}")
    print(f"Has Context:     {summary['has_context']}")

    if summary['has_context']:
        print(f"Context Age:     {summary.get('age_hours', 'Unknown')} hours")
        print(f"Is Fresh:        {summary['is_fresh']}")

    print(f"Has Preferences: {summary['has_preferences']}")

    # Try to load and show context summary
    context = PipelineState.load_context(check_freshness=False)
    if context:
        print("\nContext Summary:")
        if 'summary' in context:
            print(f"  Datasets:  {context['summary'].get('datasets_available', 0)}")
            print(f"  Records:   {context['summary'].get('human_readable_records', 'Unknown')}")
            print(f"  Size:      {context['summary'].get('human_readable_size', 'Unknown')}")
        else:
            print(f"  Sources:   {len(context.get('data_sources', {}))}")

    print("="*60 + "\n")


if __name__ == "__main__":
    # If run directly, print state information
    print_state_info()
