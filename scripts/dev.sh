#!/bin/bash

# JARVIS AI Assistant - Development Mode Script

echo "🔧 Starting JARVIS in Development Mode..."
echo ""

# Start services without Ollama (to save resources during dev)
docker-compose up -d postgres redis

echo "⏳ Waiting for database..."
sleep 3

echo ""
echo "✅ Development services started!"
echo ""
echo "📝 Next steps:"
echo "   1. Backend:  cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "   2. Frontend: cd frontend && npm run dev"
echo ""
echo "💡 Tip: Use separate terminals for backend and frontend"

