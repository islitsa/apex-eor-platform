@echo off
echo ================================================================
echo   Activating venv and launching Collaborative Agents
echo ================================================================
echo.

REM Activate venv
call venv\Scripts\activate.bat

REM Verify we're in venv
python -c "import sys; print('Python:', sys.executable)"

echo.
echo Checking AutoGen installation...
python -c "import autogen_agentchat; print('AutoGen OK')" || (
    echo.
    echo ERROR: AutoGen not found in venv!
    echo Installing now...
    pip install pyautogen autogen-ext[anthropic]
)

echo.
echo Launching Streamlit...
echo Browser will open at http://localhost:8501
echo.
echo Press Ctrl+C to stop
echo ================================================================
echo.

streamlit run src\ui\agent_collaborative_system.py

REM Deactivate venv when done
deactivate
