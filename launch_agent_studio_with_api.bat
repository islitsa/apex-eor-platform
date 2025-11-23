@echo off
echo ================================================================================
echo APEX EOR Platform - Agent Studio Launcher
echo ================================================================================
echo.
echo Starting backend API server on port 8000...
echo Starting Agent Studio on port 8501...
echo.
echo Press Ctrl+C to stop both servers
echo ================================================================================
echo.

REM Start backend API in background
start /B python -m uvicorn src.api.data_service:app --host 0.0.0.0 --port 8000 --reload

REM Wait 3 seconds for API to start
timeout /t 3 /nobreak >nul

REM Start Agent Studio (this will keep the window open)
streamlit run src/ui/agent_studio.py --server.port 8501

REM When streamlit exits, kill background API server
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *uvicorn*" 2>nul
