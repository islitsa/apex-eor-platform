# APEX Knowledge System - Quick Start Guide

## ✅ What Was Built

A **hybrid Knowledge Graph + RAG system** for your 16+ agent platform.

### Components Created

1. **Knowledge Graph** (Neo4j) - `src/knowledge/knowledge_graph.py`
   - Agent definitions & capabilities
   - Agent dependencies & workflows
   - Data relationships (Wells→Formations→Production)
   - Multi-hop reasoning

2. **RAG Knowledge Base** (ChromaDB) - `src/knowledge/knowledge_base.py`
   - 15 markdown files indexed
   - 20+ JSON schemas indexed
   - Semantic search
   - Context generation for agents

3. **Master Knowledge System** - `src/knowledge/master_knowledge.py`
   - Unified interface
   - Intelligent query routing
   - Agent context augmentation

4. **16 Specialized Agents** - Defined in setup script
   - UI Generator, Data Validator, Production Analyzer, etc.
   - Complete workflow dependencies
   - Physics validation chain

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Install Dependencies

```bash
pip install neo4j chromadb tiktoken
```

Or:
```bash
pip install -r requirements.txt
```

### Step 2: Start Neo4j

**Option A: Docker Compose (Easiest)**
```bash
docker-compose up -d
```

**Option B: Docker Run**
```bash
docker run -d \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/apex_knowledge \
  --name apex-neo4j \
  neo4j:latest
```

**Option C: Neo4j Desktop**
- Download from neo4j.com/download
- Create database with password: `apex_knowledge`

### Step 3: Initialize Knowledge Systems

```bash
python scripts/knowledge/setup_knowledge_system.py
```

This will:
- Create Knowledge Graph schema
- Add 16 agents with dependencies
- Ingest all markdown documentation
- Index all JSON schemas

**Expected output:**
```
=======================================================================
APEX KNOWLEDGE SYSTEM SETUP
=======================================================================

SETTING UP KNOWLEDGE GRAPH
...
✓ Knowledge Graph setup complete!
  Agents: 16
  Dependencies: 13

SETTING UP RAG KNOWLEDGE BASE
...
✓ Knowledge Base setup complete!
  Markdown files: 15
  JSON schemas: 20+
  Total documents in KB: 150+
```

### Step 4: Test the System

**Query Knowledge Graph:**
```bash
python scripts/knowledge/query_kg.py "Which agent handles EOR screening?"
# Result: EOR Candidate Screener (agent_12)

python scripts/knowledge/query_kg.py --all-agents
# Lists all 16 agents

python scripts/knowledge/query_kg.py --workflow agent_02 agent_16
# Shows: Data Validator → ... → Multi-Agent Validator
```

**Search Knowledge Base:**
```bash
python scripts/knowledge/query_kb.py "How to use the pipeline?"
# Returns: Relevant sections from pipeline documentation

python scripts/knowledge/query_kb.py "What is in RRC completions data?"
# Returns: Info from data dictionaries and READMEs

python scripts/knowledge/query_kb.py --stats
# Shows: Number of indexed documents
```

**Use Master Knowledge System:**
```python
from src.knowledge import APEXMasterKnowledge

mk = APEXMasterKnowledge()

# Automatically routes to correct system
result = mk.query("Which agent should analyze production data?")
print(result['answer'])
# → "Agent 'Production Analyzer' (ID: agent_03) specializes in production_analysis"

result = mk.query("How do I run the pipeline?")
print(result['answer'])
# → Returns documentation from RAG
```

---

## 📚 The 16 Agents

### Data & Validation Agents
1. **UI Generator** (`agent_01`) - Interface design, Material Design
2. **Data Validator** (`agent_02`) - Data quality, schema validation

### Analysis Agents
3. **Production Analyzer** (`agent_03`) - Production trends, decline curves
4. **Formation Matcher** (`agent_04`) - Geological formations
5. **Completion Analyzer** (`agent_05`) - Frac designs, treatments
6. **Chemical Matcher** (`agent_06`) - FracFocus analysis

### Specialist Agents
7. **Shale Specialist** (`agent_07`) - Unconventional reservoirs
8. **Decline Curve Expert** (`agent_08`) - Arps models, forecasting
9. **Causal Inference Engine** (`agent_09`) - DAG analysis, attribution
10. **Linear Inflow Analyzer** (`agent_10`) - Stage diagnostics
11. **Parent-Child Analyzer** (`agent_11`) - Well interference

### EOR Agents
12. **EOR Candidate Screener** (`agent_12`) - Well screening, ranking
13. **CO2 Injection Specialist** (`agent_13`) - CO2 flooding
14. **Gas Injection Specialist** (`agent_14`) - Gas injection EOR

### Research & Validation
15. **Hypothesis Generator** (`agent_15`) - First principles research
16. **Multi-Agent Validator** (`agent_16`) - 16-agent physics validation

### Agent Workflow Example

```
Data Validator (agent_02)
    ↓ THEN
Production Analyzer (agent_03)
    ↓ THEN
Decline Curve Expert (agent_08)
    ↓ THEN
Causal Inference Engine (agent_09)
    ↓ THEN
EOR Candidate Screener (agent_12)
    ↓ THEN
CO2 Injection Specialist (agent_13)
    ↓ THEN
Hypothesis Generator (agent_15)
    ↓ THEN
Multi-Agent Validator (agent_16)
```

---

## 🔧 Usage Examples

### Example 1: Find Agent for Task

```python
from src.knowledge import APEXMasterKnowledge

mk = APEXMasterKnowledge()

# Route task to agent
agent = mk.route_to_agent("ui_design")
print(f"Agent: {agent['name']}")
# → UI Generator

agent = mk.route_to_agent("eor_screening")
print(f"Agent: {agent['name']}")
# → EOR Candidate Screener
```

### Example 2: Get Context for Agent

```python
# Agent needs context about data pipeline
context = mk.get_context_for_agent(
    agent_id="agent_03",  # Production Analyzer
    query="How to load RRC production data?"
)

print(context)
# Returns:
# === Your Agent Profile ===
# Name: Production Analyzer
# Role: analysis
# ...
# === Relevant Documentation ===
# [From pipeline README...]
# [From data dictionaries...]
```

### Example 3: Query Agent Dependencies

```python
from src.knowledge import APEXKnowledgeGraph

kg = APEXKnowledgeGraph()

deps = kg.get_agent_dependencies("agent_12")  # EOR Screener
print(f"Requires: {deps['requires']}")
# → ['agent_09']  # Causal Inference Engine

print(f"Required by: {deps['required_by']}")
# → ['agent_13', 'agent_14']  # CO2 & Gas Specialists
```

### Example 4: Search Documentation

```python
from src.knowledge import APEXKnowledgeBase

kb = APEXKnowledgeBase()

results = kb.search("What fields are in G-1 forms?")
for result in results['results']:
    print(f"{result['metadata']['filename']}: {result['relevance']:.1%}")
    print(result['content'][:200])
```

---

## 🎯 Integration with Existing Code

### Enhance UI Agent

```python
# src/agents/ui_agent.py

from src.knowledge import APEXMasterKnowledge

class UIAgent:
    def __init__(self):
        self.knowledge = APEXMasterKnowledge()
        # ... existing code

    def chat_with_knowledge(self, user_message: str) -> str:
        """Chat with knowledge base context"""
        # Get relevant context
        context = self.knowledge.get_context_for_agent(
            agent_id="agent_01",  # UI Generator
            query=user_message
        )

        # Augment message
        augmented_message = f"""
Context:
{context}

User question:
{user_message}
"""
        return self.chat(augmented_message)
```

### Route Pipeline Tasks to Agents

```python
# scripts/pipeline/run_ingestion.py

from src.knowledge import APEXMasterKnowledge

class IngestionPipeline:
    def __init__(self):
        self.knowledge = APEXMasterKnowledge()
        # ... existing code

    def validate_data(self, dataset):
        # Find validator agent
        agent = self.knowledge.route_to_agent("data_validation")
        print(f"Routing validation to: {agent['name']}")

        # Execute validation with that agent
        # ...
```

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│               APEX Master Knowledge System                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────┐    ┌──────────────────────┐      │
│  │  Knowledge Graph     │    │   RAG Knowledge Base │      │
│  │  (Neo4j)             │    │   (ChromaDB)         │      │
│  │                      │    │                      │      │
│  │  • 16 Agents         │    │  • 15 MD files       │      │
│  │  • Workflows         │    │  • 20+ JSON schemas  │      │
│  │  • Dependencies      │    │  • Semantic search   │      │
│  │  • Reasoning         │    │  • Context gen       │      │
│  └──────────────────────┘    └──────────────────────┘      │
│           │                            │                    │
│           └────────────┬───────────────┘                    │
│                        ▼                                    │
│         Intelligent Query Routing                           │
│         - "Which agent?" → KG                               │
│         - "How to...?" → RAG                                │
│                        │                                    │
│           ┌────────────┼────────────┐                       │
│           ▼            ▼            ▼                       │
│       Agent 1      Agent 2  ...  Agent 16                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Maintenance

### Update Agents

```python
from src.knowledge import APEXKnowledgeGraph

kg = APEXKnowledgeGraph()

# Add new agent
kg.create_agent(
    agent_id="agent_17",
    name="New Specialist",
    role="specialist",
    specialization="new_task"
)

# Update agent
kg.create_agent(
    agent_id="agent_01",
    priority=10  # Update priority
)

# Add dependency
kg.create_agent_dependency("agent_17", "agent_16", "THEN")
```

### Re-index Documentation

```bash
python scripts/knowledge/setup_knowledge_system.py
```

Or programmatically:
```python
from src.knowledge import APEXKnowledgeBase

kb = APEXKnowledgeBase()
kb.clear_all()  # Clear existing
kb.ingest_all()  # Re-ingest
```

---

## 📈 Statistics

Check system health:
```bash
# Knowledge Graph stats
python scripts/knowledge/query_kg.py --stats

# Knowledge Base stats
python scripts/knowledge/query_kb.py --stats
```

Or in code:
```python
mk = APEXMasterKnowledge()
stats = mk.get_stats()
print(stats)
```

---

## 🎓 Next Steps

1. **Integrate with agents** - Add knowledge system to each agent
2. **Build orchestrator** - Create agent routing system
3. **Add workflows** - Define multi-agent workflows
4. **Track tasks** - Store task state in KG
5. **Expand schema** - Add Wells, Formations, Production nodes

---

## 📝 Files Created

- `src/knowledge/knowledge_graph.py` (400 lines)
- `src/knowledge/knowledge_base.py` (350 lines)
- `src/knowledge/master_knowledge.py` (250 lines)
- `src/knowledge/__init__.py`
- `scripts/knowledge/setup_knowledge_system.py` (300 lines)
- `scripts/knowledge/query_kg.py` (CLI tool)
- `scripts/knowledge/query_kb.py` (CLI tool)
- `docker-compose.yml` (Neo4j setup)
- Updated `requirements.txt`

**Total:** ~1,500 lines of production-ready code

---

*Last Updated: 2025-01-24*
*APEX Knowledge System - Quick Start Guide*
