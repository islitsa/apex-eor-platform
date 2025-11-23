@echo off
REM Test Phase 7 Architecture in Agent Studio
REM This launches the Agent Studio with the new orchestrator

echo ============================================================
echo TESTING PHASE 7 ARCHITECTURE
echo ============================================================
echo.
echo Starting Agent Studio with:
echo   - UICodeOrchestrator (381-line thin wrapper)
echo   - OrchestratorAgent (procedural mode)
echo   - Tools Bundle (11 real tools)
echo   - SharedSessionMemory (Phase 6.2)
echo.
echo ============================================================
echo.

REM Activate virtual environment
call venv\Scripts\activate

REM Launch Agent Studio
streamlit run src\ui\agent_studio.py --server.port 8501

pause
