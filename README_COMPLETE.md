# 📚 Wikipedia Quiz Generator - Complete Implementation

An AI-powered quiz generation system that extracts content from Wikipedia articles, identifies key entities (people, organizations, locations), and generates comprehensive quizzes using Google Gemini 2.0 Flash. Features include entity extraction, section-aware question generation, quiz history tracking, and interactive quiz taking.

## ✨ Features

### **Core Functionality**
- 🔍 **Entity Extraction**: Automatically identifies people, organizations, and locations from Wikipedia articles
- 📑 **Section Analysis**: Extracts article structure and section hierarchy
- 🤖 **AI-Powered Quiz Generation**: Uses Google Gemini 2.0 Flash with grounding prompts to minimize hallucination
- 💾 **Database Persistence**: PostgreSQL database for storing articles, quizzes, questions, and attempts
- 📊 **History Tracking**: View all past quizzes with detailed statistics
- 🎯 **Interactive Quiz Mode**: Take quizzes with instant scoring and explanations
- 🔗 **Related Topics**: Suggests related Wikipedia articles for further exploration
- 📖 **Study Guide Mode**: View all questions with answers and explanations

### **Technical Highlights**
- **Grounded Generation**: AI prompts explicitly reference article sections to prevent hallucination
- **Entity Classification**: Heuristic-based entity extraction using Wikipedia link analysis
- **Difficulty Levels**: Questions categorized as Easy, Medium, or Hard
- **Comprehensive Explanations**: Each answer includes context from the source article
- **Caching**: Prevents duplicate scraping of previously processed URLs
- **Two-Tab Interface**: Separate views for generating quizzes and viewing history

## 🏗️ Architecture

```
wiki-quiz-generator/
├── backend/
│   ├── main_complete.py          # FastAPI application with 7 endpoints
│   ├── db_models.py               # SQLAlchemy models (4 tables)
│   ├── database.py                # Database configuration
│   ├── wikipedia_service.py      # Enhanced scraping with entity extraction
│   ├── ai_service.py              # AI service with grounded prompts
│   ├── requirements_full.txt     # Complete dependencies
│   └── .env                       # Configuration (DATABASE_URL, GOOGLE_API_KEY)
├── frontend/
│   ├── index_enhanced.html        # Two-tab UI (Generate + History)
│   ├── app_enhanced.js            # Complete frontend logic
│   └── style_enhanced.css         # Comprehensive styling
└── README_COMPLETE.md             # This file
```

## 📊 Database Schema

### **WikiArticle**
- Stores scraped Wikipedia content
- Fields: url, title, summary, content, raw_html, key_entities (JSON), sections (JSON), related_topics (JSON)
- Entity structure: `{people: [], organizations: [], locations: []}`

### **Quiz**
- Quiz metadata and generation info
- Fields: article_id (FK), total_questions, difficulty_distribution (JSON), generation_time
- Linked to WikiArticle (cascade delete)

### **QuizQuestion**
- Individual quiz questions
- Fields: quiz_id (FK), question_text, option_a/b/c/d, correct_answer, explanation, difficulty, section_reference
- Supports difficulty levels: Easy, Medium, Hard

### **QuizAttempt**
- User quiz attempts with scoring
- Fields: quiz_id (FK), answers (JSON), score, percentage, time_taken
- Tracks performance over time

## 🚀 Setup Instructions

### **Prerequisites**
- Python 3.10 or higher
- PostgreSQL 13+ (or SQLite for development)
- Google API Key for Gemini (free tier available at [Google AI Studio](https://makersuite.google.com/app/apikey))

### **Backend Setup**

1. **Clone the repository**
```powershell
git clone https://github.com/Abhich05/Wiki-Quiz-Genrator.git
cd Wiki-Quiz-Genrator/backend
```

2. **Create and activate virtual environment**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. **Install dependencies**
```powershell
pip install -r requirements_full.txt
```

4. **Configure environment variables**
```powershell
# Copy template
Copy-Item .env.example .env

# Edit .env file with your configuration
notepad .env
```

Required variables:
```env
GOOGLE_API_KEY=your-google-api-key-here
DATABASE_URL=postgresql://user:password@localhost:5432/wiki_quiz
# For SQLite (development): DATABASE_URL=sqlite:///./wiki_quiz.db
```

5. **Set up PostgreSQL (Production)**

**Option A: Local PostgreSQL**
```powershell
# Install PostgreSQL
winget install PostgreSQL.PostgreSQL

# Create database
psql -U postgres
CREATE DATABASE wiki_quiz;
CREATE USER quiz_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE wiki_quiz TO quiz_user;
\q

# Update DATABASE_URL in .env
# DATABASE_URL=postgresql://quiz_user:your_password@localhost:5432/wiki_quiz
```

**Option B: SQLite (Development)**
```env
# In .env file
DATABASE_URL=sqlite:///./wiki_quiz.db
```

6. **Initialize database**
```powershell
# Database tables are created automatically on first run
python main_complete.py
```

7. **Run the backend**
```powershell
uvicorn main_complete:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at: http://localhost:8000

### **Frontend Setup**

1. **Navigate to frontend directory**
```powershell
cd ..\frontend
```

2. **Update API URL (if needed)**

Edit `app_enhanced.js`:
```javascript
// For local development
const API_BASE_URL = 'http://localhost:8000';

// For production (Render)
const API_BASE_URL = 'https://wiki-quiz-genrator-btjx.onrender.com';
```

3. **Serve frontend**

**Option A: Python HTTP Server**
```powershell
python -m http.server 3000
```

**Option B: Live Server (VS Code Extension)**
- Install "Live Server" extension in VS Code
- Right-click `index_enhanced.html` → "Open with Live Server"

**Option C: Static file server**
```powershell
npm install -g serve
serve .
```

Frontend will be available at: http://localhost:3000/index_enhanced.html

## 📡 API Endpoints

### **POST /api/generate-quiz**
Generate a quiz from a Wikipedia URL

**Request:**
```json
{
  "url": "https://en.wikipedia.org/wiki/Artificial_intelligence",
  "force_regenerate": false  // Optional: bypass cache
}
```

**Response:**
```json
{
  "id": 1,
  "url": "https://en.wikipedia.org/wiki/Artificial_intelligence",
  "title": "Artificial intelligence",
  "summary": "Article summary...",
  "key_entities": {
    "people": ["Alan Turing", "John McCarthy"],
    "organizations": ["MIT", "Stanford University"],
    "locations": ["United States", "United Kingdom"]
  },
  "sections": [
    {"title": "History", "level": 2},
    {"title": "Applications", "level": 2}
  ],
  "quiz": [
    {
      "question": "Who is considered the father of AI?",
      "option_a": "Alan Turing",
      "option_b": "John McCarthy",
      "option_c": "Marvin Minsky",
      "option_d": "Herbert Simon",
      "correct_answer": "B",
      "explanation": "John McCarthy coined the term 'artificial intelligence' in 1956.",
      "difficulty": "Easy",
      "section_reference": "History"
    }
  ],
  "related_topics": [
    "Machine learning",
    "Neural network",
    "Deep learning"
  ]
}
```

### **GET /api/quiz/{quiz_id}**
Get detailed information for a specific quiz

### **GET /api/quizzes**
Get list of all generated quizzes (history)

### **POST /api/quiz/attempt**
Submit quiz attempt and get score

**Request:**
```json
{
  "quiz_id": 1,
  "answers": {
    "0": "A",
    "1": "B",
    "2": "C"
  },
  "time_taken": 180  // seconds
}
```

**Response:**
```json
{
  "attempt_id": 1,
  "quiz_id": 1,
  "score": 2,
  "total_questions": 3,
  "percentage": 66.67,
  "time_taken": 180
}
```

### **DELETE /api/quiz/{quiz_id}**
Delete a quiz and all associated data (cascade)

### **GET /health**
Health check endpoint

### **GET /docs**
Interactive API documentation (Swagger UI)

## 🎯 Usage Guide

### **Generating a Quiz**

1. Go to the "Generate Quiz" tab
2. Enter a Wikipedia URL (e.g., `https://en.wikipedia.org/wiki/Python_(programming_language)`)
3. Click "Generate Quiz"
4. Wait for extraction (10-30 seconds depending on article length)
5. View extracted entities, sections, and related topics
6. Click "Take the Quiz" or "View as Study Guide"

### **Taking a Quiz**

1. Click "Take the Quiz" button
2. Answer multiple-choice questions
3. Track progress with the progress bar
4. Click "Submit Answers"
5. View score and detailed results
6. See explanations for each question

### **Viewing History**

1. Switch to "Past Quizzes" tab
2. See all generated quizzes in a table
3. Click "View" to see quiz details in a modal
4. Click "Delete" to remove a quiz
5. Click "Refresh" to reload the list

## 🧪 Testing

### **Manual Testing**

Test with these Wikipedia articles:
- https://en.wikipedia.org/wiki/Artificial_intelligence
- https://en.wikipedia.org/wiki/Python_(programming_language)
- https://en.wikipedia.org/wiki/World_War_II
- https://en.wikipedia.org/wiki/Albert_Einstein
- https://en.wikipedia.org/wiki/Climate_change

### **API Testing with curl**

```powershell
# Generate a quiz
curl -X POST "http://localhost:8000/api/generate-quiz" `
  -H "Content-Type: application/json" `
  -d '{"url":"https://en.wikipedia.org/wiki/Python_(programming_language)"}'

# Get quiz by ID
curl "http://localhost:8000/api/quiz/1"

# Get all quizzes
curl "http://localhost:8000/api/quizzes"

# Submit quiz attempt
curl -X POST "http://localhost:8000/api/quiz/attempt" `
  -H "Content-Type: application/json" `
  -d '{"quiz_id":1,"answers":{"0":"A","1":"B"},"time_taken":120}'
```

### **Database Verification**

```sql
-- Check article count
SELECT COUNT(*) FROM wiki_articles;

-- View recent quizzes
SELECT id, title, total_questions, created_at 
FROM quizzes 
ORDER BY created_at DESC LIMIT 10;

-- Check entity extraction
SELECT title, key_entities 
FROM wiki_articles 
WHERE key_entities IS NOT NULL;

-- View quiz attempts
SELECT quiz_id, score, percentage, time_taken 
FROM quiz_attempts 
ORDER BY created_at DESC;
```

## 🎨 Prompt Engineering

### **Key Prompt Strategies**

1. **Grounding**: Explicit instructions to use only article content
2. **Section References**: Questions must cite source sections
3. **Hallucination Prevention**: "DO NOT use external knowledge"
4. **Structured Output**: JSON format with strict schema
5. **Difficulty Distribution**: Balanced mix of Easy/Medium/Hard

### **Quiz Generation Prompt** (from `ai_service.py`)
```
Generate {num_questions} multiple-choice quiz questions based on the following Wikipedia article.

CRITICAL REQUIREMENTS:
1. ALL questions MUST be directly answerable from the article content below
2. DO NOT use external knowledge or information not in the article
3. Each question must reference which section it comes from
4. Generate questions of varying difficulty (Easy, Medium, Hard)
5. Ensure questions test understanding, not just memorization

Article sections provided:
{sections}

Article content:
{content}

For each question, provide:
- Clear question text
- 4 distinct answer options (A, B, C, D)
- Correct answer (A, B, C, or D)
- Explanation with section reference
- Difficulty level (Easy, Medium, or Hard)

Return as JSON array...
```

## 🚢 Deployment

### **Render Deployment**

**Backend:**
1. Push to GitHub
2. Create new Web Service on Render
3. Connect to GitHub repository
4. Configure:
   - Build Command: `pip install -r backend/requirements_full.txt`
   - Start Command: `cd backend && uvicorn main_complete:app --host 0.0.0.0 --port $PORT`
   - Environment Variables: `GOOGLE_API_KEY`, `DATABASE_URL`
4. Add PostgreSQL database (Render Dashboard → New PostgreSQL)
5. Copy Internal Database URL to `DATABASE_URL` environment variable

**Frontend:**
1. Update `API_BASE_URL` in `app_enhanced.js` to Render URL
2. Deploy as Static Site on Render or use GitHub Pages
3. Point to `frontend/index_enhanced.html`

### **Heroku Deployment**

```powershell
# Backend
cd backend
heroku create wiki-quiz-backend
heroku addons:create heroku-postgresql:mini
heroku config:set GOOGLE_API_KEY=your_key
git push heroku main

# Frontend
cd frontend
heroku create wiki-quiz-frontend
git push heroku main
```

## 📈 Performance & Optimization

- **Caching**: URLs are cached in database; set `force_regenerate=true` to bypass
- **Entity Extraction**: Uses heuristic patterns for fast classification
- **Database Indexing**: Indexes on `url` (WikiArticle) and `quiz_id` (foreign keys)
- **Connection Pooling**: SQLAlchemy engine with pool size 5, max overflow 10
- **Async Processing**: FastAPI async endpoints for concurrent requests

## 🐛 Troubleshooting

### **Common Issues**

**Issue: "Failed to generate quiz"**
- Check if Wikipedia URL is valid and accessible
- Verify GOOGLE_API_KEY is set correctly
- Check API rate limits (Gemini free tier: 60 requests/minute)

**Issue: Database connection errors**
- Verify DATABASE_URL format
- For PostgreSQL: Ensure database exists and user has permissions
- For SQLite: Check file permissions in backend directory

**Issue: Entity extraction returns empty arrays**
- Some articles have minimal entity information
- Entity extraction uses heuristics; may miss some entities
- Check article HTML structure (infoboxes, linked text)

**Issue: Frontend can't connect to backend**
- Check API_BASE_URL in app_enhanced.js
- Verify backend is running on correct port
- Check CORS settings if using different domains

## 📚 Dependencies

### **Backend**
```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
google-generativeai>=0.3.0
beautifulsoup4>=4.12.0
requests>=2.31.0
python-dotenv>=1.0.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
alembic>=1.13.0
pydantic>=2.0.0
```

### **Frontend**
- Vanilla JavaScript (no build required)
- CSS3 with modern features
- No external dependencies

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/YourFeature`)
3. Commit changes (`git commit -m 'Add YourFeature'`)
4. Push to branch (`git push origin feature/YourFeature`)
5. Open Pull Request

## 📝 License

This project is open source and available under the MIT License.

## 👤 Author

**Abhishek Choudhary**
- GitHub: [@Abhich05](https://github.com/Abhich05)
- Repository: [Wiki-Quiz-Genrator](https://github.com/Abhich05/Wiki-Quiz-Genrator)

## 🙏 Acknowledgments

- **Google Gemini 2.0 Flash**: AI model for quiz generation
- **Wikipedia**: Content source and data provider
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **BeautifulSoup**: HTML parsing library

## 📸 Screenshots

### Generate Quiz Tab
![Generate Quiz](screenshots/generate-quiz.png)
- URL input with validation
- Entity extraction display
- Section analysis
- Related topics suggestions

### Quiz Taking Mode
![Take Quiz](screenshots/take-quiz.png)
- Progress tracking
- Multiple choice questions
- Difficulty badges

### Quiz Results
![Quiz Results](screenshots/results.png)
- Score visualization
- Detailed explanations
- Correct/incorrect breakdown

### History Tab
![History](screenshots/history.png)
- Table of all quizzes
- Quick actions (View, Delete)
- Sortable columns

### Quiz Details Modal
![Details Modal](screenshots/modal.png)
- Complete quiz information
- All questions with answers
- Entity and section data

---

**Project Status**: ✅ Complete and Production-Ready

**Last Updated**: January 2025
