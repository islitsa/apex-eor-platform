# How to Restart Agent Studio (To Load Code Changes)

## The Problem
When you edit Python files, Agent Studio keeps the old code in memory. Changes won't take effect until you fully restart all processes.

## Step-by-Step Restart Procedure

### Step 1: Kill All Processes
```batch
kill_all_agent_studio.bat
```

This will:
- Kill all Python processes
- Kill all Streamlit processes
- Check if ports 8000 and 8501 are free
- Show any remaining processes

### Step 2: Verify Ports Are Free
After running the kill script, you should see:
```
- Port 8000 is free
- Port 8501 is free
```

If you see "WARNING: Port still in use", you need to manually kill those processes:
```batch
# Find process ID (PID) from netstat output
netstat -ano | findstr ":8000"

# Kill by PID (replace 1234 with actual PID)
taskkill /F /PID 1234
```

### Step 3: Restart Agent Studio
Double-click: `Launch_Agent_Studio.vbs`

Or run manually:
```batch
launch_agent_studio_with_api.bat
```

### Step 4: Wait for Startup
- Wait 5-10 seconds for both servers to start
- Browser should open automatically to http://localhost:8501

### Step 5: Verify Code Is Loaded
Test with a prompt like:
```
generate a dashboard of production data from rrc
```

Check the **console output** (not the UI) for debug messages:
```
[DEBUG] User intent: generate a dashboard of production data from rrc
[DEBUG] All available sources: ['fracfocus', 'rrc', 'attribution', 'completions', 'production', 'treatments']
[DEBUG] Detected sources from prompt: ['rrc', 'production']
[Orchestrator] Filtering trace to show only: ['rrc', 'production']
```

Check the **trace output** (in UI) - should only show RRC and production, NOT all 6 sources.

## Common Issues

### Issue: Ports Still in Use
**Solution:** Close the batch file window completely, then run kill script again

### Issue: Multiple Python Processes
**Solution:** Open Task Manager, kill ALL python.exe processes manually

### Issue: Changes Still Not Loading
**Solution:**
1. Close browser completely (all tabs)
2. Run kill script
3. Wait 10 seconds
4. Restart

### Issue: Can't Find Process to Kill
**Solution:**
```batch
# List all Python processes
tasklist | findstr python

# Kill all Python
taskkill /F /IM python.exe

# List all Streamlit processes
tasklist | findstr streamlit

# Kill all Streamlit
taskkill /F /IM streamlit.exe
```

## What's Different Now?

After this restart, the prompt filtering will work correctly:

**Before:**
- Prompt: "rrc production data"
- Trace shows: ALL 6 sources

**After:**
- Prompt: "rrc production data"
- Trace shows: ONLY rrc and production

The fix parses your prompt to find which sources you mentioned, then filters the trace to show only those sources.
