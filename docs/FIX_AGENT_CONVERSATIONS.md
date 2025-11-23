# Fixing Agent Conversations - Critical UX Issue

## The Problem (From Session 1.json)

**User:** "why do you show 1 dataset for rrc on the rrc card?"

**UX Designer:** Gives generic explanation about "progressive disclosure" but **has no idea what RRC is or how many datasets exist!**

**User:** "how many datasets are in fact available for RRC?"

**Gradio Developer:** "the implementation is incomplete and cut off mid-structure" - **can't see its own generated code!**

**User:** "please review navigation on the left. what ux ui principles does it violate?"

**UX Designer:** "I don't see the actual design or screenshot" - **IT DESIGNED IT but can't see it!**

---

## Root Cause Analysis

### Current Implementation (Broken)

```python
# UX Designer Q&A (line 410-418)
prompt = f"""You are the UX Designer agent.
The user asked: {user_input}

DESIGN HISTORY:
{len(design_history)} designs created  # ← Just a count!

Please answer from a UX design perspective."""

# Gradio Developer Q&A (line 438-450)
prompt = f"""You are the Gradio Developer agent.
The user asked: {user_input}

IMPLEMENTATION HISTORY:
{len(impl_history)} implementations created  # ← Just a count!

GENERATED CODE:
{st.session_state.generated_code[:500]}  # ← Only 500 chars!

Please answer from a technical perspective."""
```

### What's Missing

❌ **The actual DesignSpec** that was created
❌ **Full generated code** (only 500 chars provided)
❌ **Data source context** (how many RRC datasets exist)
❌ **Component details** (what cards were created)
❌ **Conversation history** (previous Q&A)
❌ **Visual representation** of the UI

---

## The Fix: Rich Context for Agents

### Principle: Agents Need to See What They Created

When answering questions, agents should have access to:

1. **Their own work** - full design spec or generated code
2. **The data** - actual data sources, counts, metadata
3. **Conversation history** - previous questions/answers
4. **User's current view** - what they're looking at
5. **Cross-agent context** - what the other agent did

---

## Implementation

### Step 1: Enhanced Context for UX Designer

```python
def handle_user_input(self, user_input: str):
    if any(word in user_input.lower() for word in ['design', 'ux', 'why', 'pattern', 'principle']):
        # UX Designer question
        self.add_agent_message('user', 'ux_designer', user_input)

        # BUILD RICH CONTEXT
        design_history = st.session_state.orchestrator.ux_designer.design_history

        # Get the actual design spec (not just count!)
        last_design = design_history[-1] if design_history else None

        # Get data source context
        data_sources = st.session_state.context.get('data_sources', {})

        # Build comprehensive context
        context_lines = []

        # 1. DATA SOURCE CONTEXT
        context_lines.append("DATA SOURCES AVAILABLE:")
        for source_name, source_info in data_sources.items():
            dataset_count = len(source_info.get('datasets', []))
            context_lines.append(f"  - {source_name}: {dataset_count} datasets")

        # 2. DESIGN SPEC CONTEXT
        if last_design:
            context_lines.append("\nDESIGN SPECIFICATION YOU CREATED:")
            context_lines.append(f"  Screen Type: {last_design.get('screen_type', 'N/A')}")
            context_lines.append(f"  Intent: {last_design.get('intent', 'N/A')}")
            context_lines.append(f"  Components: {len(last_design.get('components', []))}")

            # Show component details
            for comp in last_design.get('components', []):
                context_lines.append(f"    - {comp.get('type')}: {comp.get('intent')}")

            context_lines.append(f"  Patterns Used: {', '.join(last_design.get('patterns', []))}")

        # 3. GENERATED CODE CONTEXT (what Gradio Developer made)
        if 'generated_code' in st.session_state:
            code = st.session_state.generated_code
            context_lines.append(f"\nGRADIO CODE GENERATED: {len(code)} chars")

            # Extract key components from code
            if 'gr.Button' in code:
                button_count = code.count('gr.Button')
                context_lines.append(f"  Contains {button_count} buttons")
            if 'gr.Dropdown' in code:
                context_lines.append(f"  Contains dropdown navigation")
            if 'gr.Tabs' in code:
                context_lines.append(f"  Uses tabbed interface")

        # 4. CONVERSATION HISTORY
        recent_qa = st.session_state.user_messages[-5:] if len(st.session_state.user_messages) > 0 else []
        if recent_qa:
            context_lines.append("\nRECENT CONVERSATION:")
            for msg in recent_qa:
                if msg.get('role') in ['user', 'ux_designer']:
                    snippet = msg.get('content', '')[:60]
                    context_lines.append(f"  {msg.get('role')}: {snippet}...")

        context_text = "\n".join(context_lines)

        # BUILD PROMPT WITH RICH CONTEXT
        prompt = f"""You are the UX Designer agent who created this dashboard design.

THE USER'S QUESTION:
{user_input}

YOUR CONTEXT (what you have access to):
{context_text}

IMPORTANT:
- You designed this specific dashboard
- Answer based on what you actually created
- Reference specific components and data sources
- If asked about implementation details, you can see what Gradio Developer built
- If you don't know something, say so clearly

Please answer the user's question with specific details from your design."""

        # Call Claude with rich context
        try:
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            response = message.content[0].text
            self.add_user_message('ux_designer', response)
            self.add_agent_message('ux_designer', 'user', f"Answered: {user_input[:30]}...")
        except Exception as e:
            self.add_user_message('system', f"❌ Error: {e}")
```

---

### Step 2: Enhanced Context for Gradio Developer

```python
elif any(word in user_input.lower() for word in ['code', 'gradio', 'implement', 'how', 'error', 'dataset']):
    # Gradio Developer question
    self.add_agent_message('user', 'gradio_developer', user_input)

    # BUILD RICH CONTEXT
    impl_history = st.session_state.orchestrator.gradio_developer.implementation_history

    # Get data source context
    data_sources = st.session_state.context.get('data_sources', {})

    # Build comprehensive context
    context_lines = []

    # 1. DATA SOURCE CONTEXT (same as UX Designer)
    context_lines.append("DATA SOURCES YOU'RE WORKING WITH:")
    for source_name, source_info in data_sources.items():
        datasets = source_info.get('datasets', [])
        context_lines.append(f"  - {source_name}: {len(datasets)} datasets")
        for i, ds in enumerate(datasets[:3], 1):  # Show first 3
            context_lines.append(f"      {i}. {ds.get('name', 'Unknown')}")

    # 2. DESIGN SPEC CONTEXT (what UX Designer gave you)
    design_history = st.session_state.orchestrator.ux_designer.design_history
    if design_history:
        last_design = design_history[-1]
        context_lines.append("\nDESIGN SPEC YOU RECEIVED:")
        context_lines.append(f"  Screen Type: {last_design.get('screen_type')}")
        context_lines.append(f"  Components to implement: {len(last_design.get('components', []))}")
        for comp in last_design.get('components', []):
            context_lines.append(f"    - {comp.get('type')}: {comp.get('intent')}")

    # 3. YOUR GENERATED CODE (FULL, not just 500 chars!)
    if 'generated_code' in st.session_state:
        code = st.session_state.generated_code
        context_lines.append(f"\nCODE YOU GENERATED: {len(code)} chars")
        context_lines.append("=" * 60)
        context_lines.append(code)  # FULL CODE!
        context_lines.append("=" * 60)

    # 4. IMPLEMENTATION DETAILS
    if impl_history:
        last_impl = impl_history[-1]
        context_lines.append("\nYOUR IMPLEMENTATION DETAILS:")
        context_lines.append(f"  Components used: {last_impl.get('code_summary', 'N/A')}")
        context_lines.append(f"  Constraints applied: {', '.join(last_impl.get('constraints_applied', []))}")

    context_text = "\n".join(context_lines)

    # BUILD PROMPT
    prompt = f"""You are the Gradio Developer agent who implemented this dashboard.

THE USER'S QUESTION:
{user_input}

YOUR CONTEXT (what you have access to):
{context_text}

IMPORTANT:
- You wrote this specific Gradio code
- You can see the FULL code above
- You know exactly what data sources exist and how many datasets
- Answer based on what you actually implemented
- Reference specific code lines or components
- If you see a bug or issue, acknowledge it specifically

Please answer the user's question with specific technical details."""

    # Call Claude
    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,  # More tokens for technical answers
            messages=[{"role": "user", "content": prompt}]
        )
        response = message.content[0].text
        self.add_user_message('gradio_developer', response)
        self.add_agent_message('gradio_developer', 'user', f"Answered: {user_input[:30]}...")
    except Exception as e:
        self.add_user_message('system', f"❌ Error: {e}")
```

---

## Example: How This Fixes the Conversation

### Before (Broken)

**User:** "why do you show 1 dataset for rrc on the rrc card?"

**UX Designer (blind):** "From a UX design perspective, showing 1 dataset follows progressive disclosure..."

### After (Fixed)

**User:** "why do you show 1 dataset for rrc on the rrc card?"

**UX Designer (with context):** "Looking at the data sources, RRC actually has **3 datasets** available:
1. production_data
2. completion_data
3. well_info

The card shows '1 dataset' because the Gradio Developer only implemented display for the first dataset in the list. This is a bug - the card-grid component I designed should show all available datasets or indicate '3 datasets' not '1 dataset'. The progressive disclosure pattern I specified should allow users to see all datasets and select which to view."

---

### Before (Broken)

**User:** "how many datasets are in fact available for RRC?"

**Gradio Developer (blind):** "From a technical Gradio perspective, the exact number of RRC datasets isn't definitively answerable from this partial code..."

### After (Fixed)

**User:** "how many datasets are in fact available for RRC?"

**Gradio Developer (with context):** "According to the data sources I'm working with, **RRC has 3 datasets**:
1. production_data
2. completion_data
3. well_info

However, looking at my generated code, I see I'm only displaying the first dataset in the iteration. This is a bug on line 47 where I iterate through sources but only render the first dataset per source. I should fix this to show all datasets or properly aggregate the count."

---

## Key Changes Summary

### 1. Data Source Context
**Before:** Agents had no idea what data existed
**After:** Agents see all data sources with counts and names

### 2. Design Spec Context
**Before:** UX Designer couldn't see its own design
**After:** UX Designer sees full DesignSpec with components

### 3. Code Context
**Before:** Only 500 chars of code
**After:** FULL generated code available

### 4. Cross-Agent Context
**Before:** Agents work in silos
**After:** UX Designer sees what Gradio Developer built, and vice versa

### 5. Conversation History
**Before:** Each question is stateless
**After:** Agents see recent Q&A for context

---

## Implementation Priority

1. ✅ **CRITICAL:** Add data source context (fixes RRC question)
2. ✅ **CRITICAL:** Add full generated code (fixes "can't see my code" issue)
3. ✅ **HIGH:** Add design spec context (fixes "what did I design" issue)
4. ⏳ **MEDIUM:** Add conversation history
5. ⏳ **LOW:** Add visual screenshots (nice to have)

---

## Testing

After implementing, test with these exact questions from Session 1:

```
1. "why do you show 1 dataset for rrc on the rrc card?"
   → Should mention actual dataset count

2. "how many datasets are in fact available for RRC?"
   → Should give exact number and list them

3. "please review navigation on the left. what ux ui principles does it violate?"
   → Should reference the actual design and implementation
```

---

**Ready to implement this fix?** This will make agent conversations actually useful instead of weird and generic!