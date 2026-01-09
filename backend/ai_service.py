"""
Enhanced AI service with improved prompts for quiz and related topics generation
"""
import google.generativeai as genai
from typing import List, Dict
import json
import re
import logging
import time
from tenacity import retry, stop_after_attempt, wait_exponential
from config import settings

logger = logging.getLogger(__name__)


class EnhancedAIService:
    """
    Enhanced AI service with optimized prompts and related topics generation
    """
    
    def __init__(self):
        if not settings.google_api_key:
            logger.warning("GOOGLE_API_KEY not set - AI features will not work")
            self.model = None
        else:
            genai.configure(api_key=settings.google_api_key)
            self.model = genai.GenerativeModel(settings.ai_model)
        self.generation_config = {
            "temperature": 0.7,
            "max_output_tokens": 4096,
        }
    
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=4, max=20)
    )
    def generate_comprehensive_quiz(
        self,
        title: str,
        summary: str,
        content: str,
        sections: List[str],
        num_questions: int = 10
    ) -> Dict:
        """
        Generate comprehensive quiz with questions, explanations, and metadata
        
        Returns:
            Dict containing:
            - questions: List of quiz questions
            - related_topics: List of related Wikipedia topics
            - difficulty_distribution: Count by difficulty level
        """
        logger.info(f"Generating comprehensive quiz for: {title}")
        start_time = time.time()
        
        # Check if API key is configured
        if not self.model:
            raise Exception("GOOGLE_API_KEY not configured. Please set it in environment variables.")
        
        try:
            # Generate quiz questions
            questions = self._generate_quiz_questions(
                title, summary, content, sections, num_questions
            )
            
            # Generate related topics
            related_topics = self._generate_related_topics(
                title, summary, content
            )
            
            # Calculate difficulty distribution
            difficulty_dist = {
                "easy": sum(1 for q in questions if q.get("difficulty") == "easy"),
                "medium": sum(1 for q in questions if q.get("difficulty") == "medium"),
                "hard": sum(1 for q in questions if q.get("difficulty") == "hard"),
            }
            
            generation_time = time.time() - start_time
            logger.info(f"Quiz generated successfully in {generation_time:.2f}s")
            
            return {
                "questions": questions,
                "related_topics": related_topics,
                "difficulty_distribution": difficulty_dist,
                "generation_time": generation_time
            }
            
        except Exception as e:
            logger.error(f"Failed to generate quiz: {e}")
            raise Exception(f"AI generation failed: {str(e)}")
    
    def _generate_quiz_questions(
        self,
        title: str,
        summary: str,
        content: str,
        sections: List[str],
        num_questions: int
    ) -> List[Dict]:
        """Generate quiz questions using optimized prompt"""
        
        prompt = self._create_quiz_prompt(title, summary, content, sections, num_questions)
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            questions = self._parse_quiz_response(response.text, sections)
            return questions[:num_questions]
            
        except Exception as e:
            logger.error(f"Failed to generate questions: {e}")
            raise
    
    def _create_quiz_prompt(
        self,
        title: str,
        summary: str,
        content: str,
        sections: List[str],
        num_questions: int
    ) -> str:
        """
        Create optimized prompt for quiz generation with grounding
        """
        
        # Limit content length to fit within token limits
        max_content_length = 5000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
        
        sections_text = ", ".join(sections[:10]) if sections else "N/A"
        
        prompt = f"""You are an expert quiz generator. Create a high-quality educational quiz about "{title}" based STRICTLY on the provided Wikipedia article content.

**CRITICAL INSTRUCTIONS:**
1. ALL questions MUST be directly answerable from the article content provided below
2. DO NOT use external knowledge or make assumptions
3. If you reference a fact, it MUST appear in the article text
4. Include the section name where the information can be found
5. Generate EXACTLY {num_questions} questions with varied difficulty

**ARTICLE INFORMATION:**

**Title:** {title}

**Summary:**
{summary}

**Available Sections:** {sections_text}

**Full Article Content:**
{content}

**QUIZ REQUIREMENTS:**

Generate {num_questions} multiple-choice questions with this distribution:
- {num_questions // 3} EASY questions (basic facts, definitions from early sections)
- {num_questions // 3} MEDIUM questions (requiring understanding and connection of concepts)
- {num_questions - 2 * (num_questions // 3)} HARD questions (requiring analysis, synthesis, or deep comprehension)

**EACH QUESTION MUST INCLUDE:**
1. **question**: Clear, specific question text
2. **options**: Array of exactly 4 options [A, B, C, D]
3. **answer**: The correct option (must be one of the 4 options)
4. **difficulty**: "easy", "medium", or "hard"
5. **explanation**: 1-2 sentence explanation with reference to article section
6. **section**: Which article section this relates to (from sections list above)

**QUALITY STANDARDS:**
- Questions should test different aspects of the topic
- Wrong answers (distractors) should be plausible but clearly incorrect
- Avoid "all of the above" or "none of the above" options
- Avoid trick questions or ambiguous wording
- Ensure factual accuracy by grounding in article text

**OUTPUT FORMAT:**
Return ONLY valid JSON with no markdown formatting or extra text. Ensure all strings are properly escaped and all commas are correctly placed.

{{
  "questions": [
    {{
      "question": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "Option A",
      "difficulty": "easy",
      "explanation": "Brief explanation referencing the article section.",
      "section": "Section name from article"
    }}
  ]
}}

Generate the quiz now in valid JSON format:
        
        return prompt
    
    def _parse_quiz_response(self, response_text: str, sections: List[str]) -> List[Dict]:
        """Parse AI response into structured quiz questions"""
        
        try:
            # Clean the response text
            response_text = response_text.strip()
            
            # Try multiple extraction methods
            json_text = None
            
            # Method 1: Extract from code blocks
            json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1).strip()
            
            # Method 2: Find JSON object
            if not json_text:
                json_match = re.search(r'\{.*?"questions".*?\[.*?\].*?\}', response_text, re.DOTALL)
                if json_match:
                    json_text = json_match.group(0)
            
            # Method 3: Use entire response if it looks like JSON
            if not json_text and response_text.startswith('{'):
                json_text = response_text
            
            if not json_text:
                raise ValueError("No JSON found in response")
            
            # Clean common JSON issues
            json_text = json_text.replace('\n', ' ')
            json_text = re.sub(r',\s*}', '}', json_text)  # Remove trailing commas
            json_text = re.sub(r',\s*]', ']', json_text)  # Remove trailing commas in arrays
            
            data = json.loads(json_text)
            questions = data.get('questions', [])
            
            # Validate and clean questions
            validated_questions = []
            for i, q in enumerate(questions):
                try:
                    # Ensure required fields
                    if not all(key in q for key in ['question', 'options', 'answer', 'difficulty']):
                        logger.warning(f"Skipping question {i+1}: missing required fields")
                        continue
                    
                    # Validate options
                    if len(q['options']) != 4:
                        logger.warning(f"Skipping question {i+1}: must have exactly 4 options")
                        continue
                    
                    # Validate answer is in options
                    if q['answer'] not in q['options']:
                        logger.warning(f"Skipping question {i+1}: answer not in options")
                        continue
                    
                    # Validate difficulty
                    if q['difficulty'] not in ['easy', 'medium', 'hard']:
                        q['difficulty'] = 'medium'  # Default
                    
                    # Ensure section is present
                    if 'section' not in q or not q['section']:
                        # Try to find relevant section
                        q['section'] = sections[0] if sections else "General"
                    
                    # Ensure explanation is present
                    if 'explanation' not in q or not q['explanation']:
                        q['explanation'] = "Based on article content."
                    
                    validated_questions.append(q)
                    
                except Exception as e:
                    logger.warning(f"Error validating question {i+1}: {e}")
                    continue
            
            return validated_questions
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response text: {response_text[:500]}")
            raise Exception("AI response was not valid JSON")
        except Exception as e:
            logger.error(f"Error parsing quiz response: {e}")
            raise
    
    def _generate_related_topics(
        self,
        title: str,
        summary: str,
        content: str
    ) -> List[str]:
        """Generate related Wikipedia topics for further reading"""
        
        prompt = f"""Based on this Wikipedia article about "{title}", suggest 5-8 related Wikipedia topics that would be interesting for further reading.

**Article Summary:**
{summary[:500]}

**Article Content Preview:**
{content[:1000]}

**REQUIREMENTS:**
1. Topics should be directly related to the main article
2. Topics should exist as actual Wikipedia articles (use proper Wikipedia naming)
3. Include a mix of:
   - Broader concepts
   - Related people or events
   - Related technologies or theories
   - Historical context or background
4. Return ONLY a JSON array of topic names

**OUTPUT FORMAT:**
```json
{{
  "related_topics": ["Topic 1", "Topic 2", "Topic 3", "Topic 4", "Topic 5"]
}}
```

Generate the related topics now:"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            # Parse response
            json_match = re.search(r'```json\s*(.*?)\s*```', response.text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)
            else:
                json_match = re.search(r'\{.*"related_topics".*\}', response.text, re.DOTALL)
                if json_match:
                    json_text = json_match.group(0)
                else:
                    json_text = response.text
            
            data = json.loads(json_text)
            related_topics = data.get('related_topics', [])
            
            # Validate and clean
            related_topics = [t.strip() for t in related_topics if isinstance(t, str) and len(t.strip()) > 2]
            
            return related_topics[:8]  # Limit to 8 topics
            
        except Exception as e:
            logger.warning(f"Failed to generate related topics: {e}")
            # Return empty list on failure
            return []


# Create service instance
enhanced_ai_service = EnhancedAIService()
