@echo off
echo Killing all Agent Studio processes...
echo.

echo Killing Python (uvicorn API)...
taskkill /F /IM python.exe 2>nul
if %ERRORLEVEL% EQU 0 (
    echo   - Python processes killed
) else (
    echo   - No Python processes found
)

echo.
echo Killing Streamlit...
taskkill /F /IM streamlit.exe 2>nul
if %ERRORLEVEL% EQU 0 (
    echo   - Streamlit processes killed
) else (
    echo   - No Streamlit processes found
)

echo.
echo Checking port 8000...
netstat -ano | findstr ":8000" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   WARNING: Port 8000 still in use!
    netstat -ano | findstr ":8000"
) else (
    echo   - Port 8000 is free
)

echo.
echo Checking port 8501...
netstat -ano | findstr ":8501" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   WARNING: Port 8501 still in use!
    netstat -ano | findstr ":8501"
) else (
    echo   - Port 8501 is free
)

echo.
echo All processes killed. Wait 2 seconds before restarting...
timeout /t 2 /nobreak >nul
echo.
echo Ready to restart Agent Studio!
pause
