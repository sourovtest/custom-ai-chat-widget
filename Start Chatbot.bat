@echo off
setlocal
cd /d "%~dp0"
title Start Chatbot

if not exist "backend\.env" (
  if not exist "backend\.env.example" (
    echo ERROR: backend\.env.example was not found.
    goto failed
  )
  copy /Y "backend\.env.example" "backend\.env" >nul
  echo Created backend\.env from the example.
  echo Add your MySQL settings and optional AI API key, then run this file again.
  goto failed
)

if not exist ".venv\Scripts\python.exe" (
  where py >nul 2>nul
  if errorlevel 1 (
    echo ERROR: Install Python 3.10 or newer with the Python Launcher, then try again.
    goto failed
  )
  echo Creating the chatbot Python environment...
  py -3 -m venv .venv
  if errorlevel 1 (
    echo ERROR: Could not create the Python environment.
    goto failed
  )
)

set "CHATBOT_PYTHON=%CD%\.venv\Scripts\python.exe"
"%CHATBOT_PYTHON%" -c "import fastapi, uvicorn, mysql.connector, dotenv, google.generativeai" >nul 2>&1
if errorlevel 1 (
  echo Installing chatbot dependencies...
  "%CHATBOT_PYTHON%" -m pip install -r backend\requirements.txt
  if errorlevel 1 (
    echo ERROR: Dependency installation failed. Check your internet connection and try again.
    goto failed
  )
)

call :is_running
if not errorlevel 1 goto open_chatbot

echo Starting the chatbot server...
start "Bongora Chatbot Server" /D "%CD%" "%CHATBOT_PYTHON%" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

call :wait_for_server
if errorlevel 1 (
  echo ERROR: The chatbot server did not start. Check its server window for details.
  goto failed
)

:open_chatbot
if /I "%CHATBOT_SKIP_BROWSER%"=="1" goto server_ready
start "" "http://127.0.0.1:8000/"
echo Chatbot opened in your browser.
goto server_status

:server_ready
echo Chatbot server is ready at http://127.0.0.1:8000/

:server_status
echo Keep the "Bongora Chatbot Server" window open while using it.
echo Close that server window to stop the chatbot.
exit /b 0

:is_running
powershell -NoProfile -Command "$ProgressPreference='SilentlyContinue'; try { $health=Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:8000/health' -TimeoutSec 2; $page=Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:8000/' -TimeoutSec 2; if ($health.StatusCode -eq 200 -and $page.StatusCode -eq 200) { exit 0 } } catch {}; exit 1" >nul 2>&1
exit /b %errorlevel%

:wait_for_server
powershell -NoProfile -Command "$ProgressPreference='SilentlyContinue'; $deadline=[DateTime]::UtcNow.AddSeconds(30); do { try { $health=Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:8000/health' -TimeoutSec 2; $page=Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:8000/' -TimeoutSec 2; if ($health.StatusCode -eq 200 -and $page.StatusCode -eq 200) { exit 0 } } catch {}; Start-Sleep -Seconds 1 } while ([DateTime]::UtcNow -lt $deadline); exit 1" >nul 2>&1
exit /b %errorlevel%

:failed
pause
exit /b 1
