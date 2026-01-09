"""
Enhanced services with retry logic, circuit breakers, and comprehensive error handling
"""
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from typing import Optional, List, Dict
import logging
import time
import json
import re
from functools import wraps
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from config import settings
from models import QuizQuestion, DifficultyLevel

logger = logging.getLogger(__name__)


class ServiceException(Exception):
    """Base exception for service errors"""
    pass


class WikipediaException(ServiceException):
    """Wikipedia scraping errors"""
    pass


class AIServiceException(ServiceException):
    """AI service errors"""
    pass


class CircuitBreaker:
    """Simple circuit breaker pattern implementation"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half-open
    
    def call(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.state == "open":
                if time.time() - self.last_failure_time < self.timeout:
                    raise ServiceException("Circuit breaker is OPEN")
                else:
                    self.state = "half-open"
            
            try:
                result = func(*args, **kwargs)
                if self.state == "half-open":
                    self.state = "closed"
                    self.failure_count = 0
                return result
            except Exception as e:
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                if self.failure_count >= self.failure_threshold:
                    self.state = "open"
                    logger.error(f"Circuit breaker OPENED after {self.failure_count} failures")
                
                raise
        
        return wrapper


# Initialize circuit breakers
wikipedia_circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)
ai_circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=120)


class WikipediaService:
    """Enhanced Wikipedia scraping service with retry logic"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': settings.wikipedia_user_agent
        })
        self.timeout = settings.wikipedia_timeout
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.RequestException, WikipediaException))
    )
    @wikipedia_circuit_breaker.call
    def scrape_article(self, topic: str) -> str:
        """
        Scrape Wikipedia article with retry logic and circuit breaker
        
        Args:
            topic: Wikipedia topic or URL
            
        Returns:
            Article content as text
            
        Raises:
            WikipediaException: If scraping fails
        """
        logger.info(f"Scraping Wikipedia for topic: {topic}")
        
        try:
            # Convert topic to Wikipedia URL if needed
            if topic.startswith('http'):
                url = topic
            else:
                # Clean topic and create URL
                clean_topic = topic.strip().replace(' ', '_')
                url = f"https://en.wikipedia.org/wiki/{clean_topic}"
            
            logger.debug(f"Fetching URL: {url}")
            
            # Make request
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            
            # Get main content
            content = soup.find('div', {'id': 'mw-content-text'})
            if not content:
                raise WikipediaException("Could not find article content")
            
            # Extract paragraphs
            paragraphs = content.find_all('p')
            text = '\n\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
            
            # Clean text
            text = re.sub(r'\[\d+\]', '', text)  # Remove citation numbers
            text = re.sub(r'\s+', ' ', text)     # Normalize whitespace
            text = text.strip()
            
            if len(text) < 100:
                raise WikipediaException("Article content too short or empty")
            
            logger.info(f"Successfully scraped {len(text)} characters")
            return text
            
        except requests.RequestException as e:
            logger.error(f"Wikipedia request failed: {e}")
            raise WikipediaException(f"Failed to fetch Wikipedia article: {str(e)}")
        except Exception as e:
            logger.error(f"Wikipedia scraping error: {e}")
            raise WikipediaException(f"Error processing Wikipedia content: {str(e)}")
    
    def get_article_summary(self, topic: str, max_length: int = 2000) -> str:
        """Get a summary of the article for AI processing"""
        full_text = self.scrape_article(topic)
        
        # Limit text length to avoid AI token limits
        if len(full_text) > max_length:
            # Try to split at sentence boundaries
            sentences = full_text[:max_length].split('. ')
            return '. '.join(sentences[:-1]) + '.'
        
        return full_text


class AIService:
    """Enhanced AI service with circuit breaker and comprehensive error handling"""
    
    def __init__(self):
        genai.configure(api_key=settings.google_api_key)
        self.model = genai.GenerativeModel(settings.ai_model)
        self.generation_config = {
            "temperature": settings.ai_temperature,
            "max_output_tokens": settings.ai_max_tokens,
        }
    
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=4, max=20),
        retry=retry_if_exception_type(AIServiceException)
    )
    @ai_circuit_breaker.call
    def generate_quiz(
        self,
        content: str,
        num_questions: int,
        difficulty: DifficultyLevel,
        topic: str
    ) -> List[QuizQuestion]:
        """
        Generate quiz questions using AI with enhanced error handling
        
        Args:
            content: Wikipedia article content
            num_questions: Number of questions to generate
            difficulty: Quiz difficulty level
            topic: Topic name for context
            
        Returns:
            List of QuizQuestion objects
            
        Raises:
            AIServiceException: If AI generation fails
        """
        logger.info(f"Generating {num_questions} {difficulty} questions about {topic}")
        
        try:
            # Create enhanced prompt
            prompt = self._create_prompt(content, num_questions, difficulty, topic)
            
            # Generate content
            start_time = time.time()
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            duration = time.time() - start_time
            
            logger.info(f"AI generation completed in {duration:.2f}s")
            
            # Parse response
            questions = self._parse_response(response.text, difficulty)
            
            # Validate we got enough questions
            if len(questions) < num_questions * 0.8:  # Allow 20% tolerance
                logger.warning(f"Only generated {len(questions)} of {num_questions} requested questions")
            
            return questions[:num_questions]
            
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            raise AIServiceException(f"Failed to generate quiz: {str(e)}")
    
    def _create_prompt(
        self,
        content: str,
        num_questions: int,
        difficulty: DifficultyLevel,
        topic: str
    ) -> str:
        """Create an optimized prompt for quiz generation"""
        
        difficulty_instructions = {
            DifficultyLevel.EASY: "basic facts, definitions, and simple concepts that can be understood by beginners",
            DifficultyLevel.MEDIUM: "moderate understanding requiring some analysis and connection of concepts",
            DifficultyLevel.HARD: "deep understanding, critical thinking, complex analysis, and expert-level knowledge"
        }
        
        prompt = f"""You are an expert quiz generator. Create {num_questions} high-quality multiple-choice questions about {topic}.

CONTENT TO USE:
{content[:3000]}

REQUIREMENTS:
1. Generate EXACTLY {num_questions} questions
2. Difficulty: {difficulty.value} - Focus on {difficulty_instructions[difficulty]}
3. Each question must have:
   - A clear, specific question
   - Exactly 4 answer options (A, B, C, D)
   - Only ONE correct answer
   - An optional brief explanation (1-2 sentences)

4. Questions should:
   - Be based solely on the provided content
   - Test different aspects of the topic
   - Avoid trick questions or ambiguity
   - Have plausible wrong answers (distractors)

OUTPUT FORMAT (JSON):
{{
  "questions": [
    {{
      "question": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option A",
      "explanation": "Brief explanation why Option A is correct"
    }}
  ]
}}

Generate the quiz now:"""
        
        return prompt
    
    def _parse_response(self, response_text: str, difficulty: DifficultyLevel) -> List[QuizQuestion]:
        """Parse AI response into QuizQuestion objects"""
        
        try:
            # Try to extract JSON from response
            # Sometimes AI wraps JSON in markdown code blocks
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)
            else:
                # Try to find JSON object directly
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_text = json_match.group(0)
                else:
                    json_text = response_text
            
            # Parse JSON
            data = json.loads(json_text)
            
            # Extract questions
            questions_data = data.get('questions', [])
            
            questions = []
            for q_data in questions_data:
                try:
                    question = QuizQuestion(
                        question=q_data['question'],
                        options=q_data['options'],
                        correct_answer=q_data['correct_answer'],
                        explanation=q_data.get('explanation'),
                        difficulty=difficulty
                    )
                    questions.append(question)
                except Exception as e:
                    logger.warning(f"Skipping invalid question: {e}")
                    continue
            
            return questions
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response text: {response_text[:500]}")
            raise AIServiceException("AI response was not valid JSON")
        except KeyError as e:
            logger.error(f"Missing required field in response: {e}")
            raise AIServiceException(f"AI response missing required field: {e}")


# Create service instances
wikipedia_service = WikipediaService()
ai_service = AIService()
