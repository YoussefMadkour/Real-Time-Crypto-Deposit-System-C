#!/bin/bash

# Crypto Deposit Monitor - Stop Local Services Script
# This script stops all running services

echo "🛑 Stopping Crypto Deposit Monitor Services"
echo "============================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to stop a process
stop_process() {
    local pid=$1
    local name=$2

    if [ -n "$pid" ] && kill -0 $pid 2>/dev/null; then
        echo "Stopping $name (PID: $pid)..."
        kill $pid
        sleep 2

        # Force kill if still running
        if kill -0 $pid 2>/dev/null; then
            echo "Force stopping $name..."
            kill -9 $pid 2>/dev/null || true
        fi
        echo -e "${GREEN}✅ $name stopped${NC}"
    else
        echo "⚠️  $name is not running or PID not found"
    fi
}

# Stop API server
if [ -f "logs/api.pid" ]; then
    API_PID=$(cat logs/api.pid)
    stop_process $API_PID "API Server"
    rm -f logs/api.pid
else
    # Try to find and stop uvicorn processes
    pkill -f "uvicorn app.main:app" && echo -e "${GREEN}✅ API Server stopped${NC}" || echo "⚠️  API Server PID file not found"
fi

# Stop Blockchain Monitor
if [ -f "logs/monitor.pid" ]; then
    MONITOR_PID=$(cat logs/monitor.pid)
    stop_process $MONITOR_PID "Blockchain Monitor"
    rm -f logs/monitor.pid
else
    # Try to find and stop monitor processes
    pkill -f "run_monitor.py" && echo -e "${GREEN}✅ Blockchain Monitor stopped${NC}" || echo "⚠️  Monitor PID file not found"
fi

echo ""
echo "============================================"
echo -e "${GREEN}✅ All services stopped${NC}"
echo "============================================"
