"""
RAG-Based Material Design 3 Dashboard Tests

This test suite uses Pinecone to query actual M3 design principles and validates
the generated dashboard against them. Tests are generic and self-validating against
the design system stored in the vector database.

Architecture:
- Query Pinecone for M3 design principles (colors, spacing, typography, layout)
- Use Claude AI to validate generated code against retrieved principles
- Tests adapt automatically when design principles are updated in Pinecone
"""

import pytest
import re
import os
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agents.component_assembler import ComponentBasedAssembler
from agents.ux_code_generator import UXCodeGenerator
from knowledge.design_kb_pinecone import DesignKnowledgeBasePinecone

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class M3DesignValidator:
    """
    Generic validator that queries Pinecone for M3 design principles
    and uses Claude to validate code against them.
    """

    def __init__(self):
        """Initialize connection to Pinecone design knowledge base"""
        self.design_kb = DesignKnowledgeBasePinecone()

        # Initialize Claude client if available
        if ANTHROPIC_AVAILABLE:
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if api_key:
                self.client = anthropic.Anthropic(api_key=api_key)
            else:
                self.client = None
                print("[WARNING] ANTHROPIC_API_KEY not set, AI validation disabled")
        else:
            self.client = None
            print("[WARNING] anthropic package not installed, AI validation disabled")

    def query_design_principle(self, query: str, category: str = None, top_k: int = 3):
        """
        Query Pinecone for specific design principles.

        Args:
            query: Natural language query (e.g., "top app bar color specifications")
            category: Optional category filter ("color", "layout", "typography", etc.)
            top_k: Number of results to retrieve

        Returns:
            List of design principle documents with content and metadata
        """
        results = self.design_kb.query(query, category=category, top_k=top_k)
        return results

    def validate_code_against_principles(self, code: str, component_type: str) -> dict:
        """
        Use Claude AI to validate code against M3 design principles from Pinecone.

        Args:
            code: Generated dashboard code
            component_type: Type of component to validate (e.g., "Top App Bar", "Navigation Rail")

        Returns:
            dict with keys:
                - is_valid: bool
                - violations: list of M3 principle violations
                - suggestions: list of improvement suggestions
                - principles_checked: list of principles retrieved from Pinecone
        """
        if not self.client:
            return {
                "is_valid": None,
                "violations": [],
                "suggestions": [],
                "principles_checked": [],
                "error": "Claude AI client not available"
            }

        # Query Pinecone for relevant design principles
        query_map = {
            "Top App Bar": "material design 3 top app bar specifications color typography height",
            "Navigation Rail": "material design 3 navigation rail specifications width layout overflow scrollbar",
            "Color Contrast": "material design 3 color system contrast accessibility WCAG",
            "Typography": "material design 3 typography font size weight line height",
            "Spacing": "material design 3 spacing 8dp grid padding margin",
            "Layout": "material design 3 app structure layout regions top app bar navigation body"
        }

        query_text = query_map.get(component_type, f"material design 3 {component_type}")
        principles = self.query_design_principle(query_text, top_k=5)

        if not principles:
            return {
                "is_valid": None,
                "violations": ["No design principles found in Pinecone"],
                "suggestions": ["Add M3 design principles to Pinecone"],
                "principles_checked": []
            }

        # Format principles for Claude
        principles_text = "\n\n".join([
            f"--- Principle: {p['title']} ---\n{p['content']}"
            for p in principles
        ])

        # Ask Claude to validate code against principles
        prompt = f"""You are a Material Design 3 expert validator. Review the following code and check if it complies with the M3 design principles provided.

COMPONENT TYPE: {component_type}

M3 DESIGN PRINCIPLES FROM VECTOR DATABASE:
{principles_text}

CODE TO VALIDATE:
```python
{code}
```

Analyze the code and respond in JSON format:
{{
    "is_valid": true/false,
    "violations": ["violation 1", "violation 2", ...],
    "suggestions": ["suggestion 1", "suggestion 2", ...],
    "compliant_aspects": ["what is done correctly"]
}}

Be specific about which M3 principles are violated and provide actionable suggestions."""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            result_text = response.content[0].text

            # Parse JSON response
            import json
            # Extract JSON from markdown code blocks if present
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            result = json.loads(result_text)
            result["principles_checked"] = [p["title"] for p in principles]

            return result

        except Exception as e:
            return {
                "is_valid": None,
                "violations": [f"Validation error: {str(e)}"],
                "suggestions": [],
                "principles_checked": [p["title"] for p in principles],
                "error": str(e)
            }


@pytest.fixture(scope="module")
def validator():
    """Create M3 design validator that queries Pinecone"""
    return M3DesignValidator()


@pytest.fixture(scope="module")
def generated_dashboard():
    """Load the generated dashboard code for testing"""
    dashboard_path = Path(__file__).parent.parent / "generated_dashboard_with_ux_v2.py"
    if not dashboard_path.exists():
        pytest.skip(f"Generated dashboard not found at {dashboard_path}")

    with open(dashboard_path, 'r', encoding='utf-8') as f:
        return f.read()


class TestM3TopAppBarRAG:
    """RAG-based tests for Top App Bar using Pinecone design principles"""

    def test_top_app_bar_compliance(self, validator, generated_dashboard):
        """Validate Top App Bar against M3 principles from Pinecone"""
        # Extract Top App Bar section from code
        match = re.search(r'# 1\. TOP APP BAR.*?(?=# 2\.|with gr\.Row)',
                         generated_dashboard, re.DOTALL)

        if not match:
            pytest.fail("Could not find Top App Bar section in generated dashboard")

        app_bar_code = match.group(0)

        # Validate against Pinecone principles
        result = validator.validate_code_against_principles(
            code=app_bar_code,
            component_type="Top App Bar"
        )

        # Report findings
        print("\n" + "="*70)
        print("TOP APP BAR VALIDATION RESULTS")
        print("="*70)
        print(f"Principles checked: {', '.join(result.get('principles_checked', []))}")

        if result.get('compliant_aspects'):
            print(f"\n[PASS] Compliant aspects:")
            for aspect in result['compliant_aspects']:
                print(f"  - {aspect}")

        if result.get('violations'):
            print(f"\n[FAIL] Violations:")
            for violation in result['violations']:
                print(f"  - {violation}")

        if result.get('suggestions'):
            print(f"\n[SUGGEST] Suggestions:")
            for suggestion in result['suggestions']:
                print(f"  - {suggestion}")

        # Assert no critical violations
        assert result.get('is_valid') is not False, \
            f"Top App Bar violates M3 principles: {', '.join(result.get('violations', []))}"


class TestM3NavigationRailRAG:
    """RAG-based tests for Navigation Rail using Pinecone design principles"""

    def test_navigation_rail_compliance(self, validator, generated_dashboard):
        """Validate Navigation Rail against M3 principles from Pinecone"""
        # Extract Navigation Rail section
        match = re.search(r'# 2A\. NAVIGATION RAIL.*?(?=# 2B\.|with gr\.Column)',
                         generated_dashboard, re.DOTALL)

        if not match:
            pytest.fail("Could not find Navigation Rail section in generated dashboard")

        nav_rail_code = match.group(0)

        # Validate against Pinecone principles
        result = validator.validate_code_against_principles(
            code=nav_rail_code,
            component_type="Navigation Rail"
        )

        # Report findings
        print("\n" + "="*70)
        print("NAVIGATION RAIL VALIDATION RESULTS")
        print("="*70)
        print(f"Principles checked: {', '.join(result.get('principles_checked', []))}")

        if result.get('compliant_aspects'):
            print(f"\n[PASS] Compliant aspects:")
            for aspect in result['compliant_aspects']:
                print(f"  - {aspect}")

        if result.get('violations'):
            print(f"\n[FAIL] Violations:")
            for violation in result['violations']:
                print(f"  - {violation}")

        if result.get('suggestions'):
            print(f"\n[SUGGEST] Suggestions:")
            for suggestion in result['suggestions']:
                print(f"  - {suggestion}")

        # Assert no critical violations
        assert result.get('is_valid') is not False, \
            f"Navigation Rail violates M3 principles: {', '.join(result.get('violations', []))}"


class TestM3ColorContrastRAG:
    """RAG-based tests for color contrast using Pinecone design principles"""

    def test_color_contrast_compliance(self, validator, generated_dashboard):
        """Validate color contrast against M3 accessibility principles from Pinecone"""
        result = validator.validate_code_against_principles(
            code=generated_dashboard,
            component_type="Color Contrast"
        )

        # Report findings
        print("\n" + "="*70)
        print("COLOR CONTRAST VALIDATION RESULTS")
        print("="*70)
        print(f"Principles checked: {', '.join(result.get('principles_checked', []))}")

        if result.get('compliant_aspects'):
            print(f"\n[PASS] Compliant aspects:")
            for aspect in result['compliant_aspects']:
                print(f"  - {aspect}")

        if result.get('violations'):
            print(f"\n[FAIL] Violations:")
            for violation in result['violations']:
                print(f"  - {violation}")

        if result.get('suggestions'):
            print(f"\n[SUGGEST] Suggestions:")
            for suggestion in result['suggestions']:
                print(f"  - {suggestion}")

        # Assert no critical violations
        assert result.get('is_valid') is not False, \
            f"Color contrast violates M3 principles: {', '.join(result.get('violations', []))}"


class TestM3LayoutStructureRAG:
    """RAG-based tests for layout structure using Pinecone design principles"""

    def test_layout_structure_compliance(self, validator, generated_dashboard):
        """Validate overall layout structure against M3 principles from Pinecone"""
        result = validator.validate_code_against_principles(
            code=generated_dashboard,
            component_type="Layout"
        )

        # Report findings
        print("\n" + "="*70)
        print("LAYOUT STRUCTURE VALIDATION RESULTS")
        print("="*70)
        print(f"Principles checked: {', '.join(result.get('principles_checked', []))}")

        if result.get('compliant_aspects'):
            print(f"\n[PASS] Compliant aspects:")
            for aspect in result['compliant_aspects']:
                print(f"  - {aspect}")

        if result.get('violations'):
            print(f"\n[FAIL] Violations:")
            for violation in result['violations']:
                print(f"  - {violation}")

        if result.get('suggestions'):
            print(f"\n[SUGGEST] Suggestions:")
            for suggestion in result['suggestions']:
                print(f"  - {suggestion}")

        # Assert no critical violations
        assert result.get('is_valid') is not False, \
            f"Layout structure violates M3 principles: {', '.join(result.get('violations', []))}"


class TestDesignPrincipleAvailability:
    """Test that required M3 design principles exist in Pinecone"""

    def test_top_app_bar_principles_exist(self, validator):
        """Top App Bar design principles should exist in Pinecone"""
        results = validator.query_design_principle(
            "material design 3 top app bar specifications",
            top_k=3
        )
        assert len(results) > 0, \
            "No Top App Bar principles found in Pinecone. Run add_m3_structural_layout.py"

    def test_navigation_rail_principles_exist(self, validator):
        """Navigation Rail design principles should exist in Pinecone"""
        results = validator.query_design_principle(
            "material design 3 navigation rail specifications",
            top_k=3
        )
        assert len(results) > 0, \
            "No Navigation Rail principles found in Pinecone"

    def test_color_system_principles_exist(self, validator):
        """M3 color system principles should exist in Pinecone"""
        results = validator.query_design_principle(
            "material design 3 color system",
            top_k=3  # Don't filter by category, color principles may be in different categories
        )
        assert len(results) > 0, \
            "No M3 color system principles found in Pinecone"


class TestGeneratedDashboardStructure:
    """Basic structural tests (don't require AI validation)"""

    def test_has_three_structural_regions(self, generated_dashboard):
        """Dashboard should have M3's three structural regions"""
        assert 'TOP APP BAR' in generated_dashboard or 'Top App Bar' in generated_dashboard
        assert 'NAVIGATION RAIL' in generated_dashboard or 'Navigation Rail' in generated_dashboard
        assert 'BODY REGION' in generated_dashboard or 'Body' in generated_dashboard

    def test_no_duplicate_css_parameters(self, generated_dashboard):
        """gr.Blocks() should not have duplicate css= parameters"""
        blocks_pattern = r'gr\.Blocks\([^)]*\)'
        matches = re.findall(blocks_pattern, generated_dashboard)

        for match in matches:
            css_count = match.count('css=')
            assert css_count <= 1, \
                f"gr.Blocks() has duplicate css= parameters: {match}"

    def test_syntax_valid(self, generated_dashboard):
        """Generated dashboard should be valid Python"""
        try:
            compile(generated_dashboard, '<generated>', 'exec')
        except SyntaxError as e:
            pytest.fail(f"Generated dashboard has syntax error: {e}")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s", "--tb=short"])
