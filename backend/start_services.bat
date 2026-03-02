@echo off
chcp 65001 >nul
echo ========================================
echo Starting ASD Agent Backend Services
echo ========================================
echo.

REM Check if in correct directory
if not exist "memory_service.py" (
    echo [ERROR] Please run this script in the backend directory
    pause
    exit /b 1
)

REM Check .env file
if not exist ".env" (
    echo [WARNING] .env file not found, please configure environment variables first
    echo You can copy .env.example and modify the configuration
    pause
    exit /b 1
)

echo [1/4] Checking Neo4j connection...
docker ps | findstr neo4j >nul
if errorlevel 1 (
    echo [WARNING] Neo4j container not running, attempting to start...
    docker start neo4j 2>nul
    if errorlevel 1 (
        echo [INFO] If this is your first run, please execute:
        echo docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:5.26
        pause
        exit /b 1
    )
    timeout /t 5 /nobreak >nul
)
echo Neo4j is ready

echo.
echo [2/4] Starting Memory Service (port 8000)...
start "Memory Service" cmd /k "uvicorn memory_service:app --port 8000 --reload"
timeout /t 2 /nobreak >nul

echo.
echo [3/4] Starting RAG Knowledge Service (port 8001)...
start "RAG Service" cmd /k "uvicorn rag_service:app --port 8001 --reload"
timeout /t 2 /nobreak >nul

echo.
echo [4/4] Starting Realtime Video Call Service (port 8766)...
start "Realtime Service" cmd /k "python qwen_realtime_websocket.py"
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo All services started successfully
echo ========================================
echo.
echo Service URLs:
echo   Memory Service:    http://localhost:8000
echo   Health Check:      http://localhost:8000/healthcheck
echo   RAG Service:       http://localhost:8001
echo   RAG Health Check:  http://localhost:8001/healthcheck
echo   Realtime WebSocket: ws://localhost:8766
echo.
echo Press any key to close this window (services will continue running)
pause >nul
