# Railway Deployment Guide

This guide explains how to deploy the Math Insight Backend to Railway.

## 🚀 Quick Railway Deployment

### Step 1: Prepare Your Repository

1. **Ensure your code is pushed to GitHub**
2. **Your repository should have these files:**
   - `Dockerfile` (Railway-optimized)
   - `pyproject.toml` with dependencies
   - `uv.lock` file

### Step 2: Deploy to Railway

1. **Go to [Railway.app](https://railway.app/)**
2. **Click "Start a New Project"**
3. **Select "Deploy from GitHub repo"**
4. **Choose your `mathInsightBackend` repository**

### Step 3: Configure Environment Variables

In Railway dashboard, go to **Variables** tab and add:

```
SECRET_KEY=your-super-secret-production-key-here
DEBUG=False
ALLOWED_HOSTS=*.railway.app,math-insight.vercel.app
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=Math Insight <your-email@gmail.com>
```

### Step 4: Deploy

Railway will automatically:
1. ✅ Build your Docker container
2. ✅ Run database migrations
3. ✅ Start your application with Gunicorn
4. ✅ Provide you with a public URL

## 🌐 Frontend Integration

Your frontend at `https://math-insight.vercel.app/` is already configured to work with the Railway deployment.

**CORS Settings:** ✅ Already configured in `settings.py`:
- `https://math-insight.vercel.app` (production)
- `http://localhost:3000` (local frontend development)

## 📧 Email Configuration

### Gmail Setup (Recommended):

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate an App Password:**
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. **Use in Railway environment variables:**
   ```
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-16-character-app-password
   ```

### Other Email Providers:

**Outlook/Hotmail:**
```
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

**Yahoo:**
```
EMAIL_HOST=smtp.mail.yahoo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

## 🗄️ Database

**SQLite Configuration:**
- ✅ No additional setup required
- ✅ Database persists across deployments
- ✅ Stored in `/app/data/db.sqlite3`
- ✅ Automatic backups by Railway

## 🔧 Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `your-secret-key-here` |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Allowed host domains | `*.railway.app,yourdomain.com` |
| `EMAIL_HOST` | SMTP server | `smtp.gmail.com` |
| `EMAIL_PORT` | SMTP port | `587` |
| `EMAIL_USE_TLS` | Use TLS encryption | `True` |
| `EMAIL_HOST_USER` | Email username | `your-email@gmail.com` |
| `EMAIL_HOST_PASSWORD` | Email password/app password | `your-app-password` |
| `DEFAULT_FROM_EMAIL` | Default sender email | `Math Insight <email@gmail.com>` |

## 🚀 Deployment Commands

Railway automatically runs these commands during deployment:

```bash
# Install dependencies
uv sync --frozen

# Collect static files
uv run python manage.py collectstatic --noinput

# Run migrations
uv run python manage.py migrate

# Start with Gunicorn
uv run gunicorn mathInsight.wsgi:application --bind 0.0.0.0:$PORT
```

## 🔍 Monitoring & Logs

1. **View Logs:** Railway dashboard → Deployments → View logs
2. **Monitor Performance:** Railway dashboard → Metrics
3. **Check Health:** Your app URL `/admin/` should load

## 🛠️ Troubleshooting

### Common Issues:

1. **"DisallowedHost" Error:**
   ```
   ALLOWED_HOSTS=*.railway.app,your-custom-domain.com
   ```

2. **CORS Error from Frontend:**
   - Verify frontend URL in CORS settings
   - Check environment variables are set

3. **Email Not Working:**
   - Use App Password for Gmail (not regular password)
   - Check EMAIL_USE_TLS=True for most providers

4. **Static Files Not Loading:**
   - Railway automatically handles static files
   - Check `collectstatic` ran during build

### Debug Mode:

**Temporarily enable debug mode:**
```
DEBUG=True
```
**⚠️ Remember to set back to `False` for production!**

## 🔄 Redeployment

To redeploy after code changes:

1. **Push to GitHub**
2. **Railway auto-deploys** from your main branch
3. **Or manually trigger** in Railway dashboard

## 📈 Scaling

Railway can automatically scale your application:
- **Horizontal scaling:** Multiple instances
- **Vertical scaling:** More CPU/RAM
- **Auto-scaling:** Based on load

## 💾 Database Backups

Railway automatically backs up your data, but for manual backups:

1. **Connect to Railway shell:**
   ```bash
   railway shell
   ```

2. **Create backup:**
   ```bash
   cp /app/data/db.sqlite3 /app/data/backup-$(date +%Y%m%d).sqlite3
   ```

## 🌟 Production Checklist

- ✅ `DEBUG=False`
- ✅ Strong `SECRET_KEY`
- ✅ Proper `ALLOWED_HOSTS`
- ✅ Email configuration tested
- ✅ Frontend CORS working
- ✅ Admin user created
- ✅ API endpoints tested

Your Math Insight Backend is now production-ready on Railway! 🚀
