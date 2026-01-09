"""
SQLAlchemy database models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class WikiArticle(Base):
    """Model for storing Wikipedia articles and their metadata"""
    __tablename__ = "wiki_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(500), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    summary = Column(Text)
    content = Column(Text)  # Full article text
    raw_html = Column(Text)  # Raw HTML for reference
    
    # Extracted entities
    key_entities = Column(JSON)  # {"people": [], "organizations": [], "locations": []}
    sections = Column(JSON)  # List of section titles
    related_topics = Column(JSON)  # List of related Wikipedia topics
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processing_time_seconds = Column(Float)
    
    # Relationships
    quizzes = relationship("Quiz", back_populates="article", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<WikiArticle(id={self.id}, title='{self.title}')>"


class Quiz(Base):
    """Model for storing generated quizzes"""
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("wiki_articles.id"), nullable=False)
    
    # Quiz metadata
    total_questions = Column(Integer)
    difficulty_distribution = Column(JSON)  # {"easy": 2, "medium": 5, "hard": 3}
    
    # Generation metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    generation_time_seconds = Column(Float)
    llm_model = Column(String(100))
    
    # Relationships
    article = relationship("WikiArticle", back_populates="quizzes")
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Quiz(id={self.id}, article_id={self.article_id}, questions={self.total_questions})>"


class QuizQuestion(Base):
    """Model for storing individual quiz questions"""
    __tablename__ = "quiz_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    
    # Question content
    question_number = Column(Integer)  # Order in quiz
    question_text = Column(Text, nullable=False)
    option_a = Column(String(500))
    option_b = Column(String(500))
    option_c = Column(String(500))
    option_d = Column(String(500))
    correct_answer = Column(String(500), nullable=False)
    explanation = Column(Text)
    difficulty = Column(String(20))  # easy, medium, hard
    section_reference = Column(String(200))  # Which article section this relates to
    
    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    
    def __repr__(self):
        return f"<QuizQuestion(id={self.id}, difficulty='{self.difficulty}')>"


class QuizAttempt(Base):
    """Model for storing user quiz attempts and scores"""
    __tablename__ = "quiz_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    
    # User info (optional, for future authentication)
    user_id = Column(String(100))  # Can be session ID or user ID
    
    # Attempt data
    answers = Column(JSON)  # {"question_1": "answer", ...}
    score = Column(Integer)  # Number of correct answers
    total_questions = Column(Integer)
    percentage = Column(Float)
    time_taken_seconds = Column(Integer)
    
    # Metadata
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="attempts")
    
    def __repr__(self):
        return f"<QuizAttempt(id={self.id}, score={self.score}/{self.total_questions})>"
