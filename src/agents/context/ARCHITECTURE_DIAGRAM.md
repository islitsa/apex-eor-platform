# Agent Studio Architecture - Visual Overview

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     APEX EOR Repository                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ /data    │  │ /pipelines│ │ /config  │  │ /src     │       │
│  │          │  │           │  │          │  │          │       │
│  │ *.parquet│  │ *.py      │  │ *.yaml   │  │ *.py     │       │
│  │ *.csv    │  │ pipeline  │  │ settings │  │ modules  │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
                            ↓ indexes ↓
┌─────────────────────────────────────────────────────────────────┐
│                      AGENT STUDIO                                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │             Semantic Index (The "Water")                 │   │
│  │  • 500+ artifacts indexed                                │   │
│  │  • Embeddings for semantic search                        │   │
│  │  • Continuous relevance field                            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────┐         ┌──────────────────┐             │
│  │ Data Discovery   │         │ Gradient Context │             │
│  │ • Scan /data     │   ←→    │ • Semantic field │             │
│  │ • Read schemas   │         │ • Navigation     │             │
│  │ • Find patterns  │         │ • Multi-hop      │             │
│  └──────────────────┘         └──────────────────┘             │
└─────────────────────────────────────────────────────────────────┘
            ↓ agents swim in ↓               ↓ discover ↓
┌─────────────────────────────────────────────────────────────────┐
│                   CONTEXT SWIMMING AGENTS                        │
│  ┌──────────────────────┐      ┌──────────────────────┐        │
│  │  UX Designer         │      │  Gradio Implementer  │        │
│  │  • Discovers sources │  →   │  • Uses discovered   │        │
│  │  • Reads schemas     │      │  • Generates code    │        │
│  │  • Designs UI        │      │  • Compositional     │        │
│  └──────────────────────┘      └──────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
                            ↓ produces ↓
┌─────────────────────────────────────────────────────────────────┐
│                    GENERATED GRADIO UI                           │
│  • Dashboard with discovered data sources                        │
│  • M3 design system styling                                      │
│  • Compositional code (~300-400 lines)                          │
│  • Material Symbols icons                                        │
└─────────────────────────────────────────────────────────────────┘
```

## Context Flow: Traditional vs Swimming

### Traditional Architecture (Context Passing)
```
User Intent
    ↓
Pipeline/Orchestrator
    ↓ (manually configures context)
    ↓ data_sources = {...}
    ↓ schemas = {...}
    ↓
UX Agent ← receives context
    ↓
Gradio Agent ← receives context
    ↓
Generated UI

Issues:
❌ Manual configuration
❌ Agents are passive
❌ Breaks on repo changes
❌ No discovery
```

### Context Swimming Architecture (Discovery)
```
User Intent
    ↓
Agent Studio (indexes repo)
    ↓
   "Water" (Semantic Index)
    ↓
    ↓ swim ↓
    ↓
UX Agent → discovers data sources
         → reads schemas
         → explores code
    ↓
    ↓ discovered context ↓
    ↓
Gradio Agent → discovers templates
             → generates code
    ↓
Generated UI

Benefits:
✅ Autonomous discovery
✅ Agents are active
✅ Adapts automatically
✅ Finds relationships
```

## Gradient Context System

```
Query: "chemical data for EOR"
         ↓ embed ↓
    Query Embedding
         ↓
         ↓ compute gradient field ↓
         ↓
┌────────────────────────────────────────┐
│      Semantic Relevance Field          │
│                                        │
│  High relevance    ██████              │
│  (gradient peaks)  ███████             │
│                    ████████            │
│  Medium relevance  ███                 │
│                    ██                  │
│  Low relevance     █                   │
│                                        │
│  Artifacts:                            │
│  • fracfocus_chemicals.parquet: 0.95   │
│  • texas_rrc_production.csv: 0.65     │
│  • lab_results.xlsx: 0.42             │
└────────────────────────────────────────┘
         ↓
    Agent follows gradient
    to highest relevance
```

## Multi-Hop Exploration

```
Starting Point: "EOR attribution dashboard"
         ↓
    ┌────▼────┐
    │ HOP 1   │  Discover data sources
    │         │  → FracFocus (chemicals)
    │         │  → Texas RRC (production)
    │         │  → USGS (geological)
    └────┬────┘
         ↓
    ┌────▼────┐
    │ HOP 2   │  Find related code
    │         │  → /pipelines/chemical_extraction.py
    │         │  → /src/attribution/eor_model.py
    └────┬────┘
         ↓
    ┌────▼────┐
    │ HOP 3   │  Discover configurations
    │         │  → /config/data_sources.yaml
    │         │  → /config/pipeline_params.json
    └────┬────┘
         ↓
    Complete Context Map
    (data + code + configs)
```

## Discovery vs Retrieval

### Old Way: Discrete Retrieval
```
Query: "chemical data"
         ↓
Boolean Match
         ↓
     ┌───────┐
     │ Match │  (yes/no)
     └───────┘
         ↓
Return discrete results
```

### New Way: Gradient Navigation
```
Query: "chemical data"
         ↓
Continuous Relevance Field
         ↓
     ┌───────────┐
     │ 0.95  ███ │  Very relevant
     │ 0.65  ██  │  Somewhat relevant
     │ 0.42  █   │  Slightly relevant
     │ 0.15      │  Not relevant
     └───────────┘
         ↓
Navigate toward high gradients
(follow direction of increasing relevance)
```

## Integration Points with Your Existing System

```
┌────────────────────────────────────────────────┐
│         Your Existing System (Keep)            │
│  ┌──────────────────────────────────────────┐ │
│  │ ux_designer.py                           │ │
│  │ gradio_developer.py                      │ │
│  │ design_kb_pinecone.py                    │ │
│  │ m3_theme.py                              │ │
│  │ gradio_snippets.py                       │ │
│  └──────────────────────────────────────────┘ │
└────────────────────────────────────────────────┘
                    ↕ integrate ↕
┌────────────────────────────────────────────────┐
│         Agent Studio (New Layer)               │
│  ┌──────────────────────────────────────────┐ │
│  │ agent_studio.py                          │ │
│  │ context_swimming_agents.py               │ │
│  │ gradient_context.py                      │ │
│  └──────────────────────────────────────────┘ │
└────────────────────────────────────────────────┘

Integration Options:

Option A: Hybrid
├─ Keep existing agents
├─ Add discovery capability
└─ Backward compatible

Option B: Replace
├─ Use context-swimming agents
├─ Full discovery mode
└─ Maximum autonomy
```

## Token Flow: Before & After

### Before (Prompt Stuffing)
```
Prompt:
├─ System instructions (500 tokens)
├─ Data sources config (2000 tokens) ← MASSIVE
├─ Schemas (1500 tokens) ← MASSIVE
├─ UX patterns (500 tokens)
└─ User intent (200 tokens)
    Total: 4700 tokens

Output: 8000 tokens (monolithic code)
```

### After (Discovery + Composition)
```
Prompt:
├─ System instructions (500 tokens)
├─ Discovered context summary (300 tokens) ← COMPACT
├─ Compositional requirements (200 tokens)
└─ User intent (200 tokens)
    Total: 1200 tokens (75% reduction!)

Output: 2000 tokens (compositional code)
```

## File Structure After Integration

```
apex_eor/
├── data/
│   ├── fracfocus/
│   ├── texas_rrc/
│   └── usgs/
├── pipelines/
│   ├── chemical_extraction.py
│   └── production_pipeline.py
├── config/
│   └── data_sources.yaml
├── src/
│   ├── agent_studio/              ← NEW
│   │   ├── __init__.py
│   │   ├── agent_studio.py
│   │   ├── context_swimming_agents.py
│   │   ├── gradient_context.py
│   │   └── integration_example.py
│   ├── agents/
│   │   ├── ux_designer.py         ← EXISTING (keep or replace)
│   │   └── gradio_developer.py    ← EXISTING (keep or replace)
│   ├── templates/
│   │   ├── m3_theme.py            ← EXISTING (used by new agents)
│   │   └── gradio_snippets.py     ← EXISTING (optional)
│   └── knowledge/
│       └── design_kb_pinecone.py  ← EXISTING (integrate gradient)
└── generated/
    └── dashboards/
```

## Performance Characteristics

```
┌─────────────────────────────────────────────┐
│ Operation              Time      Frequency  │
├─────────────────────────────────────────────┤
│ Index repository       10s       Once/day   │
│ Discover sources       0.5s      Per query  │
│ Read schemas           1s        Per query  │
│ Gradient navigation    2s        Per query  │
│ LLM design call        5s        Per query  │
│ LLM implementation     8s        Per query  │
├─────────────────────────────────────────────┤
│ TOTAL                  ~16.5s    Per query  │
└─────────────────────────────────────────────┘

Overhead: 3.5s (discovery + navigation)
Benefit: Real schemas, relationships, 75% token reduction
```

## The Fish Analogy

```
Traditional Architecture:
    🐠 ← context ← context ← context
    Fish being fed (passive consumer)

Context Swimming:
    🐠 🌊 🌊 🌊 🌊 🌊 🌊
    Fish swimming in water (active explorer)
    The water IS the context
    The fish discovers food by exploring
```

---

"The fish doesn't ask for water. It swims." 🐠
