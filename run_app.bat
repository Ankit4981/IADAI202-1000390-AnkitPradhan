@echo off
title LogiSight Analytics Launcher
echo ===================================================
echo Starting LogiSight Analytics Dashboard...
echo ===================================================

:: Free port 8501 if a previous process is lingering
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8501 ^| findstr LISTENING') do (
    echo Freeing port 8501 (PID: %%a)...
    taskkill /F /PID %%a >nul 2>&1
)

:: Run Streamlit using virtual environment if present, else system python
if exist ".venv\Scripts\streamlit.exe" (
    call .venv\Scripts\streamlit.exe run app.py
) else (
    streamlit run app.py
)
pause
