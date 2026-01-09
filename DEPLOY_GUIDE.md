# 🚀 Render Deployment Guide

## Quick Deploy (Automatic with render.yaml)

The repository includes a `render.yaml` configuration file for automatic deployment.

### Steps:

1. **Go to Render Dashboard**: https://dashboard.render.com/
2. **Click "New +"** → **"Blueprint"**
3. **Connect your GitHub repository**: `Abhich05/Wiki-Quiz-Genrator`
4. **Render will automatically**:
   - Create a PostgreSQL database
   - Deploy the web service
   - Configure environment variables
5. **Add your API key**:
   - Go to your web service in Render dashboard
   - Click "Environment" in the left sidebar
   - Add `GOOGLE_API_KEY` with your Gemini API key
   - Save changes
6. **Done!** Your API will be live at: `https://your-app-name.onrender.com`

---

## Manual Deploy (Alternative)

If you prefer manual setup:

### 1. Create PostgreSQL Database

1. In Render dashboard, click **"New +"** → **"PostgreSQL"**
2. Set:
   - **Name**: `wiki-quiz-db`
   - **Database**: `wiki_quiz`
   - **User**: `wiki_quiz_user`
   - **Plan**: Free
3. Click **"Create Database"**
4. Copy the **Internal Database URL** (you'll need this)

### 2. Deploy Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `wiki-quiz-generator`
   - **Runtime**: `Python 3`
   - **Branch**: `main`
   - **Root Directory**: Leave empty
   - **Build Command**: 
     ```bash
     cd backend && pip install -r requirements.txt
     ```
   - **Start Command**: 
     ```bash
     cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
     ```
   - **Plan**: Free

4. **Environment Variables**:
   - Click **"Advanced"** → **"Add Environment Variable"**
   - Add:
     ```
     GOOGLE_API_KEY=your-gemini-api-key-here
     DATABASE_URL=<paste-internal-database-url>
     ```

5. Click **"Create Web Service"**

### 3. Wait for Deployment

- Initial deployment takes 5-10 minutes
- Render will install dependencies and start your app
- Once complete, you'll see "Your service is live 🎉"

---

## Getting Your API Key

Get a **FREE** Google Gemini API key:
1. Go to: https://makersuite.google.com/app/apikey
2. Click **"Create API Key"**
3. Copy the key
4. Add it to your Render environment variables

---

## Verify Deployment

Once deployed, test your API:

### Health Check
```bash
curl https://your-app-name.onrender.com/health
```

**Expected response**:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "checks": {
    "api": true,
    "database": true,
    "ai_configured": true
  }
}
```

### API Documentation
Visit: `https://your-app-name.onrender.com/docs`

---

## Update Frontend

After deployment, update your frontend to use the new API URL:

1. Open `frontend/app.js`
2. Update line 2:
   ```javascript
   const API_BASE_URL = 'https://your-app-name.onrender.com';
   ```
3. Commit and push changes

---

## Troubleshooting

### Module Not Found Error
- **Cause**: Missing dependencies
- **Fix**: Ensure `build.sh` runs or build command is correct
- **Verify**: Check build logs in Render dashboard

### Database Connection Error
- **Cause**: DATABASE_URL not set correctly
- **Fix**: Copy the **Internal Database URL** from your PostgreSQL service
- **Format**: `postgresql://user:password@host:5432/dbname`

### API Key Not Working
- **Cause**: GOOGLE_API_KEY not set or incorrect
- **Fix**: Get new key from https://makersuite.google.com/app/apikey
- **Note**: Free tier has rate limits (60 requests/minute)

### Service Won't Start
- **Check build logs**: Click "Logs" in Render dashboard
- **Common issues**:
  - Wrong build/start commands
  - Missing environment variables
  - Python version incompatibility (should be 3.11+)

---

## Free Tier Limits

Render Free Tier includes:
- ✅ 750 hours/month of runtime
- ✅ PostgreSQL database with 1GB storage
- ✅ Automatic HTTPS
- ⚠️ Spins down after 15 minutes of inactivity
- ⚠️ Takes ~30 seconds to wake up on first request

**Tip**: Keep your service warm by pinging it every 10-15 minutes with a monitoring service.

---

## Production Recommendations

For production use:
1. Upgrade to **Starter Plan** ($7/month) for:
   - No spin-down
   - Faster builds
   - More resources
2. Add custom domain
3. Set up monitoring
4. Configure proper logging
5. Enable auto-scaling

---

## Support

- **Render Docs**: https://render.com/docs
- **GitHub Issues**: https://github.com/Abhich05/Wiki-Quiz-Genrator/issues
- **API Documentation**: Check `/docs` endpoint on your deployed service

---

**Last Updated**: January 2026
