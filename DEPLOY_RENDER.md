# 🚀 Deploy to Render - Complete Guide

## 🎯 Overview

Deploy your Wiki Quiz Generator to Render.com with both frontend and backend in minutes!

**What you'll get:**
- 🔹 **Backend API**: `https://wiki-quiz-api.onrender.com`
- 🔹 **Frontend**: `https://wiki-quiz.onrender.com`
- 🔒 Free HTTPS
- 🌐 Global CDN
- 💰 Free tier available

---

## 📋 Prerequisites

1. **GitHub Account** - Your code is already pushed! ✅
2. **Render Account** - Sign up at https://render.com (free)
3. **Google API Key** - Get from https://ai.google.dev/

---

## 🎯 Method 1: Deploy Both Services (Recommended)

### Step 1: Sign Up for Render

1. Go to https://render.com
2. Click "Get Started"
3. Sign up with GitHub (recommended)
4. Authorize Render to access your repositories

---

### Step 2: Deploy Backend (Web Service)

#### A. Create New Web Service

1. Click "New +" → "Web Service"
2. Connect your repository: `Abhich05/Wiki-Quiz-Genrator`
3. Click "Connect"

#### B. Configure Backend Service

Fill in the following:

**Basic Settings:**
- **Name**: `wiki-quiz-api` (or your choice)
- **Region**: `Oregon (US West)` (or closest to you)
- **Branch**: `main`
- **Root Directory**: `backend`
- **Runtime**: `Python 3`

**Build & Deploy:**
- **Build Command**: `pip install -r requirements_prod.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

**Instance Type:**
- **Free** (for testing)
- Or **Starter** ($7/month) for production

#### C. Add Environment Variables

Click "Advanced" → "Add Environment Variable":

| Key | Value |
|-----|-------|
| `GOOGLE_API_KEY` | `your-google-api-key-here` |
| `PORT` | `10000` (Render default) |

#### D. Deploy!

1. Click "Create Web Service"
2. Wait 2-3 minutes for build
3. Your backend will be live at: `https://wiki-quiz-api.onrender.com`

---

### Step 3: Deploy Frontend (Static Site)

#### A. Create New Static Site

1. Click "New +" → "Static Site"
2. Select your repository: `Abhich05/Wiki-Quiz-Genrator`
3. Click "Connect"

#### B. Configure Frontend Service

**Basic Settings:**
- **Name**: `wiki-quiz` (or your choice)
- **Branch**: `main`
- **Root Directory**: `frontend`

**Build Settings:**
- **Build Command**: (leave empty or use `echo "No build needed"`)
- **Publish Directory**: `.` (current directory)

#### C. Deploy!

1. Click "Create Static Site"
2. Your frontend will be live at: `https://wiki-quiz.onrender.com`

---

### Step 4: Update Frontend to Use Backend URL

After backend is deployed, you need to update the frontend:

#### A. Get Backend URL

Copy your backend URL: `https://wiki-quiz-api.onrender.com`

#### B. Update Frontend

Edit `frontend/app.html` and update the API URL:

```javascript
// Find this line (around line 20-30)
const API_URL = 'http://localhost:8000';

// Change to your Render backend URL
const API_URL = 'https://wiki-quiz-api.onrender.com';
```

#### C. Push Changes

```bash
cd "C:\Projects\Wiki Quiz Generator"
git add frontend/app.html
git commit -m "Update API URL for Render deployment"
git push origin main
```

Render will automatically redeploy your frontend! 🎉

---

## 🎯 Method 2: Deploy with render.yaml (Blueprint)

For easier deployment, use Render's Blueprint feature:

### Step 1: Create render.yaml

I'll create this file for you:

```yaml
# render.yaml - Render Blueprint
services:
  # Backend API
  - type: web
    name: wiki-quiz-api
    runtime: python
    region: oregon
    plan: free
    branch: main
    rootDir: backend
    buildCommand: pip install -r requirements_prod.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: GOOGLE_API_KEY
        sync: false  # Set manually in dashboard
      - key: PORT
        value: 10000
    healthCheckPath: /

  # Frontend Static Site
  - type: web
    name: wiki-quiz-frontend
    runtime: static
    region: oregon
    plan: free
    branch: main
    rootDir: frontend
    buildCommand: echo "No build needed"
    staticPublishPath: .
    routes:
      - type: rewrite
        source: /*
        destination: /app.html
```

### Step 2: Deploy with Blueprint

1. Go to Render Dashboard
2. Click "New +" → "Blueprint"
3. Select repository: `Abhich05/Wiki-Quiz-Genrator`
4. Render will detect `render.yaml`
5. Click "Apply"
6. Set `GOOGLE_API_KEY` in environment variables
7. Both services deploy automatically!

---

## 🔧 Configuration Details

### Backend Configuration

**Dockerfile Alternative** (if you want to use Docker):

Render can also deploy from your Dockerfile:

1. When creating Web Service, choose "Docker"
2. **Dockerfile Path**: `backend/Dockerfile`
3. Render will build and deploy your Docker image

### Frontend Configuration

**Custom Domain** (optional):

1. Go to Static Site settings
2. Click "Custom Domains"
3. Add your domain: `quiz.yourdomain.com`
4. Update DNS records as shown

---

## 🌐 Update CORS for Render

Your backend already has CORS enabled, but verify in `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

For production, change to:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://wiki-quiz.onrender.com",  # Your frontend URL
        "http://localhost:3000",  # For local testing
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 Monitor Your Deployment

### Backend Monitoring

**View Logs:**
1. Go to your web service dashboard
2. Click "Logs" tab
3. See real-time application logs

**Check Health:**
```bash
curl https://wiki-quiz-api.onrender.com/
```

**Test API:**
```bash
curl https://wiki-quiz-api.onrender.com/docs
```

### Frontend Monitoring

**View Deployment:**
1. Go to static site dashboard
2. Click "Events" to see deployment history

---

## 💰 Pricing

### Free Tier (Perfect for Testing)

**Web Service (Backend):**
- ✅ 750 hours/month free
- ✅ Spins down after 15 min of inactivity
- ✅ 512 MB RAM
- ⚠️ Cold start delay (~30 seconds)

**Static Site (Frontend):**
- ✅ Completely FREE
- ✅ Global CDN
- ✅ No sleep/spin down
- ✅ Unlimited bandwidth

### Paid Tier ($7/month)

**Starter Plan Benefits:**
- 🚀 Always on (no cold starts)
- 💾 More RAM (512 MB+)
- ⚡ Faster builds
- 📊 Better monitoring

---

## 🐛 Troubleshooting

### Backend Issues

**1. Service Won't Start**

Check logs for errors:
```
Build failed: No module named 'fastapi'
```
**Fix**: Verify `requirements_prod.txt` includes all dependencies

**2. Cold Starts (Free Tier)**

Free services spin down after 15 minutes of inactivity.

**Solutions:**
- Upgrade to paid plan ($7/month)
- Use a ping service (https://uptimerobot.com) to keep it alive
- Accept 30-second cold start delay

**3. Environment Variable Not Set**

```
Error: GOOGLE_API_KEY not found
```
**Fix**: Add in Render dashboard → Service → Environment

### Frontend Issues

**1. Can't Connect to Backend**

**Check:**
- Backend URL is correct in `app.html`
- Backend is running (check Render dashboard)
- CORS is enabled

**2. 404 Not Found**

**Fix**: Ensure `Publish Directory` is set to `.` in static site settings

**3. Changes Not Showing**

Render caches aggressively:
- Hard refresh: `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)
- Clear browser cache
- Try incognito mode

---

## 🔄 Continuous Deployment

### Auto-Deploy on Git Push

Both services auto-deploy when you push to `main`:

```bash
# Make changes
git add .
git commit -m "Update feature"
git push origin main

# Render automatically:
# 1. Detects push
# 2. Builds new version
# 3. Deploys seamlessly
```

### Manual Deploy

In Render dashboard:
1. Go to your service
2. Click "Manual Deploy"
3. Choose "Clear build cache & deploy"

---

## 🎉 Complete Deployment Checklist

### Before Deployment
- [x] Code pushed to GitHub ✅
- [ ] Google API key ready
- [ ] Render account created

### Backend Deployment
- [ ] Web Service created
- [ ] Environment variables set
- [ ] Backend deployed successfully
- [ ] Test API endpoint: `https://your-api.onrender.com/docs`

### Frontend Deployment
- [ ] Static Site created
- [ ] Frontend deployed
- [ ] Updated API URL in `app.html`
- [ ] Test frontend: `https://your-frontend.onrender.com`

### Post-Deployment
- [ ] Test quiz generation end-to-end
- [ ] Check browser console for errors
- [ ] Verify CORS working
- [ ] Monitor logs for issues

---

## 🚀 Quick Deploy Commands

### Update and Redeploy

```bash
# 1. Make changes locally
cd "C:\Projects\Wiki Quiz Generator"

# 2. Update frontend API URL
# Edit frontend/app.html - change API_URL to your Render backend

# 3. Commit and push
git add .
git commit -m "Deploy to Render"
git push origin main

# Render auto-deploys both services!
```

---

## 📝 Production Checklist

### Security
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS (automatic on Render)
- [ ] Configure CORS properly
- [ ] Set up rate limiting (optional)

### Performance
- [ ] Consider paid plan for no cold starts
- [ ] Enable caching
- [ ] Monitor response times
- [ ] Set up health checks

### Monitoring
- [ ] Check logs regularly
- [ ] Set up uptime monitoring (UptimeRobot)
- [ ] Track API usage
- [ ] Monitor error rates

---

## 🎯 What's Next?

### After Successful Deployment

1. **Share Your App!**
   ```
   Backend: https://wiki-quiz-api.onrender.com
   Frontend: https://wiki-quiz.onrender.com
   ```

2. **Set Up Custom Domain** (optional)
   - Buy domain from Namecheap/GoDaddy
   - Add to Render settings
   - Update DNS records

3. **Monitor Usage**
   - Check Render dashboard daily
   - Monitor API requests
   - Track error rates

4. **Scale if Needed**
   - Upgrade to paid plan ($7/month)
   - Add more instances
   - Enable auto-scaling

---

## 📞 Support

**Render Documentation:**
- https://render.com/docs
- https://render.com/docs/deploy-fastapi
- https://render.com/docs/static-sites

**Issues:**
- Check Render status: https://status.render.com
- Community forum: https://community.render.com

---

## ✨ Success!

Your Wiki Quiz Generator is now live on Render! 🎉

**Example URLs:**
- Backend: `https://wiki-quiz-api.onrender.com`
- Frontend: `https://wiki-quiz.onrender.com`
- API Docs: `https://wiki-quiz-api.onrender.com/docs`

**Share your quiz app with the world!** 🌍

---

**Made with ❤️ - Deployed on Render in minutes!**
