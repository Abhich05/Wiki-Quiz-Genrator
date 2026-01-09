# 🚀 Quick Start Guide

Get the Wikipedia Quiz Generator running in 5 minutes!

## Prerequisites

- Python 3.10+ installed
- Git installed
- Google API Key (free from [Google AI Studio](https://makersuite.google.com/app/apikey))

## Installation Steps

### 1. Clone the Repository

```powershell
git clone https://github.com/Abhich05/Wiki-Quiz-Genrator.git
cd Wiki-Quiz-Genrator
```

### 2. Set Up Backend

```powershell
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements_full.txt
```

### 3. Configure Environment

```powershell
# Copy environment template
Copy-Item .env.example .env

# Edit .env file
notepad .env
```

Add your Google API key:
```env
GOOGLE_API_KEY=your-actual-api-key-here
DATABASE_URL=sqlite:///./wiki_quiz.db
```

### 4. Test Setup

```powershell
# Run setup test
python test_setup.py
```

If all tests pass ✅, continue to step 5!

### 5. Start Backend Server

```powershell
uvicorn main_complete:app --reload
```

Backend will run at: **http://localhost:8000**

### 6. Open Frontend

In a new terminal/browser:

```powershell
cd ..\frontend
python -m http.server 3000
```

Then open: **http://localhost:3000/index_enhanced.html**

## First Quiz

1. Enter a Wikipedia URL:
   ```
   https://en.wikipedia.org/wiki/Python_(programming_language)
   ```

2. Click "Generate Quiz"

3. Wait 20-30 seconds for:
   - Article scraping
   - Entity extraction
   - AI quiz generation

4. View the results:
   - Key entities extracted
   - Article sections
   - Quiz questions with explanations
   - Related topics

5. Click "Take the Quiz" to test yourself!

## Troubleshooting

### "Module not found" errors
```powershell
pip install -r requirements_full.txt
```

### "GOOGLE_API_KEY not set"
- Check `.env` file exists in backend folder
- Verify API key is correct (no spaces)
- Get a free key at https://makersuite.google.com/app/apikey

### "Failed to connect to API"
- Verify backend is running (http://localhost:8000)
- Check `API_BASE_URL` in `frontend/app_enhanced.js`
- For local development, should be: `http://localhost:8000`

### Database errors
```powershell
# Delete existing database
Remove-Item wiki_quiz.db

# Restart backend (will recreate tables)
uvicorn main_complete:app --reload
```

## API Documentation

Once backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
wiki-quiz-generator/
├── backend/
│   ├── main_complete.py      # FastAPI application
│   ├── db_models.py           # Database models
│   ├── wikipedia_service.py  # Scraping logic
│   ├── ai_service.py          # Quiz generation
│   └── test_setup.py          # Setup verification
├── frontend/
│   ├── index_enhanced.html    # Main UI
│   ├── app_enhanced.js        # Frontend logic
│   └── style_enhanced.css     # Styles
└── sample_data/               # Test cases
```

## Next Steps

✅ System is working!

Now try:
- **History Tab**: View all past quizzes
- **Study Guide**: See questions with answers
- **Quiz Mode**: Test your knowledge
- **Related Topics**: Explore connected articles

## Need Help?

1. Check `README_COMPLETE.md` for detailed documentation
2. Run `python test_setup.py` to diagnose issues
3. View API docs at http://localhost:8000/docs
4. Check sample data in `sample_data/` folder

## Deployment

Ready to deploy? See `README_COMPLETE.md` for:
- Render deployment (free tier available)
- PostgreSQL setup
- Environment configuration
- Production best practices

---

**Estimated Setup Time**: 5-10 minutes

**First Quiz Generation Time**: 20-30 seconds

**Enjoy creating AI-powered quizzes! 🎉**
