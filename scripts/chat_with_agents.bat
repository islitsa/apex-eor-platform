@echo off
echo ========================================
echo   Chat with Agent Interface
echo ========================================
echo.
echo Choose an option:
echo.
echo 1. Agent Studio (3-column: profile + your chat + agent chat) [RECOMMENDED]
echo 2. Watch agents generate dashboard (auto-run)
echo 3. Interactive chat (ask agents questions)
echo.
set /p choice="Enter choice (1, 2, or 3): "

if "%choice%"=="1" (
    echo.
    echo Launching Agent Studio (3-column layout)...
    streamlit run src\ui\agent_studio.py
) else if "%choice%"=="2" (
    echo.
    echo Launching agent dashboard generator...
    streamlit run src\ui\agent_chat_runner.py
) else if "%choice%"=="3" (
    echo.
    echo Launching interactive agent chat...
    streamlit run src\ui\agent_chat_interface.py
) else (
    echo Invalid choice!
    pause
)