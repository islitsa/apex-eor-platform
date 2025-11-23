@echo off
echo ================================================================================
echo CLEAN API RESTART - Port 8000
echo ================================================================================
echo.
echo Step 1: Killing Streamlit and all Python processes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul
echo.
echo Step 2: Waiting 5 seconds for ports to release...
timeout /t 5 /nobreak >nul
echo.
echo Step 3: Starting FRESH API on port 8000...
echo.
echo API ready at: http://localhost:8000
echo API docs at: http://localhost:8000/docs
echo.
echo ================================================================================
echo.
python -m uvicorn src.api.data_service:app --host 0.0.0.0 --port 8000 --reload
