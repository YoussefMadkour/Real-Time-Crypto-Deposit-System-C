#!/bin/bash

# Crypto Deposit Monitor - Local Development Startup Script
# This script starts all services needed for local development

set -e

echo "🚀 Starting Crypto Deposit Monitor - Local Development"
echo "=================================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating one...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Dependencies not installed. Installing...${NC}"
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${GREEN}✅ Dependencies already installed${NC}"
fi

# Check if PostgreSQL is running
echo "🔍 Checking PostgreSQL..."
if docker ps | grep -q postgres; then
    echo -e "${GREEN}✅ PostgreSQL is running${NC}"
else
    echo -e "${RED}❌ PostgreSQL is not running${NC}"
    echo "Starting PostgreSQL with Docker..."
    docker run --name postgres-crypto \
        -e POSTGRES_DB=crypto_deposits \
        -e POSTGRES_USER=postgres \
        -e POSTGRES_PASSWORD=password \
        -p 5432:5432 \
        -d postgres:17
    echo "Waiting for PostgreSQL to be ready..."
    sleep 5
    echo -e "${GREEN}✅ PostgreSQL started${NC}"
fi

# Run database migrations
echo "🗄️  Running database migrations..."
alembic upgrade head
echo -e "${GREEN}✅ Database is up to date${NC}"

# Check for .env file
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo "Please create a .env file with your configuration."
    echo "You can copy .env.example and fill in your values:"
    echo "  cp .env.example .env"
    exit 1
fi

echo ""
echo "=================================================="
echo -e "${GREEN}✅ All checks passed!${NC}"
echo "=================================================="
echo ""
echo "Starting services..."
echo ""

# Create a logs directory
mkdir -p logs

# Start FastAPI server
echo "🌐 Starting FastAPI server on http://localhost:8000"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > logs/api.log 2>&1 &
API_PID=$!
echo "   API PID: $API_PID"

# Wait for API to be ready
sleep 3
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✅ API server is running${NC}"
else
    echo -e "${RED}❌ Failed to start API server${NC}"
    kill $API_PID 2>/dev/null || true
    exit 1
fi

# Start Blockchain Monitor
echo "⛓️  Starting Blockchain Monitor"
python run_monitor.py > logs/monitor.log 2>&1 &
MONITOR_PID=$!
echo "   Monitor PID: $MONITOR_PID"

# Save PIDs for cleanup
echo $API_PID > logs/api.pid
echo $MONITOR_PID > logs/monitor.pid

echo ""
echo "=================================================="
echo -e "${GREEN}🎉 All services started successfully!${NC}"
echo "=================================================="
echo ""
echo "📝 Access points:"
echo "   🌐 Web UI:        http://localhost:8000"
echo "   📚 API Docs:      http://localhost:8000/docs"
echo "   🔌 WebSocket:     ws://localhost:8000/ws"
echo ""
echo "📋 Log files:"
echo "   API:              logs/api.log"
echo "   Monitor:          logs/monitor.log"
echo ""
echo "🛑 To stop all services, run:"
echo "   ./stop_local.sh"
echo ""
echo "   Or manually kill processes:"
echo "   kill $API_PID $MONITOR_PID"
echo ""
echo "💡 Tip: Open http://localhost:8000 in your browser to use the Web UI!"
echo ""

# Keep script running and show logs
echo "📊 Showing live API logs (Ctrl+C to stop following, services will keep running):"
echo "=================================================="
sleep 2
tail -f logs/api.log
