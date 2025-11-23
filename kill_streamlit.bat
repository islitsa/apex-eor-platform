@echo off
echo Killing all Streamlit processes...
taskkill /F /IM streamlit.exe 2>nul
if %errorlevel% equ 0 (
    echo All Streamlit processes killed.
) else (
    echo No Streamlit processes found.
)
timeout /t 2 >nul
