#!/bin/bash

# JARVIS AI Assistant - Stop Script

echo "🛑 Stopping JARVIS AI Assistant..."
docker-compose down

echo ""
echo "✅ Services stopped."
echo ""
echo "To remove all data (volumes), run: docker-compose down -v"

