@echo off
REM Math Insight Backend - Windows Deployment Script

echo 🚀 Math Insight Backend Deployment
echo ==================================

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

if "%1"=="dev" goto :start_dev
if "%1"=="prod" goto :start_prod
if "%1"=="stop" goto :stop_services
if "%1"=="logs" goto :show_logs
if "%1"=="backup" goto :backup_db
goto :show_help

:start_dev
echo 🔧 Starting Development Environment...

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file from example...
    copy .env.dev.example .env
    echo ✅ .env file created. You can edit it if needed.
)

REM Create data directory
if not exist data mkdir data

REM Start services
echo 🐳 Building and starting Docker containers...
docker-compose up --build
goto :end

:start_prod
echo 🚀 Starting Production Environment...

REM Check if .env.prod exists
if not exist .env.prod (
    echo 📝 Creating .env.prod file from example...
    copy .env.prod.example .env.prod
    echo ⚠️  IMPORTANT: Please edit .env.prod with your production settings!
    echo    - Change SECRET_KEY
    echo    - Set your domain in ALLOWED_HOSTS
    echo    - Configure email settings
    pause
)

REM Create data directory
if not exist data mkdir data

REM Start production services
echo 🐳 Building and starting production containers...
docker-compose -f docker-compose.prod.yml up --build -d

echo ✅ Production environment started!
echo 🌐 Application running at: http://localhost:8000

REM Create superuser
set /p create_superuser="Do you want to create a superuser? (y/n): "
if /i "%create_superuser%"=="y" (
    docker-compose -f docker-compose.prod.yml exec web uv run python manage.py createsuperuser
)
goto :end

:stop_services
echo 🛑 Stopping services...
docker-compose down
docker-compose -f docker-compose.prod.yml down
echo ✅ Services stopped.
goto :end

:show_logs
echo 📋 Showing logs...
docker-compose -f docker-compose.prod.yml ps -q web >nul 2>&1
if not errorlevel 1 (
    docker-compose -f docker-compose.prod.yml logs -f
) else (
    docker-compose logs -f
)
goto :end

:backup_db
echo 💾 Creating database backup...
for /f "tokens=1-4 delims=/ " %%i in ('date /t') do (
    for /f "tokens=1-2 delims=: " %%m in ('time /t') do (
        set backup_name=backup-%%k%%j%%i-%%m%%n.sqlite3
    )
)

docker-compose ps -q web >nul 2>&1
if not errorlevel 1 (
    docker-compose exec web cp /app/data/db.sqlite3 /app/data/%backup_name%
) else (
    docker-compose -f docker-compose.prod.yml ps -q web >nul 2>&1
    if not errorlevel 1 (
        docker-compose -f docker-compose.prod.yml exec web cp /app/data/db.sqlite3 /app/data/%backup_name%
    ) else (
        echo ❌ No running containers found.
        goto :end
    )
)

echo ✅ Database backed up as: data/%backup_name%
goto :end

:show_help
echo Usage: %0 {dev^|prod^|stop^|logs^|backup}
echo.
echo Commands:
echo   dev     - Start development environment
echo   prod    - Start production environment
echo   stop    - Stop all services
echo   logs    - Show container logs
echo   backup  - Backup SQLite database
echo.
echo Examples:
echo   %0 dev    # Start development server
echo   %0 prod   # Start production server
echo   %0 logs   # View logs

:end
pause
