# Wiki Quiz Generator - Deployment Guide

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements_prod.txt
```

### 2. Configure Environment
Create `.env` file in `backend/` directory:
```env
GOOGLE_API_KEY=your-google-api-key-here
PORT=8000
HOST=0.0.0.0
```

Get your Google API key from: https://makersuite.google.com/app/apikey

### 3. Start Server
```bash
cd backend
python main.py
```

Server runs on: http://localhost:8000

### 4. Open Frontend
Open `frontend/app.html` in your browser or serve with:
```bash
cd frontend
python -m http.server 3000
```

Frontend: http://localhost:3000/app.html

## 📦 Production Deployment

### Option 1: Local/VPS Deployment

#### Using Gunicorn (Linux/Mac)
```bash
cd backend
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Using PM2 (Node.js process manager)
```bash
pm2 start "uvicorn main:app --host 0.0.0.0 --port 8000" --name wiki-quiz
pm2 save
pm2 startup
```

### Option 2: Docker Deployment

Create `Dockerfile` in backend/:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements_prod.txt .
RUN pip install --no-cache-dir -r requirements_prod.txt

COPY . .

ENV PORT=8000
ENV HOST=0.0.0.0

CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t wiki-quiz .
docker run -p 8000:8000 --env-file .env wiki-quiz
```

### Option 3: Cloud Platform Deployment

#### Render.com
1. Create new Web Service
2. Connect your GitHub repository
3. Set build command: `pip install -r backend/requirements_prod.txt`
4. Set start command: `cd backend && python main.py`
5. Add environment variable: `GOOGLE_API_KEY`

#### Railway.app
1. Create new project
2. Add GitHub repository
3. Set root directory: `backend`
4. Add `GOOGLE_API_KEY` environment variable
5. Deploy automatically

#### Vercel (Frontend)
1. Deploy frontend folder
2. Set output directory: `frontend`
3. Update API_BASE in app.html to your backend URL

#### Netlify (Frontend)
1. Deploy frontend folder
2. Update API_BASE in app.html to your backend URL

## 🔧 Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_API_KEY` | Yes | - | Google Gemini API key |
| `PORT` | No | 8000 | Server port |
| `HOST` | No | 127.0.0.1 | Server host |

### API Endpoints

- `GET /` - Health check
- `POST /api/v2/articles/generate` - Generate quiz
- `GET /api/v2/quizzes/{id}` - Get quiz by ID
- `GET /api/v2/quizzes` - List all quizzes

## 📊 Features

- ✅ Google Gemini 2.0 Flash AI
- ✅ Wikipedia article scraping
- ✅ Customizable quiz difficulty
- ✅ 1-20 questions per quiz
- ✅ Detailed explanations
- ✅ Beautiful responsive UI
- ✅ Real-time score tracking
- ✅ In-memory storage (can add DB)

## 🛠️ Development

### Run in Development Mode
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Test the API
```bash
curl -X POST "http://localhost:8000/api/v2/articles/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://en.wikipedia.org/wiki/Python_(programming_language)",
    "num_questions": 5,
    "difficulty": "medium"
  }'
```

## 📝 Project Structure

```
Wiki Quiz Generator/
├── backend/
│   ├── main.py                 # Production server
│   ├── requirements_prod.txt   # Production dependencies
│   └── .env                    # Environment variables
├── frontend/
│   └── app.html               # Production frontend
└── README_DEPLOY.md           # This file
```

## 🔒 Security Notes

- Never commit `.env` file
- Use HTTPS in production
- Add rate limiting for public deployments
- Consider adding authentication
- Use environment variables for all secrets

## 📈 Scaling

### Add Database (PostgreSQL)
```python
# In main.py, replace in-memory storage with:
from sqlalchemy import create_engine
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
```

### Add Caching (Redis)
```python
import redis
redis_client = redis.from_url(os.getenv("REDIS_URL"))
```

### Add Rate Limiting
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/v2/articles/generate")
@limiter.limit("5/minute")
async def generate_quiz(request: Request, ...):
    ...
```

## 🐛 Troubleshooting

### "AI service not available"
- Check GOOGLE_API_KEY is set correctly
- Verify API key is valid
- Check internet connection

### "Failed to scrape Wikipedia"
- Wikipedia might be blocking requests
- Try different articles
- Check network connectivity

### Frontend can't connect to backend
- Update API_BASE in app.html
- Enable CORS (already enabled)
- Check backend is running

## 📞 Support

For issues, check:
1. Server logs in terminal
2. Browser console for frontend errors
3. Network tab for API errors

## 🎉 Success!

Your Wiki Quiz Generator is now deployed and ready to use!

Visit your app and start generating AI-powered quizzes! 🚀
