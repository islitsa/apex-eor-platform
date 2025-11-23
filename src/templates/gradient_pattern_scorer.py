"""
Lightweight Semantic Field for Pattern Scoring Augmentation

This module provides domain-aware semantic scoring to enhance pattern matching.
NO LLM tokens - pure algorithmic enhancement.

Architecture Compliance:
- Zero tokens (pure keyword matching)
- No changes to two-agent pattern
- Optional enhancement (can be disabled)
- No component generation (only scoring)
"""

from typing import Dict, List, Tuple


class SemanticFieldScorer:
    """
    Augments keyword-based pattern scoring with domain semantic awareness.

    Features:
    - Phase detection (normal, emergency, maintenance)
    - Domain concept mapping (safety, pressure, pipeline, production, reservoir)
    - Context-aware boost factors
    - Zero LLM tokens (pure algorithmic)
    """

    def __init__(self, domain: str = "petroleum_engineering"):
        """
        Initialize semantic field scorer

        Args:
            domain: Domain for semantic concepts (default: petroleum_engineering)
        """
        self.domain = domain
        self.phase = "normal"
        self.phase_history: List[Tuple[str, str]] = []

        # Domain concept keyword mappings
        # These are domain-specific semantic attractors
        self.domain_concepts = self._initialize_domain_concepts()

    def _initialize_domain_concepts(self) -> Dict[str, List[str]]:
        """Initialize domain-specific concept keyword mappings"""

        if self.domain == "petroleum_engineering":
            return {
                "safety": [
                    "alarm", "emergency", "h2s", "shutdown", "hazard",
                    "esd", "relief", "critical", "leak", "fire",
                    "gas", "toxic", "evacuation", "incident"
                ],
                "pressure": [
                    "psi", "bar", "gauge", "sensor", "overpressure",
                    "pressure", "transmitter", "measurement", "monitoring",
                    "wellhead", "annular", "casing"
                ],
                "pipeline": [
                    "flow", "corrosion", "pig", "integrity", "diameter",
                    "pipeline", "pipeline", "flowline", "gathering",
                    "inspection", "pigging", "cleaning"
                ],
                "production": [
                    "barrels", "rate", "decline", "eur", "bpd",
                    "production", "oil", "gas", "water", "yield",
                    "output", "throughput", "performance"
                ],
                "reservoir": [
                    "porosity", "permeability", "saturation", "formation",
                    "reservoir", "rock", "geology", "lithology",
                    "well", "completion", "stimulation"
                ]
            }

        # Generic fallback for non-petroleum domains
        return {}

    def detect_phase(self, requirements: Dict) -> str:
        """
        Detect operational phase from requirements (0 tokens)

        Args:
            requirements: User requirements dict

        Returns:
            Phase string: "emergency", "maintenance", or "normal"
        """
        # Convert requirements to searchable text
        text = str(requirements).lower()

        # Emergency phase indicators
        emergency_indicators = [
            "emergency", "alarm", "shutdown", "critical", "leak",
            "h2s", "fire", "explosion", "blowout", "hazard",
            "immediate", "urgent", "danger"
        ]

        emergency_count = sum(1 for indicator in emergency_indicators if indicator in text)
        if emergency_count >= 1:
            return "emergency"

        # Maintenance phase indicators
        maintenance_indicators = [
            "maintenance", "inspection", "repair", "pigging",
            "turnaround", "shutdown", "overhaul", "service",
            "preventive", "scheduled", "routine"
        ]

        maintenance_count = sum(1 for indicator in maintenance_indicators if indicator in text)
        if maintenance_count >= 1:
            return "maintenance"

        return "normal"

    def get_boost_factors(self) -> Dict[str, float]:
        """
        Get concept boost factors for current phase

        Returns:
            Dict mapping concept names to boost multipliers
        """
        if self.phase == "emergency":
            # Emergency: heavily prioritize safety and pressure monitoring
            return {
                "safety": 3.0,
                "pressure": 2.0,
                "pipeline": 1.5,
                "production": 0.8,
                "reservoir": 0.5
            }

        elif self.phase == "maintenance":
            # Maintenance: prioritize pipeline integrity and safety
            return {
                "pipeline": 2.5,
                "safety": 1.5,
                "pressure": 1.3,
                "production": 0.9,
                "reservoir": 0.7
            }

        else:  # normal
            # Normal operations: slight petroleum engineering bias
            return {
                "pressure": 1.1,
                "production": 1.1,
                "pipeline": 1.0,
                "safety": 1.0,
                "reservoir": 1.0
            }

    def calculate_concept_alignment(self, pattern_id: str, requirements: Dict) -> int:
        """
        Calculate semantic alignment score between pattern and requirements

        Args:
            pattern_id: Pattern identifier
            requirements: User requirements dict

        Returns:
            Integer score representing semantic alignment
        """
        pattern_lower = pattern_id.lower()
        req_text = str(requirements).lower()

        boost_factors = self.get_boost_factors()
        total_augmentation = 0

        for concept, keywords in self.domain_concepts.items():
            # How many concept keywords appear in pattern?
            pattern_matches = sum(1 for kw in keywords if kw in pattern_lower)

            # How many concept keywords appear in requirements?
            req_matches = sum(1 for kw in keywords if kw in req_text)

            if pattern_matches > 0 and req_matches > 0:
                # Both pattern and requirements align with this concept
                boost = boost_factors.get(concept, 1.0)

                # Calculate augmentation:
                # - Base: product of matches (pattern × requirements)
                # - Multiplied by phase-aware boost factor
                # - Converted to integer for compatibility
                augmentation = int(pattern_matches * req_matches * boost)
                total_augmentation += augmentation

        return total_augmentation

    def augment_score(self, pattern_id: str, base_score: int, requirements: Dict) -> int:
        """
        Augment pattern score with semantic field influence

        This is the main entry point called by SnippetAssembler.

        REBALANCING STRATEGY (Opus feedback):
        - Detect M3 patterns (already have 3x multiplier bonus)
        - Give STRONGER boosts to non-M3 domain patterns to compete
        - Add phase-specific SUPER BOOSTS for critical domain contexts

        Args:
            pattern_id: Pattern identifier
            base_score: Score from keyword matching
            requirements: User requirements dict

        Returns:
            Augmented score (integer for compatibility)
        """
        # Update phase if needed
        detected_phase = self.detect_phase(requirements)
        if detected_phase != self.phase:
            self.phase = detected_phase
            # Track phase changes for debugging
            req_preview = str(requirements)[:100]
            self.phase_history.append((detected_phase, req_preview))

        # Detect if this is an M3 pattern (already has 3x multiplier)
        is_m3_pattern = "_m3" in pattern_id.lower()

        # Calculate semantic alignment
        alignment_score = self.calculate_concept_alignment(pattern_id, requirements)

        # REBALANCING: Double boost for non-M3 domain patterns to compete with M3
        if not is_m3_pattern and alignment_score > 0:
            alignment_score *= 2
            print(f"  [Gradient Boost] Non-M3 pattern '{pattern_id}' doubled: +{alignment_score}")

        # SUPER BOOSTS for phase-specific critical patterns
        req_text = str(requirements).lower()
        pattern_lower = pattern_id.lower()

        if self.phase == "emergency" and "safety" in pattern_lower and not is_m3_pattern:
            # Emergency domain patterns get huge boost
            alignment_score += 20
            print(f"  [Gradient] EMERGENCY SUPER BOOST: +20 for {pattern_id}")

        elif self.phase == "maintenance" and "pipeline" in pattern_lower and not is_m3_pattern:
            # Maintenance domain patterns get big boost
            alignment_score += 15
            print(f"  [Gradient] MAINTENANCE SUPER BOOST: +15 for {pattern_id}")

        elif "pipeline" in pattern_lower and ("monitoring" in req_text or "etl" in req_text or "status" in req_text):
            # Pipeline monitoring context - boost pipeline-specific patterns
            alignment_score += 12
            print(f"  [Gradient] PIPELINE MONITORING BOOST: +12 for {pattern_id}")

        # Return augmented score
        augmented = base_score + alignment_score

        return augmented

    def get_diagnostic_info(self) -> Dict:
        """
        Get diagnostic information about scorer state

        Returns:
            Dict with diagnostic information
        """
        return {
            "domain": self.domain,
            "current_phase": self.phase,
            "phase_history": self.phase_history,
            "boost_factors": self.get_boost_factors(),
            "concepts": list(self.domain_concepts.keys())
        }
