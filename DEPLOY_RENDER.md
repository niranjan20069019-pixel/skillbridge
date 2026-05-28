# Deployment Guide for Render

## Overview

This guide will help you deploy the SkillBridge application to [Render.com](https://render.com).

The application consists of:
- **Python Flask API** (Main backend)
- **Node.js Express API** (AI services)
- **PostgreSQL Database**
- **React Frontend** (Built and served by Flask)

---

## Prerequisites

1. **GitHub Account** - Your code is already pushed to `niranjan20069019-pixel/skillbridge`
2. **Render Account** - Sign up at [render.com](https://render.com)
3. **API Keys** (optional but recommended):
   - Gemini API Key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - OpenAI API Key from [OpenAI Platform](https://platform.openai.com/api-keys)
   - YouTube API Key (if needed)

---

## Step-by-Step Deployment

### 1. Connect Render to GitHub

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Select **"Deploy an existing repository"**
4. Search for `skillbridge` and select `niranjan20069019-pixel/skillbridge`
5. Click **"Connect"**

### 2. Create the Main Flask API Service

**Service Details:**
- **Name:** `skillbridge-api`
- **Root Directory:** `/` (or leave empty)
- **Environment:** `Python 3`
- **Build Command:**
  ```bash
  pip install -r requirements.txt && flask db upgrade
  ```
- **Start Command:**
  ```bash
  gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT run:app
  ```
- **Instance Type:** Free (or Starter for production)

**Environment Variables:**
```
FLASK_ENV=production
SECRET_KEY=<generate-a-strong-secret-key>
DATABASE_URL=<will-be-set-by-Render-PostgreSQL>
GEMINI_API_KEY=<your-gemini-key>
OPENAI_API_KEY=<your-openai-key>
YOUTUBE_API_KEY=<your-youtube-key>
PYTHON_VERSION=3.12
```

Click **"Create Web Service"**

### 3. Create the PostgreSQL Database

1. In Render Dashboard, click **"New +"** → **"PostgreSQL"**
2. **Name:** `skillbridge-db`
3. **Region:** Select closest to you
4. **Version:** PostgreSQL 15
5. **Instance Type:** Free
6. Click **"Create Database"**

### 4. Connect Database to Flask Service

1. Copy the database connection string from PostgreSQL service
2. Go back to Flask service settings
3. Add environment variable:
   - **Key:** `DATABASE_URL`
   - **Value:** Paste the connection string
4. Deploy the service

### 5. Create the Node.js API Service (Optional)

1. Click **"New +"** → **"Web Service"**
2. Select `skillbridge` repository again
3. **Service Details:**
   - **Name:** `skillbridge-node-api`
   - **Root Directory:** `/backend`
   - **Environment:** `Node`
   - **Build Command:**
     ```bash
     npm install
     ```
   - **Start Command:**
     ```bash
     npm start
     ```
   - **Instance Type:** Free

4. **Environment Variables:**
   ```
   NODE_ENV=production
   PORT=10000
   GEMINI_API_KEY=<your-gemini-key>
   OPENAI_API_KEY=<your-openai-key>
   ```

5. Click **"Create Web Service"**

### 6. Update Flask Service to Use Node API

If you deploy the Node.js service, update the Flask environment:

1. Go to Flask service → **"Environment"**
2. Add:
   - **Key:** `NODE_API_URL`
   - **Value:** `https://skillbridge-node-api.onrender.com`
3. Redeploy

---

## Alternative: Use render.yaml (Recommended)

Instead of manually creating services, you can use the included `render.yaml`:

1. In Render Dashboard, click **"New +"** → **"Blueprint"**
2. Select your GitHub repository
3. Render will automatically read `render.yaml` and create all services
4. Fill in the required environment variables
5. Click **"Create"**

---

## Important Configuration Notes

### Database Initialization

The Flask app includes migration support. Migrations run automatically via:
```bash
flask db upgrade
```

### Environment Variables to Set

In Render Dashboard, add these to the Flask service:

| Key | Value | Required |
|-----|-------|----------|
| `FLASK_ENV` | `production` | ✓ |
| `SECRET_KEY` | Generate strong key | ✓ |
| `DATABASE_URL` | PostgreSQL connection | ✓ |
| `GEMINI_API_KEY` | Your API key | Optional |
| `OPENAI_API_KEY` | Your API key | Optional |
| `YOUTUBE_API_KEY` | Your API key | Optional |

### Generate Secret Key

Run this locally and copy the output:
```python
python -c "import secrets; print(secrets.token_hex(32))"
```

### Frontend

The React frontend is built and served by the Flask backend:
1. Flask will serve the frontend from `public/` directory
2. No separate web service needed for frontend
3. Build happens automatically in Flask's build command

---

## Post-Deployment Checklist

- [ ] Database created and connected
- [ ] Flask service deployed successfully
- [ ] Node.js service deployed (optional)
- [ ] Environment variables set
- [ ] Test API endpoints:
  - `https://skillbridge-api.onrender.com/` (should show login page)
  - `https://skillbridge-api.onrender.com/api/` (API endpoints)
- [ ] Check logs for errors: Dashboard → Service → "Logs"

---

## Troubleshooting

### Build Failures

Check the build logs in Render Dashboard:
1. Go to Service → **"Logs"**
2. Look for error messages
3. Common issues:
   - Missing dependencies in `requirements.txt`
   - Incompatible Python version
   - Database connection string format

### Database Issues

- Ensure `flask db upgrade` runs successfully
- Check `DATABASE_URL` format matches PostgreSQL connection string
- Verify database created in Render

### Port Issues

- Flask automatically uses `$PORT` environment variable
- Node.js should also use `$PORT` or specify a custom port

### CORS Errors

Update Flask app to accept Render domain:
1. Add to environment variables:
   ```
   ALLOWED_HOSTS=your-flask-service.onrender.com,your-node-service.onrender.com
   ```

---

## Monitoring & Logs

### View Logs

1. Go to Service in Render Dashboard
2. Click **"Logs"** tab
3. Follow real-time logs

### Performance Monitoring

- Check service metrics in Render Dashboard
- Monitor response times
- Check database connection pool usage

---

## Scaling Notes

### Free Tier Limitations
- Services spin down after 15 minutes of inactivity
- 0.5 GB RAM per service
- Limited to 100 concurrent connections per database

### Upgrade for Production
- Switch from Free to Starter/Standard plan
- Enables auto-scaling
- 24/7 availability
- Better performance

---

## Next Steps

1. Deploy on Render using the steps above
2. Test all features
3. Set up custom domain (optional)
4. Configure monitoring alerts (optional)
5. Set up automated backups for database

For more info, visit [Render Docs](https://render.com/docs)
