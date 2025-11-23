@echo off
echo ===================================================================
echo Starting Agent Studio with Trace Collection
echo ===================================================================
echo.
echo URL will be shown below when ready...
echo.
call venv\Scripts\activate
streamlit run src\ui\agent_studio.py
