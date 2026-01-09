"""
Comprehensive test suite for Wiki Quiz Generator
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from main_enhanced import app
from models import QuizGenerationRequest, DifficultyLevel, QuizQuestion
from services import WikipediaService, AIService, WikipediaException, AIServiceException


client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns basic info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "app" in data
        assert "version" in data
        assert "status" in data
    
    def test_health_endpoint(self):
        """Test detailed health check"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "checks" in data
        assert "uptime_seconds" in data


class TestQuizGeneration:
    """Test quiz generation endpoint"""
    
    def test_generate_quiz_valid_request(self):
        """Test quiz generation with valid request"""
        request_data = {
            "topic": "Python Programming",
            "num_questions": 5,
            "difficulty": "medium"
        }
        
        with patch('services.wikipedia_service.get_article_summary') as mock_wiki, \
             patch('services.ai_service.generate_quiz') as mock_ai:
            
            # Mock responses
            mock_wiki.return_value = "Python is a programming language..."
            mock_ai.return_value = [
                QuizQuestion(
                    question="What is Python?",
                    options=["A snake", "A language", "A tool", "A framework"],
                    correct_answer="A language",
                    difficulty=DifficultyLevel.MEDIUM
                )
            ] * 5
            
            response = client.post("/generate-quiz", json=request_data)
            assert response.status_code == 200
            data = response.json()
            assert data["topic"] == "Python Programming"
            assert data["total_questions"] == 5
            assert "quiz_id" in data
            assert len(data["questions"]) == 5
    
    def test_generate_quiz_invalid_num_questions(self):
        """Test quiz generation with invalid number of questions"""
        request_data = {
            "topic": "Python Programming",
            "num_questions": 100,  # Too many
            "difficulty": "medium"
        }
        
        response = client.post("/generate-quiz", json=request_data)
        assert response.status_code == 422  # Validation error
    
    def test_generate_quiz_invalid_difficulty(self):
        """Test quiz generation with invalid difficulty"""
        request_data = {
            "topic": "Python Programming",
            "num_questions": 5,
            "difficulty": "super_hard"  # Invalid
        }
        
        response = client.post("/generate-quiz", json=request_data)
        assert response.status_code == 422  # Validation error
    
    def test_generate_quiz_empty_topic(self):
        """Test quiz generation with empty topic"""
        request_data = {
            "topic": "",
            "num_questions": 5,
            "difficulty": "medium"
        }
        
        response = client.post("/generate-quiz", json=request_data)
        assert response.status_code == 422  # Validation error
    
    def test_generate_quiz_wikipedia_error(self):
        """Test handling of Wikipedia errors"""
        request_data = {
            "topic": "NonexistentTopic123456",
            "num_questions": 5,
            "difficulty": "medium"
        }
        
        with patch('services.wikipedia_service.get_article_summary') as mock_wiki:
            mock_wiki.side_effect = WikipediaException("Article not found")
            
            response = client.post("/generate-quiz", json=request_data)
            assert response.status_code == 503
            data = response.json()
            assert "detail" in data
    
    def test_generate_quiz_ai_error(self):
        """Test handling of AI service errors"""
        request_data = {
            "topic": "Python Programming",
            "num_questions": 5,
            "difficulty": "medium"
        }
        
        with patch('services.wikipedia_service.get_article_summary') as mock_wiki, \
             patch('services.ai_service.generate_quiz') as mock_ai:
            
            mock_wiki.return_value = "Python is a programming language..."
            mock_ai.side_effect = AIServiceException("AI service unavailable")
            
            response = client.post("/generate-quiz", json=request_data)
            assert response.status_code == 503


class TestRateLimiting:
    """Test rate limiting middleware"""
    
    def test_rate_limit_not_exceeded(self):
        """Test requests within rate limit"""
        for _ in range(5):
            response = client.get("/")
            assert response.status_code == 200
            assert "X-RateLimit-Limit" in response.headers
            assert "X-RateLimit-Remaining" in response.headers


class TestModels:
    """Test Pydantic models"""
    
    def test_quiz_generation_request_validation(self):
        """Test request model validation"""
        # Valid request
        request = QuizGenerationRequest(
            topic="Python",
            num_questions=10,
            difficulty=DifficultyLevel.MEDIUM
        )
        assert request.topic == "Python"
        assert request.num_questions == 10
        
        # Invalid - too many questions
        with pytest.raises(ValueError):
            QuizGenerationRequest(
                topic="Python",
                num_questions=100,
                difficulty=DifficultyLevel.MEDIUM
            )
    
    def test_quiz_question_validation(self):
        """Test quiz question model validation"""
        # Valid question
        question = QuizQuestion(
            question="What is 2+2?",
            options=["1", "2", "3", "4"],
            correct_answer="4"
        )
        assert question.correct_answer in question.options
        
        # Invalid - correct answer not in options
        with pytest.raises(ValueError):
            QuizQuestion(
                question="What is 2+2?",
                options=["1", "2", "3", "5"],
                correct_answer="4"
            )


class TestWikipediaService:
    """Test Wikipedia scraping service"""
    
    def test_scrape_article_success(self):
        """Test successful article scraping"""
        service = WikipediaService()
        
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = """
                <html>
                    <div id="mw-content-text">
                        <p>Python is a programming language.</p>
                        <p>It was created by Guido van Rossum.</p>
                    </div>
                </html>
            """
            mock_get.return_value = mock_response
            
            content = service.scrape_article("Python")
            assert len(content) > 0
            assert "Python" in content or "programming" in content.lower()
    
    def test_scrape_article_not_found(self):
        """Test handling of missing articles"""
        service = WikipediaService()
        
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = Exception("404 Not Found")
            mock_get.return_value = mock_response
            
            with pytest.raises(WikipediaException):
                service.scrape_article("NonexistentArticle12345")


class TestAIService:
    """Test AI service"""
    
    def test_generate_quiz_success(self):
        """Test successful quiz generation"""
        service = AIService()
        
        with patch.object(service.model, 'generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = """
            {
                "questions": [
                    {
                        "question": "What is Python?",
                        "options": ["A snake", "A language", "A tool", "A framework"],
                        "correct_answer": "A language",
                        "explanation": "Python is a programming language"
                    }
                ]
            }
            """
            mock_generate.return_value = mock_response
            
            questions = service.generate_quiz(
                content="Python is a programming language",
                num_questions=1,
                difficulty=DifficultyLevel.MEDIUM,
                topic="Python"
            )
            
            assert len(questions) >= 1
            assert isinstance(questions[0], QuizQuestion)


class TestSecurity:
    """Test security features"""
    
    def test_security_headers_present(self):
        """Test that security headers are added"""
        response = client.get("/")
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
    
    def test_cors_headers_present(self):
        """Test CORS headers are present"""
        response = client.get("/")
        assert "Access-Control-Allow-Origin" in response.headers


class TestErrorHandling:
    """Test error handling"""
    
    def test_404_error(self):
        """Test 404 for non-existent endpoints"""
        response = client.get("/nonexistent")
        assert response.status_code == 404
    
    def test_validation_error_format(self):
        """Test validation error response format"""
        response = client.post("/generate-quiz", json={})
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
