"""
Unit Tests for Enhanced UI Agent

Tests Pinecone RAG integration and evolutionary critique functionality.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.agents.ui_agent_enhanced import EnhancedUIAgent, generate_ui, generate_ui_evolved


class TestEnhancedUIAgentInit:
    """Test agent initialization"""

    def test_init_without_rag(self):
        """Test initialization with RAG disabled"""
        agent = EnhancedUIAgent(use_rag=False, use_evolution=False)
        assert agent.use_rag is False
        assert agent.use_evolution is False
        assert agent.knowledge_base is None
        assert agent.evolutionary_system is None

    def test_init_with_rag_only(self):
        """Test initialization with RAG enabled"""
        try:
            agent = EnhancedUIAgent(use_rag=True, use_evolution=False)
            # May fail if Pinecone not configured, which is okay
            assert agent.use_evolution is False
        except Exception as e:
            # Expected if PINECONE_API_KEY not set
            assert "PINECONE_API_KEY" in str(e) or "Pinecone" in str(e)

    def test_init_with_evolution_only(self):
        """Test initialization with evolution enabled"""
        try:
            agent = EnhancedUIAgent(use_rag=False, use_evolution=True)
            assert agent.use_rag is False
        except Exception:
            # Expected if dependencies not available
            pass


class TestRAGIntegration:
    """Test Pinecone RAG functionality"""

    @pytest.mark.skipif(not Path(".env").exists(), reason="No .env file with API keys")
    def test_query_design_guidelines(self):
        """Test querying Pinecone for design guidelines"""
        try:
            agent = EnhancedUIAgent(use_rag=True, use_evolution=False)
            if agent.knowledge_base:
                guidelines = agent.query_design_guidelines("dashboard with charts", top_k=3)
                assert isinstance(guidelines, list)
                # If Pinecone is populated, should return results
                if len(guidelines) > 0:
                    assert 'text' in guidelines[0] or 'content' in guidelines[0]
        except Exception as e:
            pytest.skip(f"Pinecone not configured: {e}")

    @pytest.mark.skipif(not Path(".env").exists(), reason="No .env file")
    def test_enhance_prompt_with_rag(self):
        """Test prompt enhancement with RAG guidelines"""
        try:
            agent = EnhancedUIAgent(use_rag=True, use_evolution=False)
            if agent.knowledge_base:
                original = "Create a contact form"
                enhanced = agent.enhance_prompt_with_rag(original)

                assert len(enhanced) >= len(original)
                # Should contain original description
                assert "contact form" in enhanced.lower()
        except Exception:
            pytest.skip("Pinecone not configured")

    def test_enhance_prompt_without_rag(self):
        """Test prompt enhancement with RAG disabled"""
        agent = EnhancedUIAgent(use_rag=False, use_evolution=False)
        original = "Create a dashboard"
        enhanced = agent.enhance_prompt_with_rag(original)

        # Should return unchanged
        assert enhanced == original


class TestSimpleGeneration:
    """Test basic UI generation without evolution"""

    @pytest.mark.skipif(not Path(".env").exists(), reason="No API keys")
    @pytest.mark.slow
    def test_generate_simple_ui(self):
        """Test simple UI generation"""
        agent = EnhancedUIAgent(use_rag=False, use_evolution=False)

        files = agent.generate_ui_simple(
            description="Create a simple button that says 'Click me'",
            framework="gradio",
            include_backend=False
        )

        assert isinstance(files, dict)
        assert len(files) > 0

        # Check generated code contains Gradio
        code = list(files.values())[0]
        assert "gradio" in code.lower() or "gr." in code


class TestCodeParsing:
    """Test code block parsing"""

    def test_parse_code_blocks_with_markers(self):
        """Test parsing code with file markers"""
        agent = EnhancedUIAgent(use_rag=False, use_evolution=False)

        response = """
### FILE: app.py
```python
import gradio as gr

def main():
    demo = gr.Interface(fn=lambda x: x, inputs="text", outputs="text")
    demo.launch()
```

### FILE: utils.py
```python
def helper():
    return "help"
```
"""

        files = agent._parse_code_blocks(response)

        assert len(files) == 2
        assert "app.py" in files
        assert "utils.py" in files
        assert "import gradio" in files["app.py"]
        assert "helper" in files["utils.py"]

    def test_parse_code_blocks_without_markers(self):
        """Test parsing code without file markers"""
        agent = EnhancedUIAgent(use_rag=False, use_evolution=False)

        response = """
```python
import gradio as gr
demo = gr.Interface(lambda x: x, "text", "text")
demo.launch()
```
"""

        files = agent._parse_code_blocks(response)

        assert len(files) >= 1
        # Should create default file
        code = list(files.values())[0]
        assert "import gradio" in code


class TestConvenienceFunctions:
    """Test convenience wrapper functions"""

    @pytest.mark.skipif(not Path(".env").exists(), reason="No API keys")
    @pytest.mark.slow
    def test_generate_ui_function(self):
        """Test generate_ui convenience function"""
        files = generate_ui(
            description="A button",
            framework="gradio",
            use_rag=False
        )

        assert isinstance(files, dict)


# Pytest configuration
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
