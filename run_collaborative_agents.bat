@echo off
echo ================================================
echo Launching Collaborative Agent UI Generator
echo ================================================
echo.
echo This system uses REAL agent collaboration with:
echo - UX Designer proposing designs
echo - Gradio Developer providing technical feedback
echo - UX Critic reviewing implementations
echo - Code Reviewer ensuring quality
echo.
echo Make sure ANTHROPIC_API_KEY is set!
echo.
pause

streamlit run src\ui\agent_collaborative_system.py
