"""
Enhanced models with comprehensive validation
"""
from pydantic import BaseModel, Field, field_validator, HttpUrl
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum


class DifficultyLevel(str, Enum):
    """Quiz difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuizGenerationRequest(BaseModel):
    """Request model for quiz generation"""
    topic: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Wikipedia topic or article URL",
        examples=["Python Programming", "https://en.wikipedia.org/wiki/Artificial_intelligence"]
    )
    num_questions: int = Field(
        default=10,
        ge=3,
        le=20,
        description="Number of questions to generate"
    )
    difficulty: DifficultyLevel = Field(
        default=DifficultyLevel.MEDIUM,
        description="Quiz difficulty level"
    )
    
    @field_validator('topic')
    @classmethod
    def validate_topic(cls, v: str) -> str:
        """Validate and clean topic"""
        v = v.strip()
        if not v:
            raise ValueError("Topic cannot be empty")
        # Remove potentially harmful characters
        dangerous_chars = ['<', '>', '"', "'", ';', '&', '|']
        for char in dangerous_chars:
            if char in v:
                raise ValueError(f"Topic contains invalid character: {char}")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Artificial Intelligence",
                "num_questions": 10,
                "difficulty": "medium"
            }
        }


class QuizQuestion(BaseModel):
    """Model for a single quiz question"""
    question: str = Field(..., min_length=10, max_length=500)
    options: List[str] = Field(..., min_items=2, max_items=6)
    correct_answer: str = Field(..., min_length=1)
    explanation: Optional[str] = Field(None, max_length=1000)
    difficulty: Optional[DifficultyLevel] = None
    category: Optional[str] = None
    
    @field_validator('correct_answer')
    @classmethod
    def validate_correct_answer(cls, v: str, info) -> str:
        """Ensure correct answer is in options"""
        options = info.data.get('options', [])
        if options and v not in options:
            raise ValueError("Correct answer must be one of the options")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is the capital of France?",
                "options": ["London", "Berlin", "Paris", "Madrid"],
                "correct_answer": "Paris",
                "explanation": "Paris has been the capital of France since the 12th century",
                "difficulty": "easy",
                "category": "Geography"
            }
        }


class QuizResponse(BaseModel):
    """Response model for generated quiz"""
    topic: str
    questions: List[QuizQuestion]
    total_questions: int
    difficulty: DifficultyLevel
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    quiz_id: Optional[str] = None
    estimated_duration_minutes: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Artificial Intelligence",
                "questions": [
                    {
                        "question": "What is machine learning?",
                        "options": ["A type of AI", "A programming language", "A database", "An OS"],
                        "correct_answer": "A type of AI",
                        "difficulty": "easy"
                    }
                ],
                "total_questions": 10,
                "difficulty": "medium",
                "generated_at": "2025-11-08T12:00:00",
                "estimated_duration_minutes": 15
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    path: Optional[str] = Field(None, description="Request path that caused error")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Invalid input data",
                "details": {"field": "num_questions", "issue": "Value too large"},
                "timestamp": "2025-11-08T12:00:00",
                "path": "/api/v1/generate-quiz"
            }
        }


class HealthCheck(BaseModel):
    """Health check response"""
    status: Literal["healthy", "degraded", "unhealthy"]
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    checks: dict[str, bool]
    uptime_seconds: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "2.0.0",
                "timestamp": "2025-11-08T12:00:00",
                "checks": {
                    "api": True,
                    "ai_service": True,
                    "wikipedia": True
                },
                "uptime_seconds": 3600.5
            }
        }


class QuizSubmission(BaseModel):
    """Model for quiz answer submission"""
    quiz_id: str
    answers: dict[int, str] = Field(..., description="Question index to answer mapping")
    
    @field_validator('answers')
    @classmethod
    def validate_answers(cls, v: dict) -> dict:
        """Validate answers structure"""
        if not v:
            raise ValueError("At least one answer must be provided")
        return v


class QuizResult(BaseModel):
    """Model for quiz results"""
    quiz_id: str
    total_questions: int
    correct_answers: int
    wrong_answers: int
    score_percentage: float
    time_taken_seconds: Optional[int] = None
    passed: bool
    grade: Literal["A+", "A", "B", "C", "D", "F"]
    feedback: str
    details: List[dict]
    
    class Config:
        json_schema_extra = {
            "example": {
                "quiz_id": "quiz_12345",
                "total_questions": 10,
                "correct_answers": 8,
                "wrong_answers": 2,
                "score_percentage": 80.0,
                "passed": True,
                "grade": "B",
                "feedback": "Good job! You have a solid understanding of the topic.",
                "details": []
            }
        }
