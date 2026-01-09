"""
Complete API implementation with database integration
Meets all project requirements
"""
import time
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field
import logging

# Import our modules
from config import settings
from database import get_db, init_db
from db_models import WikiArticle, Quiz, QuizQuestion, QuizAttempt
from wikipedia_service import enhanced_wikipedia_service
from ai_service import enhanced_ai_service

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Application start time
app_start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting Wiki Quiz Generator API v2.0")
    logger.info("📊 Initializing database...")
    init_db()
    logger.info("✅ Database ready")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down application")


# Initialize FastAPI
app = FastAPI(
    title="Wiki Quiz Generator API",
    description="Generate AI-powered quizzes from Wikipedia articles with full history tracking",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API
class QuizGenerationRequest(BaseModel):
    url: str = Field(..., description="Wikipedia article URL or topic name")
    num_questions: int = Field(default=10, ge=5, le=15, description="Number of questions")
    force_regenerate: bool = Field(default=False, description="Force regeneration even if cached")
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://en.wikipedia.org/wiki/Alan_Turing",
                "num_questions": 10,
                "force_regenerate": False
            }
        }


class QuizQuestionResponse(BaseModel):
    question: str
    options: List[str]
    answer: str
    difficulty: str
    explanation: str
    section: Optional[str] = None


class QuizResponse(BaseModel):
    id: int
    url: str
    title: str
    summary: str
    key_entities: dict
    sections: List[str]
    quiz: List[QuizQuestionResponse]
    related_topics: List[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class QuizHistoryItem(BaseModel):
    id: int
    article_id: int
    url: str
    title: str
    total_questions: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class QuizAttemptRequest(BaseModel):
    quiz_id: int
    answers: dict = Field(..., description="Question number to answer mapping")
    time_taken_seconds: int = Field(default=0)


class QuizAttemptResponse(BaseModel):
    id: int
    quiz_id: int
    score: int
    total_questions: int
    percentage: float
    correct_answers: List[int]
    wrong_answers: List[int]
    
    class Config:
        from_attributes = True


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": "Wiki Quiz Generator API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "generate_quiz": "POST /api/generate-quiz",
            "get_quiz": "GET /api/quiz/{quiz_id}",
            "list_quizzes": "GET /api/quizzes",
            "submit_attempt": "POST /api/quiz/attempt"
        }
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "version": "2.0.0",
        "uptime_seconds": time.time() - app_start_time,
        "checks": {
            "api": True,
            "database": db_status == "healthy",
            "ai_configured": bool(settings.google_api_key),
        }
    }


@app.post("/api/generate-quiz", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def generate_quiz(
    request: QuizGenerationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate a quiz from Wikipedia article
    
    - Scrapes Wikipedia article
    - Extracts entities, sections, and content
    - Generates AI-powered quiz questions
    - Suggests related topics
    - Stores everything in database
    - Returns complete quiz data
    """
    logger.info(f"Quiz generation requested for: {request.url}")
    
    try:
        # Check if article already exists (caching)
        existing_article = db.query(WikiArticle).filter(
            WikiArticle.url == request.url
        ).first()
        
        if existing_article and not request.force_regenerate:
            logger.info(f"Using cached article: {existing_article.title}")
            article = existing_article
        else:
            # Scrape Wikipedia article
            logger.info("Scraping Wikipedia article...")
            article_data = enhanced_wikipedia_service.scrape_full_article(request.url)
            
            if existing_article:
                # Update existing article
                article = existing_article
                article.summary = article_data["summary"]
                article.content = article_data["content"]
                article.raw_html = article_data["raw_html"]
                article.key_entities = article_data["key_entities"]
                article.sections = article_data["sections"]
                article.processing_time_seconds = article_data["processing_time"]
                article.updated_at = datetime.utcnow()
            else:
                # Create new article
                article = WikiArticle(
                    url=article_data["url"],
                    title=article_data["title"],
                    summary=article_data["summary"],
                    content=article_data["content"],
                    raw_html=article_data["raw_html"],
                    key_entities=article_data["key_entities"],
                    sections=article_data["sections"],
                    processing_time_seconds=article_data["processing_time"]
                )
                db.add(article)
                db.commit()
                db.refresh(article)
        
        # Generate quiz with AI
        logger.info("Generating quiz with AI...")
        quiz_data = enhanced_ai_service.generate_comprehensive_quiz(
            title=article.title,
            summary=article.summary,
            content=article.content,
            sections=article.sections or [],
            num_questions=request.num_questions
        )
        
        # Store quiz in database
        quiz = Quiz(
            article_id=article.id,
            total_questions=len(quiz_data["questions"]),
            difficulty_distribution=quiz_data["difficulty_distribution"],
            generation_time_seconds=quiz_data["generation_time"],
            llm_model=settings.ai_model
        )
        db.add(quiz)
        db.commit()
        db.refresh(quiz)
        
        # Store questions
        for i, q_data in enumerate(quiz_data["questions"]):
            question = QuizQuestion(
                quiz_id=quiz.id,
                question_number=i + 1,
                question_text=q_data["question"],
                option_a=q_data["options"][0] if len(q_data["options"]) > 0 else "",
                option_b=q_data["options"][1] if len(q_data["options"]) > 1 else "",
                option_c=q_data["options"][2] if len(q_data["options"]) > 2 else "",
                option_d=q_data["options"][3] if len(q_data["options"]) > 3 else "",
                correct_answer=q_data["answer"],
                explanation=q_data.get("explanation", ""),
                difficulty=q_data["difficulty"],
                section_reference=q_data.get("section", "")
            )
            db.add(question)
        
        # Update article with related topics
        article.related_topics = quiz_data["related_topics"]
        
        db.commit()
        
        # Build response
        quiz_questions = [
            QuizQuestionResponse(
                question=q_data["question"],
                options=q_data["options"],
                answer=q_data["answer"],
                difficulty=q_data["difficulty"],
                explanation=q_data.get("explanation", ""),
                section=q_data.get("section")
            )
            for q_data in quiz_data["questions"]
        ]
        
        response = QuizResponse(
            id=quiz.id,
            url=article.url,
            title=article.title,
            summary=article.summary,
            key_entities=article.key_entities or {},
            sections=article.sections or [],
            quiz=quiz_questions,
            related_topics=quiz_data["related_topics"],
            created_at=quiz.created_at
        )
        
        logger.info(f"✅ Quiz generated successfully: ID={quiz.id}")
        return response
        
    except Exception as e:
        logger.error(f"Failed to generate quiz: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "QuizGenerationError", "message": str(e)}
        )


@app.get("/api/quiz/{quiz_id}", response_model=QuizResponse)
async def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    """Get full quiz details by ID"""
    
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    article = quiz.article
    questions = sorted(quiz.questions, key=lambda q: q.question_number)
    
    quiz_questions = [
        QuizQuestionResponse(
            question=q.question_text,
            options=[q.option_a, q.option_b, q.option_c, q.option_d],
            answer=q.correct_answer,
            difficulty=q.difficulty,
            explanation=q.explanation or "",
            section=q.section_reference
        )
        for q in questions
    ]
    
    return QuizResponse(
        id=quiz.id,
        url=article.url,
        title=article.title,
        summary=article.summary,
        key_entities=article.key_entities or {},
        sections=article.sections or [],
        quiz=quiz_questions,
        related_topics=article.related_topics or [],
        created_at=quiz.created_at
    )


@app.get("/api/quizzes", response_model=List[QuizHistoryItem])
async def list_quizzes(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    List all quizzes (history view)
    Returns summary information for all generated quizzes
    """
    quizzes = db.query(Quiz).join(WikiArticle).order_by(
        Quiz.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return [
        QuizHistoryItem(
            id=quiz.id,
            article_id=quiz.article_id,
            url=quiz.article.url,
            title=quiz.article.title,
            total_questions=quiz.total_questions,
            created_at=quiz.created_at
        )
        for quiz in quizzes
    ]


@app.post("/api/quiz/attempt", response_model=QuizAttemptResponse)
async def submit_quiz_attempt(
    request: QuizAttemptRequest,
    db: Session = Depends(get_db)
):
    """
    Submit quiz attempt and calculate score
    """
    quiz = db.query(Quiz).filter(Quiz.id == request.quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    questions = sorted(quiz.questions, key=lambda q: q.question_number)
    
    # Calculate score
    correct = []
    wrong = []
    
    for q in questions:
        user_answer = request.answers.get(str(q.question_number))
        if user_answer == q.correct_answer:
            correct.append(q.question_number)
        else:
            wrong.append(q.question_number)
    
    score = len(correct)
    total = len(questions)
    percentage = (score / total * 100) if total > 0 else 0
    
    # Store attempt
    attempt = QuizAttempt(
        quiz_id=quiz.id,
        answers=request.answers,
        score=score,
        total_questions=total,
        percentage=percentage,
        time_taken_seconds=request.time_taken_seconds,
        completed_at=datetime.utcnow()
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    
    return QuizAttemptResponse(
        id=attempt.id,
        quiz_id=quiz.id,
        score=score,
        total_questions=total,
        percentage=percentage,
        correct_answers=correct,
        wrong_answers=wrong
    )


@app.delete("/api/quiz/{quiz_id}")
async def delete_quiz(quiz_id: int, db: Session = Depends(get_db)):
    """Delete a quiz and its associated data"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    db.delete(quiz)
    db.commit()
    
    return {"message": "Quiz deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    
    logger.info("🔥 Starting development server...")
    logger.info(f"📝 API Documentation: http://{settings.host}:{settings.port}/docs")
    logger.info(f"🔍 Health Check: http://{settings.host}:{settings.port}/health")
    
    uvicorn.run(
        "main_complete:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level="info"
    )
