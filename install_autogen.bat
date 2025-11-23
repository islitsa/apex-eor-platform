@echo off
echo ============================================
echo Installing AutoGen for Agent Chat Runner
echo ============================================
echo.

echo [1/3] Installing pyautogen...
pip install pyautogen

echo.
echo [2/3] Installing litellm (for better Claude support)...
pip install litellm

echo.
echo [3/3] Installing other dependencies...
pip install python-dotenv

echo.
echo ============================================
echo Installation Complete!
echo ============================================
echo.
echo Next steps:
echo 1. Make sure ANTHROPIC_API_KEY is set in your environment
echo 2. Run: streamlit run src\ui\agent_chat_runner_autogen.py
echo.
echo If you have issues, run: python autogen_setup_guide.py
echo.
pause
