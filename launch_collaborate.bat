@echo off
echo ================================================================
echo   Launching Collaborative Agent UI Generator
echo ================================================================
echo.
echo Context: 4 data sources, 216M records
echo Model: Claude 3.5 Sonnet
echo.
echo Opening browser at http://localhost:8501
echo.
echo Press Ctrl+C to stop when done
echo ================================================================
echo.

streamlit run src\ui\agent_collaborative_system.py
