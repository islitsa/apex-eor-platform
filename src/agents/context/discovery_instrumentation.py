"""
Discovery Instrumentation - Performance tracking and bottleneck detection

This module instruments discovery tools to track:
1. Where discovery fails to find files (missing files)
2. Where discovery searches wrong locations (navigation errors)
3. How long each operation takes (performance bottlenecks)
4. What gradient context information would help (gap analysis)

Purpose: Identify where path coordinates are needed in gradient context
"""

import time
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
import traceback


@dataclass
class DiscoveryAttempt:
    """Single discovery attempt tracking"""
    timestamp: str
    method: str  # 'find_data_sources', 'get_schema', 'explore_directory', etc.
    query: str
    success: bool
    duration_ms: float
    results_count: int

    # Navigation tracking
    searched_locations: List[str]  # Where did we look?
    expected_location: Optional[str]  # Where did we expect to find it?
    actual_location: Optional[str]  # Where did we actually find it?

    # Error tracking
    error: Optional[str]
    error_type: Optional[str]  # 'not_found', 'permission_denied', 'timeout', etc.

    # Gradient context analysis
    had_gradient_hint: bool  # Did gradient context provide hints?
    gradient_hint_type: Optional[str]  # 'structure', 'root_path', 'file_pattern', etc.
    gradient_hint_useful: bool  # Did the hint help?
    missing_hint_type: Optional[str]  # What hint would have helped?


@dataclass
class DiscoverySession:
    """Complete discovery session (multiple attempts)"""
    session_id: str
    start_time: str
    end_time: Optional[str]
    total_attempts: int
    successful_attempts: int
    failed_attempts: int
    total_duration_ms: float

    attempts: List[DiscoveryAttempt]

    # Summary statistics
    avg_duration_ms: float
    success_rate: float

    # Bottleneck analysis
    slowest_operations: List[Dict[str, Any]]
    failed_operations: List[Dict[str, Any]]
    navigation_errors: List[Dict[str, Any]]  # Searched wrong places

    # Gradient context gaps
    missing_path_hints: int  # How many times we needed path coordinates
    missing_structure_hints: int  # How many times we needed directory structure
    missing_file_hints: int  # How many times we needed file patterns


class DiscoveryInstrumentor:
    """
    Instruments discovery tools to track performance and identify gaps.

    Usage:
        instrumentor = DiscoveryInstrumentor()

        # Wrap discovery operations
        with instrumentor.track_operation('find_data_sources', query='chemical data') as tracker:
            results = discovery_tools.find_data_sources('chemical data')
            tracker.record_success(results, searched=['/data/raw/fracfocus'])
    """

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize instrumentor.

        Args:
            output_dir: Directory to save instrumentation logs
        """
        self.output_dir = output_dir or Path(__file__).parent.parent.parent.parent / 'logs' / 'discovery'
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.current_session = None
        self.attempts: List[DiscoveryAttempt] = []

        print(f"[Discovery Instrumentation] Initialized - logs: {self.output_dir}")

    def start_session(self, session_id: Optional[str] = None) -> str:
        """Start a new discovery session"""
        session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_session = session_id
        self.attempts = []

        print(f"\n{'='*80}")
        print(f"[Discovery Session] Starting: {session_id}")
        print(f"{'='*80}\n")

        return session_id

    def end_session(self) -> DiscoverySession:
        """End current session and generate report"""
        if not self.current_session:
            raise ValueError("No active session")

        end_time = datetime.now().isoformat()

        # Calculate statistics
        total_attempts = len(self.attempts)
        successful_attempts = sum(1 for a in self.attempts if a.success)
        failed_attempts = total_attempts - successful_attempts
        total_duration_ms = sum(a.duration_ms for a in self.attempts)
        avg_duration_ms = total_duration_ms / total_attempts if total_attempts > 0 else 0
        success_rate = successful_attempts / total_attempts if total_attempts > 0 else 0

        # Identify bottlenecks
        slowest_operations = sorted(
            [{'method': a.method, 'query': a.query, 'duration_ms': a.duration_ms}
             for a in self.attempts],
            key=lambda x: x['duration_ms'],
            reverse=True
        )[:5]

        # Identify failures
        failed_operations = [
            {
                'method': a.method,
                'query': a.query,
                'error': a.error,
                'error_type': a.error_type,
                'searched_locations': a.searched_locations
            }
            for a in self.attempts if not a.success
        ]

        # Identify navigation errors (searched wrong places)
        navigation_errors = [
            {
                'method': a.method,
                'query': a.query,
                'searched': a.searched_locations,
                'expected': a.expected_location,
                'actual': a.actual_location
            }
            for a in self.attempts
            if a.expected_location and a.actual_location and a.expected_location != a.actual_location
        ]

        # Gradient context gaps
        missing_path_hints = sum(1 for a in self.attempts if a.missing_hint_type == 'path')
        missing_structure_hints = sum(1 for a in self.attempts if a.missing_hint_type == 'structure')
        missing_file_hints = sum(1 for a in self.attempts if a.missing_hint_type == 'file_pattern')

        session = DiscoverySession(
            session_id=self.current_session,
            start_time=self.attempts[0].timestamp if self.attempts else datetime.now().isoformat(),
            end_time=end_time,
            total_attempts=total_attempts,
            successful_attempts=successful_attempts,
            failed_attempts=failed_attempts,
            total_duration_ms=total_duration_ms,
            attempts=self.attempts,
            avg_duration_ms=avg_duration_ms,
            success_rate=success_rate,
            slowest_operations=slowest_operations,
            failed_operations=failed_operations,
            navigation_errors=navigation_errors,
            missing_path_hints=missing_path_hints,
            missing_structure_hints=missing_structure_hints,
            missing_file_hints=missing_file_hints
        )

        # Save to file
        self._save_session(session)

        # Print summary
        self._print_summary(session)

        # Reset
        self.current_session = None
        self.attempts = []

        return session

    def track_operation(
        self,
        method: str,
        query: str,
        gradient_hint: Optional[Dict[str, Any]] = None
    ):
        """
        Context manager for tracking a discovery operation.

        Usage:
            with instrumentor.track_operation('find_data_sources', 'chemical data') as tracker:
                results = tools.find_data_sources('chemical data')
                tracker.record_success(results, searched=['/data/raw'])
        """
        return OperationTracker(self, method, query, gradient_hint)

    def record_attempt(self, attempt: DiscoveryAttempt):
        """Record a discovery attempt"""
        self.attempts.append(attempt)

        # Print real-time feedback (using ASCII for Windows compatibility)
        status = "OK" if attempt.success else "FAIL"
        duration_str = f"{attempt.duration_ms:.1f}ms"

        print(f"  [{status}] {attempt.method}: '{attempt.query}' ({duration_str})")
        if not attempt.success:
            print(f"      Error: {attempt.error_type} - {attempt.error}")
        if attempt.searched_locations:
            print(f"      Searched: {', '.join(attempt.searched_locations[:3])}")
        if attempt.missing_hint_type:
            print(f"      Missing hint: {attempt.missing_hint_type}")

    def _save_session(self, session: DiscoverySession):
        """Save session to JSON file"""
        filename = f"{session.session_id}.json"
        filepath = self.output_dir / filename

        # Convert to dict (handling numpy arrays if any)
        session_dict = asdict(session)

        with open(filepath, 'w') as f:
            json.dump(session_dict, f, indent=2)

        print(f"\n[Discovery Instrumentation] Session saved: {filepath}")

    def _print_summary(self, session: DiscoverySession):
        """Print session summary"""
        print(f"\n{'='*80}")
        print(f"[Discovery Session] Summary: {session.session_id}")
        print(f"{'='*80}")

        print(f"\n Overall Statistics:")
        print(f"  Total attempts: {session.total_attempts}")
        print(f"  Successful: {session.successful_attempts} ({session.success_rate*100:.1f}%)")
        print(f"  Failed: {session.failed_attempts}")
        print(f"  Total duration: {session.total_duration_ms:.1f}ms")
        print(f"  Average duration: {session.avg_duration_ms:.1f}ms")

        if session.slowest_operations:
            print(f"\n   Slowest Operations:")
            for i, op in enumerate(session.slowest_operations[:3], 1):
                print(f"  {i}. {op['method']}: '{op['query']}' ({op['duration_ms']:.1f}ms)")

        if session.failed_operations:
            print(f"\n Failed Operations:")
            for i, op in enumerate(session.failed_operations[:3], 1):
                print(f"  {i}. {op['method']}: '{op['query']}'")
                print(f"      Error: {op['error_type']}")
                if op['searched_locations']:
                    print(f"      Searched: {', '.join(op['searched_locations'][:2])}")

        if session.navigation_errors:
            print(f"\n Navigation Errors (searched wrong locations):")
            for i, error in enumerate(session.navigation_errors[:3], 1):
                print(f"  {i}. {error['method']}: '{error['query']}'")
                print(f"      Expected: {error['expected']}")
                print(f"      Actually found at: {error['actual']}")

        print(f"\n Gradient Context Gaps:")
        print(f"  Missing path coordinates: {session.missing_path_hints}")
        print(f"  Missing structure hints: {session.missing_structure_hints}")
        print(f"  Missing file patterns: {session.missing_file_hints}")

        print(f"\n{'='*80}\n")


class OperationTracker:
    """Context manager for tracking individual operations"""

    def __init__(
        self,
        instrumentor: DiscoveryInstrumentor,
        method: str,
        query: str,
        gradient_hint: Optional[Dict[str, Any]] = None
    ):
        self.instrumentor = instrumentor
        self.method = method
        self.query = query
        self.gradient_hint = gradient_hint
        self.start_time = None

        # Track what we're recording
        self.searched_locations: List[str] = []
        self.expected_location: Optional[str] = None
        self.actual_location: Optional[str] = None
        self.results = None
        self.error = None
        self.error_type = None
        self.missing_hint_type = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000

        # Determine success
        success = exc_type is None and self.error is None

        # Extract error info
        if exc_type:
            self.error = str(exc_val)
            self.error_type = exc_type.__name__

        # Analyze gradient hints
        had_gradient_hint = self.gradient_hint is not None
        gradient_hint_type = None
        gradient_hint_useful = False

        if self.gradient_hint:
            # Determine what type of hint we had
            if 'root_path' in self.gradient_hint:
                gradient_hint_type = 'root_path'
            elif 'structure' in self.gradient_hint:
                gradient_hint_type = 'structure'
            elif 'file_pattern' in self.gradient_hint:
                gradient_hint_type = 'file_pattern'

            # Check if hint was useful (actual location matched hint)
            if self.actual_location and gradient_hint_type == 'root_path':
                hint_path = self.gradient_hint.get('root_path', '')
                gradient_hint_useful = hint_path in self.actual_location

        # Determine what hint we needed
        if not success and not gradient_hint_useful:
            # We failed - what hint would have helped?
            if self.error_type in ['FileNotFoundError', 'not_found']:
                self.missing_hint_type = 'path'  # Needed path coordinates
            elif len(self.searched_locations) > 5:
                self.missing_hint_type = 'structure'  # Searched too many places
            elif self.actual_location and self.expected_location:
                self.missing_hint_type = 'path'  # Searched wrong place

        # Count results
        results_count = 0
        if self.results is not None:
            if isinstance(self.results, list):
                results_count = len(self.results)
            elif isinstance(self.results, dict):
                results_count = 1

        # Create attempt record
        attempt = DiscoveryAttempt(
            timestamp=datetime.now().isoformat(),
            method=self.method,
            query=self.query,
            success=success,
            duration_ms=duration_ms,
            results_count=results_count,
            searched_locations=self.searched_locations,
            expected_location=self.expected_location,
            actual_location=self.actual_location,
            error=self.error,
            error_type=self.error_type,
            had_gradient_hint=had_gradient_hint,
            gradient_hint_type=gradient_hint_type,
            gradient_hint_useful=gradient_hint_useful,
            missing_hint_type=self.missing_hint_type
        )

        self.instrumentor.record_attempt(attempt)

        # Don't suppress exceptions
        return False

    def record_success(
        self,
        results: Any,
        searched: Optional[List[str]] = None,
        actual_location: Optional[str] = None,
        expected_location: Optional[str] = None
    ):
        """Record successful operation"""
        self.results = results
        self.searched_locations = searched or []
        self.actual_location = actual_location
        self.expected_location = expected_location

    def record_failure(
        self,
        error: str,
        error_type: str,
        searched: Optional[List[str]] = None,
        expected_location: Optional[str] = None
    ):
        """Record failed operation"""
        self.error = error
        self.error_type = error_type
        self.searched_locations = searched or []
        self.expected_location = expected_location


# Convenience function for analyzing existing logs
def analyze_discovery_logs(logs_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Analyze all discovery logs to identify patterns.

    Returns summary of:
    - Most common failure types
    - Most common navigation errors
    - What gradient hints would help most
    """
    logs_dir = logs_dir or Path(__file__).parent.parent.parent.parent / 'logs' / 'discovery'

    if not logs_dir.exists():
        return {'error': 'No logs directory found'}

    all_sessions = []
    for log_file in logs_dir.glob('*.json'):
        with open(log_file) as f:
            all_sessions.append(json.load(f))

    if not all_sessions:
        return {'error': 'No session logs found'}

    # Aggregate statistics
    total_sessions = len(all_sessions)
    total_attempts = sum(s['total_attempts'] for s in all_sessions)
    total_failures = sum(s['failed_attempts'] for s in all_sessions)

    # Most common errors
    error_types = {}
    for session in all_sessions:
        for op in session.get('failed_operations', []):
            error_type = op.get('error_type', 'unknown')
            error_types[error_type] = error_types.get(error_type, 0) + 1

    # Most needed hints
    total_path_hints_needed = sum(s.get('missing_path_hints', 0) for s in all_sessions)
    total_structure_hints_needed = sum(s.get('missing_structure_hints', 0) for s in all_sessions)
    total_file_hints_needed = sum(s.get('missing_file_hints', 0) for s in all_sessions)

    return {
        'total_sessions': total_sessions,
        'total_attempts': total_attempts,
        'total_failures': total_failures,
        'failure_rate': total_failures / total_attempts if total_attempts > 0 else 0,
        'most_common_errors': sorted(error_types.items(), key=lambda x: x[1], reverse=True),
        'gradient_hints_needed': {
            'path_coordinates': total_path_hints_needed,
            'directory_structure': total_structure_hints_needed,
            'file_patterns': total_file_hints_needed
        }
    }


if __name__ == "__main__":
    # Test instrumentation
    instrumentor = DiscoveryInstrumentor()
    session_id = instrumentor.start_session()

    # Simulate some discovery operations
    with instrumentor.track_operation('find_data_sources', 'chemical data') as tracker:
        tracker.record_success(
            results=['fracfocus', 'lab_data'],
            searched=['/data/raw', '/data/raw/fracfocus'],
            actual_location='/data/raw/fracfocus'
        )

    with instrumentor.track_operation('get_schema', 'fracfocus') as tracker:
        tracker.record_failure(
            error='No parsed files found',
            error_type='not_found',
            searched=['/data/fracfocus', '/data/raw/fracfocus'],
            expected_location='/data/raw/fracfocus/Chemical_data/parsed'
        )

    # End session
    session = instrumentor.end_session()

    print(f"\nTest session complete: {session.session_id}")
