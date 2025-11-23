@echo off
echo ================================================================
echo    APEX EOR Platform - Collaborative Agent UI Generator
echo ================================================================
echo.
echo This will:
echo   1. Generate context from your existing data
echo   2. Launch the collaborative multi-agent system
echo   3. Agents will work together to create your UI
echo.
echo Make sure ANTHROPIC_API_KEY is set!
echo.
pause

echo.
echo [1/2] Generating context from pipeline data...
python scripts\pipeline\run_ingestion.py --generate-context

echo.
echo [2/2] Launching collaborative agent system...
echo.
echo Watch the agents collaborate in your browser!
echo.

streamlit run src\ui\agent_collaborative_system.py
