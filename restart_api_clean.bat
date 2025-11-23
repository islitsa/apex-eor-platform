@echo off
echo ================================================================================
echo CLEAN RESTART OF API SERVER
echo ================================================================================
echo.
echo Step 1: Killing ALL Python processes...
taskkill /F /IM python.exe 2>nul
echo.
echo Step 2: Waiting 3 seconds...
timeout /t 3 /nobreak >nul
echo.
echo Step 3: Starting fresh API server with --reload...
echo API will be available at: http://localhost:8000
echo API docs: http://localhost:8000/docs
echo.
python -m uvicorn src.api.data_service:app --host 0.0.0.0 --port 8000 --reload
