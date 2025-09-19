#!/bin/bash

# Math Insight Backend - Simple Deployment Script
# This script helps you deploy the application easily

set -e

echo "🚀 Math Insight Backend Deployment"
echo "=================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Function to start development environment
start_dev() {
    echo "🔧 Starting Development Environment..."

    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        echo "📝 Creating .env file from example..."
        cp .env.dev.example .env
        echo "✅ .env file created. You can edit it if needed."
    fi

    # Create data directory
    mkdir -p data

    # Start services
    echo "🐳 Building and starting Docker containers..."
    docker-compose up --build
}

# Function to start production environment
start_prod() {
    echo "🚀 Starting Production Environment..."

    # Check if .env.prod exists
    if [ ! -f .env.prod ]; then
        echo "📝 Creating .env.prod file from example..."
        cp .env.prod.example .env.prod
        echo "⚠️  IMPORTANT: Please edit .env.prod with your production settings!"
        echo "   - Change SECRET_KEY"
        echo "   - Set your domain in ALLOWED_HOSTS"
        echo "   - Configure email settings"
        read -p "Press Enter after editing .env.prod to continue..."
    fi

    # Create data directory
    mkdir -p data

    # Start production services
    echo "🐳 Building and starting production containers..."
    docker-compose -f docker-compose.prod.yml up --build -d

    echo "✅ Production environment started!"
    echo "🌐 Application running at: http://localhost:8000"

    # Create superuser
    read -p "Do you want to create a superuser? (y/n): " create_superuser
    if [ "$create_superuser" = "y" ]; then
        docker-compose -f docker-compose.prod.yml exec web uv run python manage.py createsuperuser
    fi
}

# Function to stop services
stop_services() {
    echo "🛑 Stopping services..."
    docker-compose down
    docker-compose -f docker-compose.prod.yml down
    echo "✅ Services stopped."
}

# Function to show logs
show_logs() {
    echo "📋 Showing logs..."
    if [ -f docker-compose.prod.yml ] && docker-compose -f docker-compose.prod.yml ps -q web &> /dev/null; then
        docker-compose -f docker-compose.prod.yml logs -f
    else
        docker-compose logs -f
    fi
}

# Function to backup database
backup_db() {
    echo "💾 Creating database backup..."
    backup_name="backup-$(date +%Y%m%d-%H%M%S).sqlite3"

    if docker-compose ps -q web &> /dev/null; then
        docker-compose exec web cp /app/data/db.sqlite3 /app/data/$backup_name
    elif docker-compose -f docker-compose.prod.yml ps -q web &> /dev/null; then
        docker-compose -f docker-compose.prod.yml exec web cp /app/data/db.sqlite3 /app/data/$backup_name
    else
        echo "❌ No running containers found."
        exit 1
    fi

    echo "✅ Database backed up as: data/$backup_name"
}

# Main menu
case "${1:-}" in
    "dev")
        start_dev
        ;;
    "prod")
        start_prod
        ;;
    "stop")
        stop_services
        ;;
    "logs")
        show_logs
        ;;
    "backup")
        backup_db
        ;;
    *)
        echo "Usage: $0 {dev|prod|stop|logs|backup}"
        echo ""
        echo "Commands:"
        echo "  dev     - Start development environment"
        echo "  prod    - Start production environment"
        echo "  stop    - Stop all services"
        echo "  logs    - Show container logs"
        echo "  backup  - Backup SQLite database"
        echo ""
        echo "Examples:"
        echo "  $0 dev    # Start development server"
        echo "  $0 prod   # Start production server"
        echo "  $0 logs   # View logs"
        exit 1
        ;;
esac
