@echo off
echo ===================================================================
echo Launching Pipeline with Agent Studio (with Trace Collection)
echo ===================================================================
echo.
echo Step 1: Killing any existing Streamlit processes...
call kill_streamlit.bat
echo.
echo Step 2: Activating virtual environment...
call venv\Scripts\activate
echo.
echo Step 3: Running pipeline with UI...
echo.
python scripts/pipeline/run_ingestion.py --generate-context --launch-ui collaborate
