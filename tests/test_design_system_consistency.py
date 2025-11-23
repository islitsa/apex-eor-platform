"""
Design System Consistency Tests

These meta-tests validate the design system itself (Pinecone knowledge base).
They ensure there are no conflicting specifications, that there's a single source
of truth for design tokens, and that component specs reference tokens instead of
hardcoding values.

This prevents the issue where tests pass but validate against polluted data.
"""

import pytest
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from knowledge.design_kb_pinecone import DesignKnowledgeBasePinecone


@pytest.fixture(scope="module")
def design_kb():
    """Connect to Pinecone design knowledge base"""
    return DesignKnowledgeBasePinecone()


class TestColorTokenConsistency:
    """Validate that color tokens have single, consistent definitions"""

    def test_single_primary_color_definition(self, design_kb):
        """There should be exactly ONE definition for 'primary' color"""
        results = design_kb.query("material design 3 primary color", top_k=10)

        primary_colors = set()
        docs_with_primary = []

        for doc in results:
            # Look for "primary: #HEXCODE" pattern
            matches = re.findall(r'\bprimary:\s*(#[0-9A-Fa-f]{6})', doc['content'], re.I)
            for match in matches:
                primary_colors.add(match.upper())
                docs_with_primary.append((doc['title'], match))

        # Report what was found
        print(f"\nFound {len(primary_colors)} different primary color(s):")
        for color in primary_colors:
            docs = [title for title, c in docs_with_primary if c.upper() == color]
            print(f"  {color}: in {len(docs)} document(s)")

        # Assert single definition
        assert len(primary_colors) == 1, \
            f"Expected 1 primary color, found {len(primary_colors)}: {primary_colors}"

        # Assert it's the M3 blue
        assert "#1890FF" in primary_colors, \
            f"Primary color should be #1890FF (M3 blue), found: {primary_colors}"

    def test_no_conflicting_color_definitions(self, design_kb):
        """Check for other color conflicts beyond primary"""
        results = design_kb.query("material design 3 design tokens color", top_k=5)

        conflicts = []

        color_tokens = ['on-primary', 'surface', 'error', 'success']

        for token in color_tokens:
            colors_found = set()

            for doc in results:
                pattern = rf'\b{token}:\s*(#[0-9A-Fa-f]{{6}})'
                matches = re.findall(pattern, doc['content'], re.I)
                colors_found.update([m.upper() for m in matches])

            if len(colors_found) > 1:
                conflicts.append((token, colors_found))

        if conflicts:
            conflict_msg = "\n".join([f"  {token}: {colors}" for token, colors in conflicts])
            pytest.fail(f"Found conflicting color definitions:\n{conflict_msg}")

    def test_no_purple_6750A4_in_design_tokens(self, design_kb):
        """The old purple (#6750A4) should NOT be in design tokens"""
        results = design_kb.query("material design 3 design tokens authority", top_k=1, category="design-tokens")

        if results:
            content = results[0]['content']
            assert '#6750A4' not in content.upper(), \
                "Purple #6750A4 found in design tokens - should only have M3 blue #1890FF"


class TestComponentSpecsReferenceTokens:
    """Validate that component specs reference design tokens, not hardcode values"""

    def test_top_app_bar_references_tokens(self, design_kb):
        """Top App Bar spec should reference {primary}, not hardcode colors"""
        results = design_kb.query("material design 3 top app bar specification", top_k=1)

        if not results:
            pytest.skip("Top App Bar specification not found in Pinecone")

        content = results[0]['content']
        title = results[0]['title']

        # Should reference tokens
        has_reference = any(phrase in content.lower() for phrase in [
            'reference design tokens',
            '{primary}',
            'query',
            'design tokens'
        ])

        assert has_reference, \
            f"{title} should reference design tokens, not hardcode color values"

    def test_navigation_rail_references_tokens(self, design_kb):
        """Navigation Rail spec should reference {surface}, not hardcode colors"""
        results = design_kb.query("material design 3 navigation rail specification", top_k=1)

        if not results:
            pytest.skip("Navigation Rail specification not found in Pinecone")

        content = results[0]['content']
        title = results[0]['title']

        # Should reference tokens
        has_reference = any(phrase in content.lower() for phrase in [
            'reference design tokens',
            '{surface}',
            'query',
            'design tokens'
        ])

        assert has_reference, \
            f"{title} should reference design tokens, not hardcode color values"


class TestDesignTokensAuthority:
    """Validate there's a single authoritative source for design tokens"""

    def test_design_tokens_document_exists(self, design_kb):
        """There should be an authoritative design tokens document"""
        results = design_kb.query("material design 3 design tokens", category="design-tokens", top_k=1)

        assert len(results) > 0, \
            "No design tokens document found in Pinecone"

        doc = results[0]
        assert 'authority' in doc.get('title', '').lower() or \
               doc.get('metadata', {}).get('authority') == 'true', \
            "Design tokens document should be marked as authoritative"

    def test_design_tokens_has_all_required_colors(self, design_kb):
        """Design tokens document should define all required colors"""
        results = design_kb.query("material design 3 design tokens", category="design-tokens", top_k=1)

        if not results:
            pytest.fail("Design tokens document not found")

        content = results[0]['content']

        required_tokens = [
            'primary',
            'on-primary',
            'surface',
            'outline'
        ]

        missing = []
        for token in required_tokens:
            pattern = rf'\b{token}:\s*#[0-9A-Fa-f]{{6}}'
            if not re.search(pattern, content, re.I):
                missing.append(token)

        assert not missing, \
            f"Design tokens document missing required colors: {missing}"


class TestNoHardcodedColors:
    """Validate that component assembler queries colors, doesn't hardcode them"""

    def test_component_assembler_uses_query_method(self):
        """Component assembler should have _query_color_token method"""
        assembler_path = Path(__file__).parent.parent / "src" / "agents" / "component_assembler_v3.py"

        if not assembler_path.exists():
            pytest.skip("Component assembler not found")

        with open(assembler_path, 'r', encoding='utf-8') as f:
            code = f.read()

        assert '_query_color_token' in code, \
            "Component assembler should have _query_color_token() method"

        assert 'self._query_color_token' in code, \
            "Component assembler should call _query_color_token() method"

    def test_component_assembler_no_hardcoded_purple(self):
        """Component assembler should NOT have #6750A4 hardcoded"""
        assembler_path = Path(__file__).parent.parent / "src" / "agents" / "component_assembler_v3.py"

        if not assembler_path.exists():
            pytest.skip("Component assembler not found")

        with open(assembler_path, 'r', encoding='utf-8') as f:
            code = f.read()

        # Check if purple is hardcoded (not in comments)
        lines_with_purple = []
        for i, line in enumerate(code.split('\n'), 1):
            if '#6750A4' in line.upper() and not line.strip().startswith('#'):
                lines_with_purple.append((i, line.strip()))

        assert not lines_with_purple, \
            f"Found hardcoded purple #6750A4 in component_assembler_v3.py at lines: " + \
            ", ".join([str(l) for l, _ in lines_with_purple])


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
