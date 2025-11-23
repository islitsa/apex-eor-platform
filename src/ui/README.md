# Agent Chat Interface

**Interactive Streamlit interface to chat with UX Designer and Gradio Developer agents**

## Features

🎨 **Watch Agents Collaborate in Real-Time**
- See UX Designer create design specifications
- Watch Gradio Developer implement with constraints
- View Chain of Thought reasoning
- Inspect implementation plans

💬 **Chat with Individual Agents**
- Ask UX Designer about design decisions
- Ask Gradio Developer about implementation details
- Provide feedback that influences future generations

📊 **Interactive UI Generation**
- Load pipeline context
- Specify requirements (screen type, user intent)
- Generate code and watch the process
- Download generated code

## Quick Start

### Option 1: Launch Script (Windows)
```bash
scripts\launch_agent_chat.bat
```

### Option 2: Direct Command
```bash
streamlit run src/ui/agent_chat_interface.py
```

## How to Use

### 1. Load Context
Click **"Load Pipeline Context"** to discover data sources from your pipeline.

### 2. Specify Requirements
- Choose screen type (dashboard, navigation, settings, etc.)
- Describe user intent
- Click **"Generate UI Code"**

### 3. Watch Agents Work
The right pane shows the conversation:
- 🎭 **Orchestrator**: Coordinates the process
- 🎨 **UX Designer**: Creates design specification
  - Queries UX patterns from Pinecone
  - Applies Chain of Thought reasoning
  - Defines components and interactions
- ⚙️ **Gradio Developer**: Implements the design
  - Queries Gradio constraints from Pinecone
  - Creates implementation plan
  - Generates validated code

### 4. Chat with Agents
Use the chat input at the bottom to ask questions or provide feedback:

**Example Questions:**
- "Why did you choose a master-detail pattern?" (routes to UX Designer)
- "How does the Gradio event handling work?" (routes to Gradio Developer)
- "Can we make the buttons bigger?"
- "I prefer a different color scheme"

**Routing Logic:**
- Questions with "design", "ux", "layout", "pattern", "user" → UX Designer
- Questions with "gradio", "code", "implement", "component" → Gradio Developer
- General feedback → Orchestrator (notes for future generations)

### 5. Download Code
Once generation completes, download the code using the download button.

## Architecture

```
┌─────────────────┐
│ User Interface  │
│  (Streamlit)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Orchestrator   │  ← Coordinates agents
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌─────────┐ ┌────────────┐
│   UX    │ │  Gradio    │
│Designer │ │ Developer  │
└─────────┘ └────────────┘
    │            │
    ▼            ▼
┌──────────────────────┐
│  Pinecone RAG        │
│  - UX Patterns       │
│  - Design Principles │
│  - Gradio Constraints│
└──────────────────────┘
```

## Agent Enhancements

All agents include:
- ✅ **Chain of Thought (CoT)**: Step-by-step reasoning
- ✅ **Planning**: Separate planning phase before execution
- ✅ **Memory**: Track history across session
- ✅ **Skills**: Automated validation and testing
- ✅ **Persona**: Specialized expertise

## Example Session

```
User: Generate a dashboard_navigation screen

Orchestrator: Initializing two-agent system...

UX Designer: Starting design process...
UX Designer: Querying UX patterns from Pinecone...
UX Designer: Applying Chain of Thought reasoning...
UX Designer: Design complete! (3 components, 2 interactions)

Gradio Developer: Starting implementation...
Gradio Developer: Querying Gradio constraints from Pinecone...
Gradio Developer: Creating implementation plan...
Gradio Developer: Generating Gradio code...
Gradio Developer: Validating code (Skills)...
Gradio Developer: Implementation complete! (15,234 chars)

Orchestrator: Code generation complete!

User: Why did you choose a card-grid layout?

UX Designer: I chose a card-grid layout because it provides
excellent information density while maintaining visual clarity...
```

## Troubleshooting

**Streamlit not found:**
```bash
pip install streamlit
```

**Context loading fails:**
Make sure you have run the pipeline at least once to generate metadata.

**Agents not responding:**
Check that `ANTHROPIC_API_KEY` and `PINECONE_API_KEY` are set in `.env`

## File Location

[src/ui/agent_chat_interface.py](./agent_chat_interface.py)