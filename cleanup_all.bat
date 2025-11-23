@echo off
echo Cleaning up all running servers...

REM Kill all Python processes (Streamlit, API)
taskkill /F /IM python.exe 2>nul
echo Killed Python processes

REM Kill all Node processes (Vite dev server)
taskkill /F /IM node.exe 2>nul
echo Killed Node processes

REM Wait a moment
timeout /t 2 /nobreak >nul

echo.
echo All servers stopped!
echo You can now launch Agent Studio with the VBS file.
pause
