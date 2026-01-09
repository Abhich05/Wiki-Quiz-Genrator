"""
Wiki Quiz Generator - Production Server
Google Gemini AI + Wikipedia Scraping
"""
import logging
import os
from typing import Dict, List
from datetime import datetime
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
import requests
from bs4 import BeautifulSoup
import html2text
import google.generativeai as genai
import json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Wiki Quiz Generator",
    description="Generate AI-powered quizzes from Wikipedia articles",
    version="2.0.0"
)

# CORS - Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Google Gemini AI
google_api_key = os.getenv("GOOGLE_API_KEY", "")
if not google_api_key or google_api_key == "your-google-api-key-here":
    logger.warning("⚠️ Google API key not configured! Set GOOGLE_API_KEY in .env")
    model = None
else:
    try:
        genai.configure(api_key=google_api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        logger.info("✅ Google Gemini 2.0 Flash initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Gemini: {e}")
        model = None

# In-memory storage (can be replaced with database)
articles_db = {}
quizzes_db = {}

# ============================================================================
# Pydantic Models
# ============================================================================

class GenerateRequest(BaseModel):
    url: HttpUrl
    num_questions: int = 5
    difficulty: str = "medium"

class Question(BaseModel):
    id: int
    question: str
    options: List[str]
    correct_answer: int
    explanation: str

class Quiz(BaseModel):
    id: str
    article_title: str
    questions: List[Question]
    created_at: str

class HealthResponse(BaseModel):
    status: str
    ai_enabled: bool
    model: str
    version: str

# ============================================================================
# Core Functions
# ============================================================================

def scrape_wikipedia(url: str) -> Dict[str, str]:
    """Scrape Wikipedia article content"""
    try:
        logger.info(f"📰 Scraping Wikipedia: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(str(url), headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title = soup.find('h1', class_='firstHeading')
        title_text = title.get_text() if title else "Unknown Article"
        
        # Extract main content
        content_div = soup.find('div', class_='mw-parser-output')
        if not content_div:
            raise ValueError("Could not find article content")
        
        # Remove unwanted elements
        for unwanted in content_div.find_all(['table', 'script', 'style', 'sup']):
            unwanted.decompose()
        
        # Convert HTML to text
        h = html2text.HTML2Text()
        h.ignore_links = True
        h.ignore_images = True
        h.ignore_emphasis = False
        text_content = h.handle(str(content_div))
        
        # Clean and limit content
        text_content = text_content.strip()
        text_content = text_content[:12000]  # Limit for API
        
        logger.info(f"✅ Scraped '{title_text}' - {len(text_content)} characters")
        
        return {
            "title": title_text,
            "content": text_content,
            "url": str(url)
        }
        
    except requests.RequestException as e:
        logger.error(f"❌ Network error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch Wikipedia article: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Scraping error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to scrape article: {str(e)}")


def generate_quiz_with_ai(article: Dict, num_questions: int, difficulty: str) -> List[Dict]:
    """Generate quiz questions using Google Gemini AI"""
    if not model:
        raise HTTPException(
            status_code=503, 
            detail="AI service not available. Please configure GOOGLE_API_KEY in .env"
        )
    
    try:
        logger.info(f"🤖 Generating {num_questions} {difficulty} questions with Gemini AI...")
        
        prompt = f"""Based on the following Wikipedia article about "{article['title']}", generate {num_questions} multiple-choice quiz questions at {difficulty} difficulty level.

Article content:
{article['content']}

Generate questions in this EXACT JSON format:
{{
  "questions": [
    {{
      "question": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": 0,
      "explanation": "Detailed explanation of why the answer is correct"
    }}
  ]
}}

Requirements:
- Each question must have EXACTLY 4 options
- correct_answer is the index (0-3) of the correct option
- Questions should be clear, educational, and engaging
- All answers must be verifiable from the article content
- Difficulty: {difficulty} (easy = basic facts, medium = concepts, hard = analysis)
- Include diverse question types (facts, concepts, analysis)
- Explanations should reference specific article content
- Return ONLY valid JSON, no markdown code blocks, no additional text
"""

        # Generate content with Gemini
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Clean markdown code blocks if present
        if result_text.startswith('```'):
            lines = result_text.split('\n')
            result_text = '\n'.join(lines[1:-1])
            if result_text.startswith('json'):
                result_text = result_text[4:].strip()
        
        # Parse JSON
        try:
            result = json.loads(result_text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}\nResponse: {result_text[:500]}")
            raise HTTPException(status_code=500, detail="AI generated invalid response format")
        
        questions = result.get("questions", [])
        
        if not questions:
            raise HTTPException(status_code=500, detail="AI generated no questions")
        
        # Validate and add IDs
        for i, q in enumerate(questions):
            q["id"] = i + 1
            # Validate structure
            if not all(k in q for k in ["question", "options", "correct_answer", "explanation"]):
                raise HTTPException(status_code=500, detail=f"Invalid question structure at index {i}")
            if len(q["options"]) != 4:
                raise HTTPException(status_code=500, detail=f"Question {i+1} doesn't have 4 options")
        
        logger.info(f"✅ Generated {len(questions)} high-quality questions")
        return questions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ AI generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI generation error: {str(e)}")

# ============================================================================
# API Routes
# ============================================================================

@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "ai_enabled": model is not None,
        "model": "gemini-2.0-flash" if model else "none",
        "version": "2.0.0"
    }


@app.post("/api/v2/articles/generate", response_model=Quiz)
async def generate_quiz(request: GenerateRequest):
    """
    Generate a quiz from a Wikipedia article URL
    
    - **url**: Wikipedia article URL (e.g., https://en.wikipedia.org/wiki/Python)
    - **num_questions**: Number of questions to generate (1-20, default: 5)
    - **difficulty**: Question difficulty - easy, medium, or hard (default: medium)
    """
    try:
        # Validate inputs
        if request.num_questions < 1 or request.num_questions > 20:
            raise HTTPException(status_code=400, detail="num_questions must be between 1 and 20")
        
        if request.difficulty not in ["easy", "medium", "hard"]:
            raise HTTPException(status_code=400, detail="difficulty must be easy, medium, or hard")
        
        # Step 1: Scrape Wikipedia article
        article = scrape_wikipedia(request.url)
        
        # Step 2: Generate quiz with AI
        questions = generate_quiz_with_ai(
            article,
            request.num_questions,
            request.difficulty
        )
        
        # Step 3: Create and store quiz
        quiz_id = f"quiz_{len(quizzes_db) + 1}_{int(datetime.utcnow().timestamp())}"
        quiz = {
            "id": quiz_id,
            "article_title": article["title"],
            "questions": questions,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Store in memory
        quizzes_db[quiz_id] = quiz
        articles_db[quiz_id] = article
        
        logger.info(f"✅ Quiz '{quiz_id}' created successfully for '{article['title']}'")
        
        return quiz
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.get("/api/v2/quizzes/{quiz_id}", response_model=Quiz)
async def get_quiz(quiz_id: str):
    """Retrieve a previously generated quiz by ID"""
    if quiz_id not in quizzes_db:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    return quizzes_db[quiz_id]


@app.get("/api/v2/quizzes")
async def list_quizzes():
    """List all generated quizzes"""
    return {
        "total": len(quizzes_db),
        "quizzes": [
            {
                "id": quiz_id,
                "title": quiz["article_title"],
                "num_questions": len(quiz["questions"]),
                "created_at": quiz["created_at"]
            }
            for quiz_id, quiz in quizzes_db.items()
        ]
    }

# ============================================================================
# Startup & Main
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Run on server startup"""
    logger.info("=" * 80)
    logger.info("🚀 Wiki Quiz Generator - Production Server Starting")
    logger.info("=" * 80)
    logger.info(f"AI Model: {'Google Gemini 2.0 Flash' if model else 'Not Configured'}")
    logger.info(f"Status: {'Ready' if model else 'Limited Mode - Configure GOOGLE_API_KEY'}")
    logger.info("=" * 80)


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "127.0.0.1")
    
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        app, 
        host=host, 
        port=port,
        log_level="info"
    )
