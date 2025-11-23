# Quick Start: Fine-tune UI Agent in 5 Steps

## Setup (One-time, 5 minutes)

1. **Get OpenAI API Key:**
   - Go to: https://platform.openai.com/api-keys
   - Create new key
   - Add to `.env`:
     ```
     OPENAI_API_KEY=sk-your-key-here
     ```

2. **Install OpenAI SDK:**
   ```bash
   pip install openai
   ```

---

## Option A: Quick Fine-tuning (Use Existing Data)

If you already have evolution logs from testing:

```bash
# 1. Prepare dataset (1 minute)
python scripts/prepare_openai_finetuning.py

# 2. Start fine-tuning (1-2 hours, runs in background)
python scripts/finetune_openai.py

# 3. Done! Fine-tuned model ID saved to: data/finetuned_model_id.txt
```

---

## Option B: Full Pipeline (Generate Fresh Data)

If you want to generate 300+ new training examples:

```bash
# 1. Generate training data (3 hours - run overnight)
python scripts/generate_training_dataset.py

# 2. Prepare dataset (1 minute)
python scripts/prepare_openai_finetuning.py

# 3. Start fine-tuning (1-2 hours)
python scripts/finetune_openai.py

# 4. Done! Model ID saved to: data/finetuned_model_id.txt
```

---

## Check Status Anytime

```bash
# List all fine-tuning jobs
python scripts/check_finetuning_status.py

# Check specific job
python scripts/check_finetuning_status.py ftjob-abc123
```

---

## Cost

- **Training:** ~$6 for 150 examples
- **Usage:** Same as GPT-4o ($3.75 input, $15 output per 1M tokens)

---

## What Happens

**Before Fine-tuning:**
```python
# User asks: "Create a dashboard"
# UI Agent generates:
# config.py ❌
COLORS = {"primary": "#1976D2"}
```

**After Fine-tuning:**
```python
# User asks: "Create a dashboard"
# UI Agent generates:
# dashboard.py ✅
import streamlit as st
st.title("Dashboard")
st.metric("Users", "1,234")
```

---

## Full Documentation

- **Complete guide:** [OPENAI_FINETUNING_GUIDE.md](OPENAI_FINETUNING_GUIDE.md)
- **System architecture:** [EVOLUTIONARY_UI_SYSTEM_COMPLETE.md](EVOLUTIONARY_UI_SYSTEM_COMPLETE.md)
- **Troubleshooting:** See guides above
