@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo.
echo === Delphi: full stack (API + Explorer + Streamlit) ===
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo [Delphi] Python was not found. Install from https://www.python.org/
    exit /b 1
)
where node >nul 2>nul
if errorlevel 1 (
    echo [Delphi] Node.js was not found. Install from https://nodejs.org/
    exit /b 1
)
where npm >nul 2>nul
if errorlevel 1 (
    echo [Delphi] npm was not found. Reinstall Node.js from https://nodejs.org/
    exit /b 1
)

echo [Delphi] Upgrading pip and installing Python packages...
python -m pip install --upgrade pip -q
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [Delphi] pip install failed.
    exit /b 1
)

echo [Delphi] Installing Radar / Explorer npm packages...
pushd "%~dp0web"
if exist package-lock.json (
    call npm ci
) else (
    call npm install
)
if errorlevel 1 (
    echo [Delphi] npm install failed.
    popd
    exit /b 1
)
popd

echo.
echo [Delphi] Starting API      - http://127.0.0.1:8000  ^(new window^)
start "Delphi API" /D "%~dp0" cmd /k "python -m uvicorn api.main:app --host 127.0.0.1 --port 8000"

echo [Delphi] Starting Explorer - http://127.0.0.1:5173  ^(new window^)
start "Delphi Explorer" /D "%~dp0web" cmd /k "npm run dev"

echo [Delphi] Waiting a few seconds for API and Vite to start...
timeout /t 8 /nobreak >nul

set "DELPHI_RADAR_URL=http://127.0.0.1:5173"
echo.
echo [Delphi] Starting website  - Streamlit ^(this window^)
echo [Delphi] Open http://localhost:8501 in your browser.
echo [Delphi] Close this window to stop Streamlit. API and Explorer keep running in their own windows until you close them.
echo.
python -m streamlit run app.py

endlocal
exit /b %ERRORLEVEL%
