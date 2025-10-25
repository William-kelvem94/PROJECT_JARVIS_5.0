#!/bin/bash

# JARVIS AI Assistant - Start Script

set -e

echo "🤖 Starting JARVIS AI Assistant..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "✅ Please edit .env file with your configuration before continuing."
    echo "   Run this script again after configuring."
    exit 0
fi

echo "📦 Building and starting services..."
docker-compose up -d --build

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

# Wait for backend
echo "🔍 Checking backend health..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is ready!"
        break
    fi
    attempt=$((attempt+1))
    echo "   Attempt $attempt/$max_attempts..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Backend failed to start. Check logs with: docker-compose logs backend"
    exit 1
fi

# Run database migrations
echo ""
echo "🗄️  Running database migrations..."
docker exec jarvis_backend alembic upgrade head

echo ""
echo "✅ JARVIS AI Assistant is now running!"
echo ""
echo "📍 Access points:"
echo "   Frontend:  http://localhost"
echo "   API Docs:  http://localhost:8000/api/docs"
echo "   Health:    http://localhost:8000/health"
echo ""
echo "📝 Useful commands:"
echo "   View logs:     docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart:       docker-compose restart"
echo ""
echo "🎉 Happy coding!"

