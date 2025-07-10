@echo off
echo Starting Minions and Master...

start "Minion 8001" cmd /k "venv\Scripts\activate && uvicorn app.minion.main:app --port 8001"
start "Minion 8002" cmd /k "venv\Scripts\activate && uvicorn app.minion.main:app --port 8002"
start "Minion 8003" cmd /k "venv\Scripts\activate && uvicorn app.minion.main:app --port 8003"
start "Minion 8004" cmd /k "venv\Scripts\activate && uvicorn app.minion.main:app --port 8004"

timeout /t 3 >nul

start "Master" cmd /k "venv\Scripts\activate && python -m app.master.main"
