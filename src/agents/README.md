# UI/UX Agent

A full-stack conversational AI agent for building data visualization and interaction interfaces for the APEX EOR platform.

## Features

- **Conversational Interface**: Chat with the agent to design UIs iteratively
- **Full-Stack Generation**: Creates frontend, backend, and database code
- **Data-Aware**: Understands RRC datasets structure (completions, permits, production)
- **Framework Support**: Streamlit, React, Flask, FastAPI
- **Code Export**: Automatically saves generated files to disk
- **Session Management**: Save and resume conversations

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up API key
echo "ANTHROPIC_API_KEY=your_key_here" >> .env
```

## Quick Start

### Basic Usage

```python
from src.agents.ui_agent import UIAgent

# Initialize agent
agent = UIAgent()

# Chat with the agent
response = agent.chat("""
Create a Streamlit dashboard for RRC completion data with:
- Filters for operator and date range
- A data table showing completions
- A chart of completions over time
""")

print(response)
```

### Generate UI Files

```python
from src.agents.ui_agent import UIAgent

agent = UIAgent()

# Generate and save UI code to disk
files = agent.generate_ui(
    description="Build a full-stack dashboard for production data analysis",
    framework="streamlit",
    include_backend=True,
    output_dir="generated_ui/production_dashboard"
)

print(f"Generated {len(files)} files")
```

### Interactive Mode

```python
from src.agents.ui_agent_example import interactive_mode

# Start interactive chat session
interactive_mode()
```

## Examples

See [ui_agent_example.py](ui_agent_example.py) for detailed examples:

1. **Simple Chat** - Basic conversational UI generation
2. **Generate UI Files** - Automatic file creation
3. **Iterative Design** - Refine UI through conversation
4. **Specific Components** - Generate reusable components
5. **Data Context** - View agent's dataset knowledge

## Agent Capabilities

### Frontend
- Streamlit dashboards
- React components (TypeScript)
- Interactive forms, filters, tables
- Data visualizations (Plotly, Recharts)
- Responsive layouts

### Backend
- Flask/FastAPI endpoints
- SQL queries (DuckDB, PostgreSQL)
- CRUD operations
- Data transformations
- Authentication/authorization

### Data Context

The agent understands your RRC datasets:

**Completions Data**
- 541,052 records from 25,106 completion packets
- Key fields: api_number, operator, lease_name, completion_date

**Horizontal Permits**
- 168,239 permit records
- Key fields: permit_number, api_number, operator_name, lease_name

**Production Data**
- 90+ million production records
- Key tables: OG_COUNTY_LEASE_CYCLE_DATA_TABLE (74M rows), OG_LEASE_CYCLE_DATA_TABLE (22M rows)
- Key fields: api_number, cycle_date, oil_prod_volume, gas_prod_volume

## Workflow

1. **Initialize agent**: `agent = UIAgent()`
2. **Describe what you want**: Natural language description of UI/functionality
3. **Review generated code**: Agent provides complete, runnable code
4. **Iterate if needed**: Ask for changes or enhancements
5. **Save to disk**: Use `generate_ui()` with `output_dir` parameter

## Example Requests

```python
# Dashboard with filters
agent.chat("Create a dashboard for exploring completion data with filters for operator and date")

# API endpoint
agent.chat("Build a Flask API endpoint to search wells by API number")

# React component
agent.chat("Create a reusable React component for displaying production trends")

# Full-stack app
agent.chat("""
Build a full-stack application:
- Frontend: Streamlit with map view of wells
- Backend: FastAPI with CRUD operations
- Database: DuckDB queries
- Features: Search, filter, export to CSV
""")

# Specific enhancement
agent.chat("Add authentication to the API using JWT tokens")
```

## Session Management

```python
# Save conversation for later
agent.save_conversation("my_ui_design.json")

# Load previous conversation
agent.load_conversation("my_ui_design.json")

# Reset conversation
agent.reset()
```

## Generated File Structure

Typical output structure:

```
generated_ui/
├── dashboard/
│   ├── app.py              # Streamlit dashboard
│   ├── components/         # Reusable components
│   │   ├── filters.py
│   │   └── charts.py
│   ├── api/                # Backend API
│   │   ├── routes.py
│   │   └── models.py
│   ├── utils/              # Helper functions
│   │   ├── data_loader.py
│   │   └── queries.py
│   └── requirements.txt    # Dependencies
```

## Tips

- **Be specific**: The more detail you provide, the better the generated code
- **Ask questions**: The agent will clarify ambiguous requirements
- **Iterate**: Start simple, then ask for enhancements
- **Review code**: Always review and test generated code before deployment
- **Use data context**: Refer to specific datasets (completions, permits, production)
- **Specify framework**: Mention Streamlit, React, Flask, etc.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      UI Agent                            │
│                                                          │
│  ┌──────────────┐     ┌─────────────────────────────┐  │
│  │              │     │                              │  │
│  │   Anthropic  │────▶│    System Prompt             │  │
│  │   Claude API │     │    (RRC Data Context)        │  │
│  │              │     │                              │  │
│  └──────────────┘     └─────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Conversation History                      │  │
│  │  [ User → Assistant → User → Assistant... ]      │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Code Generation & Parsing                 │  │
│  │  • Extract code blocks                            │  │
│  │  • Save to file structure                         │  │
│  │  • Include dependencies                           │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
                 ┌────────────────┐
                 │  Generated UI  │
                 │   • Frontend   │
                 │   • Backend    │
                 │   • Database   │
                 └────────────────┘
```

## Next Steps

1. Run examples: `python src/agents/ui_agent_example.py`
2. Try interactive mode for hands-on experience
3. Generate your first UI for RRC data exploration
4. Integrate generated code into your APEX platform

## Support

For issues or questions, refer to:
- [ui_agent.py](ui_agent.py) - Main agent implementation
- [ui_agent_example.py](ui_agent_example.py) - Usage examples
- [../../data/raw/rrc/QUICK_START.md](../../data/raw/rrc/QUICK_START.md) - RRC data loading guide
