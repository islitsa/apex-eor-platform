# OpenAI Fine-tuning Guide for UI Agent

Complete guide to fine-tune GPT-4 on UI generation patterns using the evolutionary critique system.

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Step-by-Step Workflow](#step-by-step-workflow)
4. [Cost Estimates](#cost-estimates)
5. [Timeline](#timeline)
6. [Troubleshooting](#troubleshooting)

---

## Overview

This guide walks you through fine-tuning GPT-4 to fix the UI Agent's behavioral pattern of generating config files instead of actual UI components.

**The Problem We're Solving:**
- Current UI Agent generates `config.py`, `requirements.txt`, etc. FIRST
- It rarely generates actual Streamlit components (`st.title()`, `st.button()`, etc.)
- Users expect dashboard code, but get infrastructure code instead

**The Solution:**
- Use evolutionary critique to generate 300+ training examples
- Fine-tune GPT-4 on these examples showing correct behavior
- System message explicitly teaches: "Generate ACTUAL UI code first"

---

## Prerequisites

### 1. OpenAI Account Setup

1. **Create OpenAI Account:**
   - Go to: https://platform.openai.com/signup
   - Sign up with email

2. **Add Payment Method:**
   - Go to: https://platform.openai.com/account/billing
   - Add credit card (required for fine-tuning)
   - Recommended: Add $50 credit

3. **Get API Key:**
   - Go to: https://platform.openai.com/api-keys
   - Click "Create new secret key"
   - Name it: `UI Agent Fine-tuning`
   - Copy the key (starts with `sk-`)

4. **Add to .env:**
   ```bash
   OPENAI_API_KEY=sk-your-key-here
   ```

### 2. Install OpenAI SDK

```bash
pip install openai
```

### 3. Verify Installation

```bash
python -c "import openai; print(openai.__version__)"
```

Should print version like `1.12.0` or higher.

---

## Step-by-Step Workflow

### Phase 1: Generate Training Data (Optional but Recommended)

**Time:** ~3 hours
**Output:** 300+ training examples from evolutionary critique

```bash
# Generate 100 UI evolutions (contact forms, dashboards, tables, etc.)
python scripts/generate_training_dataset.py
```

**What This Does:**
- Runs 100 different UI descriptions through evolutionary critique
- Each evolution produces 2-4 iterations of improvement
- Logs saved to: `data/evolutionary_logs/*.json`
- Creates 300+ prompt/response pairs showing:
  - Initial bad version (config files only)
  - Final good version (actual UI components)
  - Improvement trajectory

**Can I Skip This?**
- Yes, if you already ran some evolutions manually
- Minimum recommended: 50+ evolution logs
- More data = better fine-tuning results

---

### Phase 2: Prepare Dataset for OpenAI

**Time:** ~1 minute
**Output:** `data/ui_agent_openai_finetuning.jsonl`

```bash
# Convert evolution logs to OpenAI JSONL format
python scripts/prepare_openai_finetuning.py
```

**What This Does:**
- Reads all files in `data/evolutionary_logs/`
- Extracts positive examples (final versions that scored 7.0+)
- Extracts improvement examples (showing iteration trajectory)
- Formats in OpenAI's required structure:
  ```json
  {
    "messages": [
      {"role": "system", "content": "You are an expert UI/UX developer..."},
      {"role": "user", "content": "Create a Streamlit dashboard..."},
      {"role": "assistant", "content": "import streamlit as st\nst.title(...)"}
    ]
  }
  ```

**Output Sample:**
```
Found 100 evolution logs
Total Examples: 150
Format: JSONL (OpenAI fine-tuning format)

[OK] Dataset saved to: data/ui_agent_openai_finetuning.jsonl
     Size: 2.3 MB
```

---

### Phase 3: Execute Fine-tuning

**Time:** 1-2 hours (mostly waiting)
**Output:** Fine-tuned model ID like `ft:gpt-4o-2024-08-06:org:ui-agent-v1:abc123`

```bash
# Start fine-tuning job
python scripts/finetune_openai.py
```

**What This Does:**

1. **Validates prerequisites:**
   - OpenAI SDK installed
   - API key in .env
   - Dataset file exists

2. **Uploads dataset to OpenAI:**
   ```
   Uploading: data/ui_agent_openai_finetuning.jsonl
   Size: 2.3 MB
   [OK] Upload complete
       File ID: file-abc123
   ```

3. **Starts fine-tuning job:**
   ```
   Base Model: gpt-4o-2024-08-06
   Suffix: ui-agent-v1
   [OK] Fine-tuning job started
       Job ID: ftjob-abc123
       Status: validating_files
   ```

4. **Monitors progress:**
   ```
   [10:30:15] Status: running
              Tokens trained: 125,000
   [10:45:20] Status: running
              Tokens trained: 250,000
   [11:00:25] Status: succeeded

   ====================================================================
   FINE-TUNING COMPLETE!
   ====================================================================
   Fine-tuned Model: ft:gpt-4o-2024-08-06:org:ui-agent-v1:abc123
   ```

**Can I Close the Script?**
- Yes! Job continues in background on OpenAI's servers
- Check status anytime with:
  ```bash
  python scripts/check_finetuning_status.py ftjob-abc123
  ```

---

### Phase 4: Test Fine-tuned Model

**Time:** ~2 minutes
**Output:** Comparison of base vs fine-tuned model behavior

```bash
# Test the fine-tuned model (will be created next)
python scripts/test_finetuned_model.py
```

**What This Tests:**
- Give same prompt to base GPT-4 and fine-tuned model
- Compare outputs side-by-side
- Verify fine-tuned model generates actual UI code first

**Expected Result:**

**Base GPT-4:**
```python
# config.py
COLORS = {"primary": "#1976D2"}

# requirements.txt
streamlit>=1.28.0
```

**Fine-tuned Model:**
```python
# dashboard.py
import streamlit as st

st.title("Production Dashboard")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Active Wells", "1,234")
with col2:
    st.metric("Daily Production", "45,678 BBL")
```

✅ **Success!** Fine-tuned model generates UI components first.

---

### Phase 5: Update UI Agent

**Time:** ~5 minutes
**Action:** Modify UI Agent to use fine-tuned model

#### Option A: Replace Default Model (Recommended)

Edit `src/agents/ui_agent.py`:

```python
class UIAgent:
    def __init__(self, api_key: str = None):
        # Before:
        # self.model = "claude-sonnet-4-20250514"

        # After (use your actual fine-tuned model ID):
        self.model = "ft:gpt-4o-2024-08-06:org:ui-agent-v1:abc123"

        # Switch to OpenAI client
        from openai import OpenAI
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

Update the `generate_ui` method to use OpenAI API format instead of Anthropic.

#### Option B: Create Separate Fine-tuned UI Agent

Create `src/agents/finetuned_ui_agent.py`:

```python
"""Fine-tuned UI Agent using OpenAI GPT-4"""

import os
from openai import OpenAI
from typing import Dict

class FinetunedUIAgent:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # Load model ID from saved file
        with open("data/finetuned_model_id.txt", 'r') as f:
            self.model = f.read().strip()

    def generate_ui(self, description: str, framework: str = "Streamlit") -> Dict[str, str]:
        """Generate UI using fine-tuned model"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert UI/UX developer specializing in Streamlit applications."
                },
                {
                    "role": "user",
                    "content": f"Create a {framework} UI: {description}"
                }
            ],
            temperature=0.7
        )

        # Parse response into files
        # (Implementation similar to original UIAgent)
        return files
```

Use this in evolutionary system:
```python
from src.agents.finetuned_ui_agent import FinetunedUIAgent

system = EvolutionaryUISystem(ui_agent=FinetunedUIAgent())
```

---

## Cost Estimates

### Training Costs

OpenAI charges based on tokens processed:

**GPT-4o Fine-tuning Pricing (as of 2024):**
- Training: $25 per 1M tokens
- Input usage: $3.75 per 1M tokens (same as base GPT-4o)
- Output usage: $15 per 1M tokens (same as base GPT-4o)

**Example Cost Calculation:**

Assuming 150 examples averaging 1,500 tokens each:
- Total training tokens: 150 × 1,500 = 225,000 tokens
- Training cost: 225,000 / 1,000,000 × $25 = **$5.63**
- One-time training cost: ~$6

**Inference Costs:**

After fine-tuning, using the model costs the same as base GPT-4o:
- Input: $3.75 per 1M tokens
- Output: $15 per 1M tokens

For comparison with Anthropic Claude:
- Claude Sonnet 4: $3 per 1M input, $15 per 1M output
- **Similar pricing!**

---

## Timeline

| Phase | Task | Duration | Can Run Overnight? |
|-------|------|----------|-------------------|
| 1 | Generate training data (100 evolutions) | 3 hours | ✅ Yes |
| 2 | Prepare dataset | 1 minute | ❌ No need |
| 3 | Upload dataset | 30 seconds | ❌ No need |
| 4 | Fine-tuning job | 1-2 hours | ✅ Yes |
| 5 | Test fine-tuned model | 2 minutes | ❌ No |
| 6 | Update UI Agent | 5 minutes | ❌ No |
| **Total** | **End-to-end** | **~4-5 hours** | **Mostly automated** |

**Recommended Schedule:**
- **Day 1 Evening:** Start `generate_training_dataset.py`, let run overnight
- **Day 2 Morning:** Run prepare + upload (2 minutes), start fine-tuning
- **Day 2 Lunch:** Fine-tuning complete, test and deploy

---

## Troubleshooting

### Error: "OpenAI API key not found"

**Cause:** `.env` missing `OPENAI_API_KEY`

**Fix:**
1. Get API key from https://platform.openai.com/api-keys
2. Add to `.env`:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```
3. Restart script

---

### Error: "Insufficient quota"

**Cause:** OpenAI account needs payment method or insufficient credits

**Fix:**
1. Go to: https://platform.openai.com/account/billing
2. Add payment method
3. Add $50 credit (fine-tuning requires prepaid credits)
4. Wait ~5 minutes for credits to appear
5. Retry

---

### Error: "Training file has invalid format"

**Cause:** JSONL file doesn't meet OpenAI requirements

**Fix:**
1. Validate dataset:
   ```bash
   python -c "import json; [json.loads(line) for line in open('data/ui_agent_openai_finetuning.jsonl')]"
   ```
2. If error, regenerate:
   ```bash
   python scripts/prepare_openai_finetuning.py
   ```

---

### Fine-tuning Job Stuck in "validating_files"

**Normal:** This status can last 5-10 minutes

**If stuck >30 minutes:**
```bash
# Cancel and restart
python scripts/check_finetuning_status.py <job-id>
```

Check OpenAI status page: https://status.openai.com

---

### Fine-tuned Model Still Generates Config Files

**Possible Causes:**
1. Not enough training examples (need 50+ diverse examples)
2. System message not included in prompts
3. Training data quality issues

**Fix:**
1. Generate more training data:
   ```bash
   python scripts/generate_training_dataset.py
   ```
2. Retrain with more epochs:
   - Edit `scripts/finetune_openai.py`
   - Change `n_epochs: 3` to `n_epochs: 5`
3. Add system message to UI Agent prompts:
   ```python
   system_message = "You are an expert UI/UX developer. Generate ACTUAL UI code first, not config files."
   ```

---

## Next Steps After Fine-tuning

1. **Test extensively:**
   - Try 10+ different UI descriptions
   - Verify all generate actual UI components first
   - Compare quality to base model

2. **Continue evolution:**
   - Use fine-tuned model in evolutionary system
   - Generate more training data
   - Fine-tune again for further improvement

3. **Monitor performance:**
   - Track critique scores over time
   - Identify remaining issues
   - Iterate on training data

4. **Document learnings:**
   - Save successful prompts
   - Note behavioral improvements
   - Share insights with team

---

## Support

- **OpenAI Documentation:** https://platform.openai.com/docs/guides/fine-tuning
- **OpenAI Community:** https://community.openai.com
- **Pricing:** https://openai.com/pricing
- **Status:** https://status.openai.com

---

## Summary

**You've built an automated fine-tuning pipeline that:**
1. ✅ Generates training data through evolutionary critique
2. ✅ Prepares dataset in OpenAI format
3. ✅ Executes fine-tuning job
4. ✅ Tests and deploys fine-tuned model

**Total time investment:** ~5 hours (mostly automated)
**Total cost:** ~$6 for training + standard inference costs
**Expected improvement:** UI Agent generates actual UI code instead of config files

**This is a production-ready system for continuously improving your AI agents through evolution and fine-tuning.**
