#!/bin/bash

echo "🚀 Starting DevCareerCompass with Astro CLI"
echo "==========================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from env.example..."
    if [ -f env.example ]; then
        cp env.example .env
        echo "✅ Created .env file from env.example"
    else
        echo "❌ env.example not found. Please create a .env file with your API keys."
        exit 1
    fi
fi

# Check if Astro CLI is installed
if ! command -v astro &> /dev/null; then
    echo "❌ Astro CLI is not installed. Please install it first:"
    echo "   brew install astro"
    exit 1
fi

# Stop any existing Astro projects
echo "🛑 Stopping any existing Astro projects..."
astro dev kill 2>/dev/null || true

# Start Astro development environment
echo "🐳 Starting Astro development environment..."
astro dev start

# Check if Airflow is running
if curl -s http://localhost:8080 > /dev/null; then
    echo ""
    echo "✅ Astro is running successfully!"
    echo "🌐 Access Airflow UI at: http://localhost:8080"
    echo "📊 DAG: devcareer_compass_data_collection"
    echo "🕐 Schedule: Daily at 2:00 AM"
    echo ""
    echo "🔧 To stop Astro: astro dev stop"
    echo "📋 To view logs: astro dev logs"
    echo "🔄 To restart: astro dev restart"
else
    echo "❌ Astro failed to start. Check logs with:"
    echo "   astro dev logs"
fi 