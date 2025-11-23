# How to Run the Collaborative Agent UI Generator

## 🚀 Quick Start (One Command)

### Option 1: Simple Launcher (Easiest)

```bash
start_collaborative_ui.bat
```

This will:
1. Generate context from your data
2. Launch the collaborative agent system
3. Open in your browser automatically

### Option 2: Using the Main Launcher

```bash
# Interactive menu
python launch.py
# Then select option 7: Launch Collaborative Agents

# Or direct command
python launch.py ui collaborate
```

### Option 3: Pipeline Integration

```bash
# Generate context and launch in one command
python scripts\pipeline\run_ingestion.py --generate-context --launch-ui collaborate
```

## 📋 What Happens

### Step 1: Context Generation
The system scans your `data/raw/` directory and generates context:
- Identifies available datasets (production, permits, completions, fracfocus)
- Counts records and calculates sizes
- Saves to `~/.apex_eor/pipeline_context.json`

### Step 2: Streamlit Launches
A browser window opens with the collaborative UI at `http://localhost:8501`

### Step 3: Agent Collaboration Begins
Click **"Start Collaboration"** button and watch:

```
UX Designer:
"I propose a 3-tab dashboard with:
- Tab 1: Production Overview with time-series charts
- Tab 2: Well Details with filterable data table
- Tab 3: Analytics with heatmaps
Using master-detail pattern for drill-down..."

Gradio Developer:
"Good design! A few technical considerations:
- Gradio tabs work well up to 5 tabs, we're safe with 3
- For time-series, I'll use Plotly for interactivity
- Master-detail pattern works great with gr.Row and gr.Column
- Let me implement this..."

[Shows code]

UX Critic:
"Implementation looks solid! A few UX suggestions:
- Add loading states for data fetching
- Include error handling messages
- Add export buttons for reports
- Consider adding tooltips..."

Gradio Developer:
"Excellent feedback! Let me refine..."

[Shows improved code]

Code Reviewer:
"Code is production-ready! All suggestions addressed."

COLLABORATION_COMPLETE
```

### Step 4: Code Generation Complete
- Final code appears in the "Generated Code" section
- Click "Save Code" to save as `generated_collaborative_ui.py`
- Generated code is complete and runnable!

## 🎯 All Available Commands

### Pipeline-Integrated Commands

```bash
# Full pipeline + collaborative UI
python scripts\pipeline\run_ingestion.py --all --launch-ui collaborate

# Context only + collaborative UI (faster, no data reload)
python scripts\pipeline\run_ingestion.py --generate-context --launch-ui collaborate

# Other UI options
python scripts\pipeline\run_ingestion.py --generate-context --launch-ui studio      # Old 3-column UI
python scripts\pipeline\run_ingestion.py --generate-context --launch-ui runner      # Old auto-runner
python scripts\pipeline\run_ingestion.py --generate-context --launch-ui interface   # Debug interface
```

### Direct Streamlit Commands

```bash
# Launch collaborative system directly
streamlit run src\ui\agent_collaborative_system.py

# Launch other UIs
streamlit run src\ui\agent_studio.py
streamlit run src\ui\agent_chat_runner.py
streamlit run src\ui\agent_chat_interface.py
```

### Launcher Commands

```bash
# Interactive menu
python launch.py

# Direct UI launch
python launch.py ui collaborate    # Collaborative system (RECOMMENDED)
python launch.py ui studio          # Agent Studio
python launch.py ui runner          # Agent Runner
python launch.py ui interface       # Agent Interface

# Pipeline commands
python launch.py ingest --all              # Full pipeline
python launch.py ingest --generate-context # Context only
python launch.py status                    # Check status
```

## 🔑 Prerequisites

### 1. API Key

```bash
# Check if set
echo %ANTHROPIC_API_KEY%

# Set it (Windows)
set ANTHROPIC_API_KEY=sk-ant-your-key-here

# Or add to .env file
echo ANTHROPIC_API_KEY=sk-ant-your-key-here > .env
```

### 2. Data

You need pipeline context. Generate it:

```bash
# If you have data in data/raw/
python scripts\pipeline\run_ingestion.py --generate-context

# If you need to download data first
python scripts\pipeline\run_ingestion.py --all
```

### 3. Dependencies

```bash
pip install pyautogen autogen-ext[anthropic] streamlit
```

## 📊 What You'll See in the UI

### Header Section
```
Status: [Agents are collaborating...]
[Start Collaboration] [Save Code] [Reset]
```

### Two-Panel Layout

**Left Panel: Agent Collaboration**
- Real-time agent conversation
- Formatted with agent names and roles
- Shows design proposals, feedback, critiques, code

**Right Panel: Terminal**
- Raw message flow
- Message counter
- Debugging information

### Final Output

**Generated Code Expander**
- Complete Python code
- Ready to run with `python generated_collaborative_ui.py`
- Includes all imports, components, event handlers

## 🎨 Customization

### Change Prompt

The initial prompt is generated from your data context. To customize:

1. Edit requirements in `agent_collaborative_system.py`:

```python
requirements = {
    'screen_type': 'dashboard',  # Change to 'report', 'form', etc.
    'intent': 'Your custom intent here',
    'data_sources': st.session_state.context.get('data_sources', {})
}
```

### Change Model

Edit `_create_model_client()` in `agent_collaborative_system.py`:

```python
return AnthropicChatCompletionClient(
    model="claude-3-haiku-20240307",  # Faster, cheaper
    # or
    model="claude-3-opus-20240229",   # More capable
    api_key=self.api_key
)
```

### Adjust Collaboration Depth

```python
termination = TextMentionTermination("COLLABORATION_COMPLETE") | MaxMessageTermination(30)
# Increase 30 for more rounds
```

### Modify Agent Behavior

Edit system messages in `_create_collaborative_agents()`:

```python
self.ux_designer = AssistantAgent(
    name="UX_Designer",
    model_client=model_client,
    system_message="""Your custom instructions here..."""
)
```

## 🆘 Troubleshooting

### "No context found"
```bash
python scripts\pipeline\run_ingestion.py --generate-context
```

### "ANTHROPIC_API_KEY not set"
```bash
set ANTHROPIC_API_KEY=your-key-here
```

### "AutoGen not installed"
```bash
pip install pyautogen autogen-ext[anthropic]
```

### Agents not collaborating
- Check API key is valid
- Ensure you have API credits
- Check terminal for error messages
- Try with Claude 3 Haiku (cheaper) for testing

### Browser doesn't open
Manually navigate to: `http://localhost:8501`

### Port 8501 already in use
Kill existing Streamlit:
```bash
# Windows
taskkill /F /IM streamlit.exe

# Or use different port
streamlit run src\ui\agent_collaborative_system.py --server.port 8502
```

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Quick 3-step guide
- **[COLLABORATIVE_AGENTS_README.md](COLLABORATIVE_AGENTS_README.md)** - Deep dive into architecture
- **[autogen_setup_guide.py](autogen_setup_guide.py)** - Setup diagnostics

## 🎓 Tips for Best Results

1. **Let agents finish** - Don't interrupt, each round improves quality
2. **Watch the dialogue** - You'll learn about Gradio capabilities/constraints
3. **Read critiques** - UX and Code reviewers catch real issues
4. **Compare to old system** - Run your old sequential agents to see the difference
5. **Iterate** - If not satisfied, hit Reset and try again with adjusted requirements

## 🎉 You're Ready!

The easiest way to start:

```bash
start_collaborative_ui.bat
```

Then click **"Start Collaboration"** in the browser and watch the magic! 🚀

---

**Questions?** Check the documentation files or review the code - it's well-commented!
