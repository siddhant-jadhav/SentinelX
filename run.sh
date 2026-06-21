#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# SentinelX — Launch Script
# Starts both FastAPI backend and Streamlit frontend
# ═══════════════════════════════════════════════════════════════

set -e

echo "🛡️  SentinelX — Cyber Threat Intelligence Platform"
echo "═══════════════════════════════════════════════════════"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found."
    exit 1
fi

echo "📦 Python: $(python3 --version)"

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📦 Activating virtual environment..."
source venv/bin/activate

echo "📦 Installing dependencies..."
pip install -r requirements.txt --quiet

# Copy .env if doesn't exist
if [ ! -f ".env" ]; then
    echo "📄 Creating .env from template..."
    cp .env.example .env
fi

# Seed database
echo "🗄️  Seeding database..."
python3 -c "from backend.seed import seed_database; seed_database()"

# Start backend
echo "🚀 Starting FastAPI backend on http://localhost:8003..."
uvicorn backend.main:app --host 0.0.0.0 --port 8003 --reload &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
echo "🎨 Starting Streamlit frontend on http://localhost:8503..."
streamlit run frontend/app.py --server.port 8503 --server.headless true &
FRONTEND_PID=$!

echo ""
echo "═══════════════════════════════════════════════════════"
echo "✅ SentinelX is running!"
echo ""
echo "   🌐 Frontend:  http://localhost:8503"
echo "   🔧 Backend:   http://localhost:8003"
echo "   📚 API Docs:  http://localhost:8003/docs"
echo ""
echo "   👤 Admin:     admin / SentinelX@2024"
echo "   👤 Analyst:   analyst / analyst123"
echo ""
echo "   Press Ctrl+C to stop all services"
echo "═══════════════════════════════════════════════════════"

# Trap Ctrl+C to stop both processes
cleanup() {
    echo ""
    echo "🛑 Stopping SentinelX..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    wait $BACKEND_PID 2>/dev/null
    wait $FRONTEND_PID 2>/dev/null
    echo "👋 Goodbye!"
}

trap cleanup EXIT INT TERM

# Wait for either process to exit
wait
