# Docker Deployment Guide

This guide explains how to deploy the Math Insight Backend using Docker and docker-compose.

## Prerequisites

- Docker installed on your system
- Docker Compose installed
- Git (to clone the repository)

## Project Structure

```
mathInsightBackend/
├── Dockerfile              # Development Docker image
├── Dockerfile.prod        # Production Docker image
├── docker-compose.yml     # Development compose file
├── docker-compose.prod.yml # Production compose file
├── .dockerignore          # Files to ignore in Docker context
├── .env.prod.example      # Example production environment file
├── nginx.conf             # Nginx configuration for production
└── pyproject.toml         # UV dependencies
```

## Quick Start (Development)

1. **Clone and navigate to the project:**
   ```bash
   git clone <your-repo-url>
   cd mathInsightBackend
   ```

2. **Build and run with docker-compose:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - API: http://localhost:8000
   - Admin: http://localhost:8000/admin/

4. **Create a superuser (in another terminal):**
   ```bash
   docker-compose exec web uv run python manage.py createsuperuser
   ```

## Production Deployment

### Step 1: Prepare Environment

1. **Copy the production environment template:**
   ```bash
   cp .env.prod.example .env.prod
   ```

2. **Edit `.env.prod` with your production values:**
   ```bash
   nano .env.prod
   ```

   **Important:** Change these values:
   - `SECRET_KEY`: Generate a new secret key
   - `ALLOWED_HOSTS`: Add your domain name
   - `DEBUG`: Set to `False`

### Step 2: Deploy with Docker Compose

1. **Build and run production services:**
   ```bash
   docker-compose -f docker-compose.prod.yml up --build -d
   ```

2. **Create superuser:**
   ```bash
   docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
   ```

3. **Access your application:**
   - Application: http://your-domain (via Nginx)
   - Direct API: http://your-domain:8000

### Step 3: SSL/HTTPS (Recommended)

For production, set up SSL using Let's Encrypt:

1. **Install Certbot:**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   ```

2. **Get SSL certificate:**
   ```bash
   sudo certbot --nginx -d yourdomain.com
   ```

## Alternative: Single Container Deployment

If you prefer to use just Docker without compose:

### Development:
```bash
# Build the image
docker build -t mathinsight-backend .

# Run the container
docker run -p 8000:8000 -v $(pwd)/data:/app/data mathinsight-backend
```

### Production:
```bash
# Build production image
docker build -f Dockerfile.prod -t mathinsight-backend-prod .

# Run with environment file
docker run -p 8000:8000 \
  --env-file .env.prod \
  -v $(pwd)/data:/app/data \
  mathinsight-backend-prod
```

## Database Options

### Option 1: SQLite (Default)
- **Pros:** Simple, no additional setup
- **Cons:** Not suitable for high-traffic production
- **Persistence:** Database stored in `./data/` directory

### Option 2: PostgreSQL (Recommended for Production)

1. **Uncomment PostgreSQL section in `docker-compose.prod.yml`**

2. **Update your `.env.prod`:**
   ```
   DATABASE_URL=postgres://mathinsight:password123@db:5432/mathinsight
   ```

3. **Add PostgreSQL dependency:**
   ```bash
   uv add psycopg2-binary
   ```

4. **Update settings.py to use DATABASE_URL:**
   ```python
   import dj_database_url

   DATABASES = {
       'default': dj_database_url.parse(env('DATABASE_URL', default='sqlite:///db.sqlite3'))
   }
   ```

## Useful Commands

### Development Commands:
```bash
# View logs
docker-compose logs -f

# Access container shell
docker-compose exec web bash

# Run Django commands
docker-compose exec web uv run python manage.py migrate
docker-compose exec web uv run python manage.py collectstatic

# Stop services
docker-compose down

# Remove volumes (careful: deletes data!)
docker-compose down -v
```

### Production Commands:
```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Access container shell
docker-compose -f docker-compose.prod.yml exec web bash

# Update application (zero-downtime)
docker-compose -f docker-compose.prod.yml build web
docker-compose -f docker-compose.prod.yml up -d --no-deps web

# Backup database (SQLite)
docker-compose -f docker-compose.prod.yml exec web cp /app/data/db.sqlite3 /app/backup-$(date +%Y%m%d).sqlite3
```

## Environment Variables

### Development (.env):
```
DEBUG=True
SECRET_KEY=your-development-key
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
```

### Production (.env.prod):
```
DEBUG=False
SECRET_KEY=your-super-secret-production-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgres://user:pass@db:5432/dbname  # Optional
```

## Security Considerations

1. **Change default SECRET_KEY** in production
2. **Set DEBUG=False** in production
3. **Use HTTPS** with proper SSL certificates
4. **Restrict ALLOWED_HOSTS** to your domain only
5. **Use strong database passwords**
6. **Regularly update Docker images**
7. **Monitor logs** for suspicious activity

## Monitoring and Maintenance

### Health Checks:
The containers include health checks that monitor:
- HTTP response from the application
- Container restart on failure

### Log Monitoring:
```bash
# Follow all logs
docker-compose -f docker-compose.prod.yml logs -f

# Follow specific service logs
docker-compose -f docker-compose.prod.yml logs -f web
docker-compose -f docker-compose.prod.yml logs -f nginx
```

### Backup Strategy:
1. **Database backups** (automated via cron)
2. **Media files backup**
3. **Environment files backup**
4. **Regular image updates**

## Troubleshooting

### Common Issues:

1. **Port already in use:**
   ```bash
   # Change port in docker-compose.yml
   ports:
     - "8001:8000"  # Use port 8001 instead
   ```

2. **Permission issues:**
   ```bash
   # Fix file permissions
   sudo chown -R $(whoami):$(whoami) ./data
   ```

3. **Database migrations:**
   ```bash
   # Run migrations manually
   docker-compose exec web uv run python manage.py migrate
   ```

4. **Static files not serving:**
   ```bash
   # Collect static files
   docker-compose exec web uv run python manage.py collectstatic --noinput
   ```

## Performance Optimization

1. **Use multi-stage builds** (already implemented in Dockerfile.prod)
2. **Enable Nginx caching** for static files
3. **Use Redis for caching** (optional)
4. **Configure proper worker processes** in gunicorn
5. **Monitor resource usage** with Docker stats

```bash
# Monitor resource usage
docker stats

# Scale services if needed
docker-compose -f docker-compose.prod.yml up -d --scale web=3
```

This Docker setup provides a robust, scalable deployment solution for your Math Insight Backend using uv package management and Django best practices.
