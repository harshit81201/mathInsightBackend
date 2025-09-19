# Math Insight Backend

A Django REST API backend for managing quizzes, students, and educational content using **SQLite** database and **uv** package manager.

**🌐 Frontend:** [https://math-insight.vercel.app/](https://math-insight.vercel.app/)

## 🚀 Railway Deployment (Recommended)

Deploy to Railway in minutes:

1. **Push to GitHub**
2. **Connect to [Railway.app](https://railway.app/)**
3. **Set environment variables**
4. **Deploy automatically** ✨

See **[Railway Deployment Guide](RAILWAY_DEPLOYMENT.md)** for detailed instructions.

## 🐳 Local Docker Development

```bash
# Development
docker-compose up --build

# Production testing
docker-compose -f docker-compose.prod.yml up --build -d
```

## 💻 Local Development (Without Docker)

```bash
# Install dependencies
uv sync

# Run migrations
uv run python manage.py migrate

# Create superuser
uv run python manage.py createsuperuser

# Start development server
uv run python manage.py runserver
```

## 🌐 CORS Configuration

✅ **Frontend URLs already configured:**
- `https://math-insight.vercel.app` (production)
- `http://localhost:3000` (local development)

## 📧 Email Configuration

Add to your environment variables:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=Math Insight <your-email@gmail.com>
```

## 📚 Documentation

- **[Railway Deployment](RAILWAY_DEPLOYMENT.md)** - Complete Railway deployment guide
- **[API Documentation](QUIZ_API_GUIDE.md)** - Complete API guide with examples
- **[Docker Deployment](DOCKER_DEPLOYMENT.md)** - Docker setup guide

## ✨ Features

- 🔐 JWT Authentication
- 📝 Quiz Management System
- 📊 Student Score Tracking
- 👥 Parent/Teacher Role Management
- 🗄️ SQLite Database (simple & reliable)
- 🐳 Docker Support
- 📧 Email Integration
- 🌐 CORS configured for Vercel frontend
- 🚀 Railway deployment ready

## 📱 API Endpoints

- `POST /api/quizzes/` - Create quiz
- `GET /api/scores/teacher/{id}/students/` - Get student scores summary
- `GET /api/scores/teacher/{id}/student/{id}/` - Get detailed student scores
- And many more... (see [API Guide](QUIZ_API_GUIDE.md))

## 🛠️ Tech Stack

- **Backend:** Django REST Framework
- **Database:** SQLite (file-based, zero setup)
- **Package Manager:** uv (fast Python package manager)
- **Authentication:** JWT tokens
- **Deployment:** Railway (recommended) or Docker
- **Production Server:** Gunicorn
- **Frontend Integration:** CORS configured for Vercel
