# Fine-Tuning Guide for UI Agent

## Complete Step-by-Step Process

### Step 1: Generate Training Data (Overnight - 3 hours)

```bash
python scripts/generate_training_dataset.py
```

**What this does:**
- Generates 100 different UIs (forms, tables, dashboards, charts, etc.)
- Each UI goes through 3-4 iterations of improvement
- Saves all evolution logs to `data/evolutionary_logs/`

**Result:** 100+ JSON files with before/after examples

---

### Step 2: Prepare Fine-tuning Dataset (5 minutes)

```bash
python scripts/prepare_finetuning_dataset.py
```

**What this does:**
- Reads all evolution logs
- Extracts 3 types of examples per evolution:
  1. **Negative example**: What NOT to do (config-only files)
  2. **Positive example**: What TO do (actual Streamlit code)
  3. **Improvement example**: How to refine iteratively
- Formats everything for Anthropic's fine-tuning API

**Result:** `data/ui_agent_finetuning_dataset.json` (~300+ training examples)

---

### Step 3: Fine-Tune with Anthropic (1-4 hours)

#### Option A: Using Anthropic Console (Easy)

1. **Go to:** https://console.anthropic.com/settings/fine-tuning

2. **Click:** "Create Fine-tuning Job"

3. **Upload:** `data/ui_agent_finetuning_dataset.json`

4. **Configure:**
   - Base Model: `claude-sonnet-4-20250514`
   - Training Steps: Auto (recommended)
   - Learning Rate: Auto (recommended)
   - Validation Split: 10%

5. **Start Training**

6. **Monitor:** Progress in the console

7. **Get Model ID:** When complete, you'll get a model ID like:
   ```
   ft:claude-sonnet-4:your-org:ui-agent-v1:abc123
   ```

#### Option B: Using Anthropic API (Advanced)

```python
from anthropic import Anthropic

client = Anthropic(api_key="your-api-key")

# Create fine-tuning job
with open("data/ui_agent_finetuning_dataset.json", "rb") as f:
    job = client.fine_tuning.jobs.create(
        model="claude-sonnet-4-20250514",
        training_file=f,
        hyperparameters={
            "n_epochs": 3,
            "learning_rate_multiplier": 1.0
        }
    )

print(f"Fine-tuning job created: {job.id}")
print(f"Status: {job.status}")

# Monitor progress
while job.status != "completed":
    time.sleep(60)  # Check every minute
    job = client.fine_tuning.jobs.retrieve(job.id)
    print(f"Status: {job.status}")

print(f"Fine-tuned model: {job.fine_tuned_model}")
```

---

### Step 4: Update UI Agent to Use Fine-Tuned Model (2 minutes)

Edit `src/agents/ui_agent.py`:

```python
# Find this section (around line 50):
self.client = Anthropic(api_key=self.api_key)

# Add after it:
self.model = "ft:claude-sonnet-4:your-org:ui-agent-v1:abc123"  # Your fine-tuned model ID
```

Then update the `chat()` method (around line 385):

```python
# Change this:
response = self.client.messages.create(
    model="claude-sonnet-4-20250514",  # Old base model
    ...
)

# To this:
response = self.client.messages.create(
    model=self.model,  # Fine-tuned model
    ...
)
```

---

### Step 5: Test the Fine-Tuned Agent (5 minutes)

```python
from src.agents.ui_agent import UIAgent

agent = UIAgent()

# Test with the same prompt that failed before
response = agent.generate_ui(
    description="Create a pipeline dashboard with status indicators",
    framework="Streamlit"
)

# Should now generate ACTUAL dashboard code, not just config!
for filename, code in response.items():
    print(f"Generated: {filename}")
```

---

## Expected Improvements After Fine-Tuning

### Before Fine-Tuning:
```
Prompt: "Create a dashboard"

Generated Files:
✗ config.py
✗ requirements.txt
✗ utils.py
✗ NO DASHBOARD!
```

### After Fine-Tuning:
```
Prompt: "Create a dashboard"

Generated Files:
✓ dashboard.py (with st.title(), st.button(), st.dataframe())
✓ utils.py (supporting functions)
✓ config.py (if needed)
✓ ACTUAL WORKING DASHBOARD!
```

---

## Training Dataset Statistics (Expected)

From 100 UI evolutions with 3-4 iterations each:

- **~100 negative examples**: Shows what NOT to do
- **~100 positive examples**: Shows what TO do
- **~100 improvement examples**: Shows how to refine
- **Total: ~300 training examples**

Each example includes:
- User prompt
- Generated code
- Critique scores
- Design guideline citations
- Improvement suggestions

---

## Cost Estimate

**Anthropic Fine-Tuning Pricing:**
- Training: ~$10-30 per 1M tokens
- Your dataset: ~300 examples × 2000 tokens = 600K tokens
- **Estimated cost: $6-18**

**Worth it?** Absolutely! Fixes the core UI generation problem permanently.

---

## Troubleshooting

### "Dataset format invalid"
Check that the JSON has this structure:
```json
{
  "examples": [
    {
      "messages": [
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."}
      ]
    }
  ]
}
```

### "Not enough examples"
Anthropic requires minimum 10 examples. You should have 300+.

### "Fine-tuning failed"
Check logs in Anthropic console for specific error.

---

## Timeline Summary

1. **Generate data**: 3 hours (overnight)
2. **Prepare dataset**: 5 minutes
3. **Upload & configure**: 10 minutes
4. **Fine-tuning**: 1-4 hours (automatic)
5. **Update agent**: 2 minutes
6. **Test**: 5 minutes

**Total hands-on time: ~20 minutes**
**Total wait time: 4-7 hours**

---

## What You'll Get

A UI Agent that:
- ✅ Generates actual Streamlit code first (not just config)
- ✅ Includes proper components (st.button, st.dataframe, etc.)
- ✅ Follows Material Design 3 guidelines
- ✅ Implements accessibility features (ARIA labels)
- ✅ Iteratively improves when given feedback
- ✅ Cites design guidelines in comments

**Ready to start?**

```bash
# Step 1: Generate training data
python scripts/generate_training_dataset.py

# (Wait 3 hours)

# Step 2: Prepare dataset
python scripts/prepare_finetuning_dataset.py

# Step 3: Go to https://console.anthropic.com/settings/fine-tuning
```

---

**Last Updated**: 2025-10-24
**Status**: Ready to fine-tune! 🚀
