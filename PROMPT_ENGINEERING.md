# Prompt Engineering Documentation

This document details the prompt templates and strategies used in the Wikipedia Quiz Generator to ensure high-quality, grounded quiz generation.

## Core Principles

### 1. Grounding
All prompts explicitly instruct the AI to use ONLY information from the provided article content. This prevents hallucination and ensures factual accuracy.

### 2. Section References
Questions must cite which section of the article they come from, enabling verification and helping users locate information.

### 3. Structured Output
Prompts request JSON-formatted responses with strict schemas, making parsing reliable and consistent.

### 4. Difficulty Distribution
Prompts explicitly request a mix of Easy, Medium, and Hard questions to create engaging quizzes for different skill levels.

## Main Quiz Generation Prompt

**Location**: `backend/ai_service.py` → `_create_quiz_prompt()`

```python
prompt = f"""
Generate {num_questions} multiple-choice quiz questions based on the following Wikipedia article.

CRITICAL REQUIREMENTS:
1. ALL questions MUST be directly answerable from the article content below
2. DO NOT use external knowledge or information not in the article
3. Each question must reference which section it comes from
4. Generate questions of varying difficulty (Easy, Medium, Hard)
5. Ensure questions test understanding, not just memorization
6. Each question should have exactly 4 distinct options (A, B, C, D)
7. Include a clear explanation for why the correct answer is right

Article Title: {title}

Article Sections (for reference):
{section_list}

Full Article Content:
{content}

DIFFICULTY GUIDELINES:
- Easy: Basic facts, definitions, direct quotes (Who, What, When)
- Medium: Requires understanding relationships, causes, effects (How, Why)
- Hard: Requires synthesis, comparison, or analysis across multiple sections

OUTPUT FORMAT:
Return a JSON array of question objects with this exact structure:
[
  {{
    "question": "Your question text here?",
    "option_a": "First option",
    "option_b": "Second option",
    "option_c": "Third option",
    "option_d": "Fourth option",
    "correct_answer": "A" | "B" | "C" | "D",
    "explanation": "Detailed explanation citing the article section",
    "difficulty": "Easy" | "Medium" | "Hard",
    "section_reference": "Section name from the article"
  }}
]

IMPORTANT:
- Make questions specific and unambiguous
- Ensure all four options are plausible but only one is correct
- Explanations should help users learn, not just state the answer
- Section references must match actual section names from the list above
- Aim for roughly: 30% Easy, 50% Medium, 20% Hard questions
"""
```

### Prompt Analysis

**Strengths:**
1. **Clear Constraints**: Numbered requirements make expectations explicit
2. **Context Provision**: Includes both section list and full content
3. **Difficulty Framework**: Provides concrete guidelines for each level
4. **Output Schema**: Exact JSON structure prevents parsing errors
5. **Educational Focus**: Emphasizes learning value in explanations

**Key Phrases:**
- "MUST be directly answerable" - Strong imperative language
- "DO NOT use external knowledge" - Explicit boundary setting
- "Reference which section" - Enforces source attribution
- "Plausible but only one is correct" - Quality control for options

## Related Topics Generation Prompt

**Location**: `backend/ai_service.py` → `_generate_related_topics()`

```python
prompt = f"""
Based on the Wikipedia article about "{title}", suggest 5-8 related topics that would be interesting to explore next.

Requirements:
1. Topics should be genuinely related to the main article
2. Suggest topics that would help someone learn more about the subject
3. Each topic should be a valid Wikipedia article title
4. Focus on concepts, people, or events mentioned in the article
5. Provide a diverse set of topics (not all the same type)

Article summary:
{summary}

Key concepts from the article:
{key_concepts}

Return ONLY a JSON array of topic names (strings), like:
["Topic 1", "Topic 2", "Topic 3", ...]

Do not include explanations, just the topic names.
"""
```

### Prompt Analysis

**Strengths:**
1. **Targeted Output**: Simple JSON array format
2. **Quality Criteria**: "genuinely related" and "help someone learn"
3. **Practical Constraint**: Must be valid Wikipedia titles
4. **Diversity Instruction**: Prevents repetitive suggestions

## Entity Extraction Strategy

**Location**: `backend/wikipedia_service.py` → `_extract_entities()`

### Approach: Heuristic-Based Classification

The system uses Wikipedia's link structure and text patterns to classify entities:

```python
# People Detection Heuristics:
- Links containing birth/death year patterns: "(1879–1955)"
- Links containing "born" or "died" in nearby text
- Common name patterns with biographical indicators

# Organization Detection Heuristics:
- Keywords: "University", "Institute", "Corporation", "Organization"
- Keywords: "Company", "Foundation", "Association", "Society"
- Proper nouns with organizational indicators

# Location Detection Heuristics:
- Country names (from predefined list)
- City names (major global cities)
- Geographic terms: "Region", "Province", "State"
- Links to geography-related Wikipedia categories
```

### Why Heuristics Instead of NLP Models?

1. **Speed**: Pattern matching is faster than loading spaCy models
2. **Accuracy**: Wikipedia's structured data (infoboxes, links) is highly reliable
3. **Simplicity**: No model dependencies, easier deployment
4. **Transparency**: Heuristics are explainable and debuggable

### Trade-offs

**Pros:**
- Very fast processing
- No external model dependencies
- High precision (few false positives)
- Works well with Wikipedia's structure

**Cons:**
- May miss entities without Wikipedia links
- Requires Wikipedia-specific patterns
- Lower recall than trained NER models

## Prompt Optimization Strategies

### 1. Temperature Setting

```python
model = genai.GenerativeModel('gemini-2.0-flash-exp')
response = model.generate_content(
    prompt,
    generation_config={
        'temperature': 0.3,  # Lower = more focused, deterministic
        'top_p': 0.8,
        'top_k': 40,
        'max_output_tokens': 4096,
    }
)
```

**Rationale:**
- **Temperature 0.3**: Reduces randomness for factual questions
- **Top-p 0.8**: Balances diversity with quality
- **Top-k 40**: Limits to most probable tokens
- **Max tokens 4096**: Allows for 10+ detailed questions

### 2. Few-Shot Learning (Implicit)

The prompt includes example JSON structure, which acts as implicit few-shot guidance:

```json
[
  {
    "question": "Your question text here?",
    "option_a": "First option",
    ...
  }
]
```

This shows the model the exact output format without needing explicit training examples.

### 3. Chain-of-Thought (in Explanations)

Explanations are prompted to be "detailed" and "cite the article section", encouraging the model to:
1. Identify the correct answer
2. Locate supporting information
3. Explain the reasoning
4. Reference the source

Example output:
```
"explanation": "John McCarthy coined the term 'artificial intelligence' at 
the Dartmouth Conference in 1956, where he organized a summer research project 
that is considered the birth of AI as a field. This information is found in 
the 'History' section of the article."
```

## Error Handling and Validation

### Response Validation

```python
def validate_quiz_response(questions):
    """Validate AI-generated quiz questions"""
    required_fields = [
        'question', 'option_a', 'option_b', 'option_c', 'option_d',
        'correct_answer', 'explanation', 'difficulty', 'section_reference'
    ]
    
    for q in questions:
        # Check all fields present
        if not all(field in q for field in required_fields):
            raise ValueError("Missing required field")
        
        # Validate correct_answer is A, B, C, or D
        if q['correct_answer'] not in ['A', 'B', 'C', 'D']:
            raise ValueError("Invalid correct_answer")
        
        # Validate difficulty
        if q['difficulty'] not in ['Easy', 'Medium', 'Hard']:
            raise ValueError("Invalid difficulty")
    
    return True
```

### Retry Logic

```python
max_retries = 3
for attempt in range(max_retries):
    try:
        response = model.generate_content(prompt)
        questions = json.loads(response.text)
        validate_quiz_response(questions)
        return questions
    except Exception as e:
        if attempt == max_retries - 1:
            raise
        continue
```

## Prompt Evolution

### Version 1 (Initial)
```
Generate quiz questions from this article.
```
**Problems:**
- Hallucinated facts not in article
- Inconsistent output format
- No difficulty variation

### Version 2 (With Constraints)
```
Generate quiz questions based ONLY on the following article.
Do not use external information.
Return as JSON.
```
**Improvements:**
- Reduced hallucination
- Structured output
**Remaining Issues:**
- Vague difficulty levels
- No source attribution

### Version 3 (Current)
```
Generate {n} questions based on the following Wikipedia article.

CRITICAL REQUIREMENTS:
1. ALL questions MUST be directly answerable from the article content
2. DO NOT use external knowledge
3. Each question must reference which section it comes from
4. Generate questions of varying difficulty (Easy, Medium, Hard)
...
```
**Improvements:**
- Strong imperative language
- Section references for verification
- Clear difficulty guidelines
- Detailed output schema

## Best Practices for Quiz Generation Prompts

### 1. Use Strong Imperatives
❌ "Try to only use article content"
✅ "ALL questions MUST be directly answerable from the article content"

### 2. Provide Examples
❌ "Return as JSON"
✅ "Return a JSON array with this exact structure: [{ ... }]"

### 3. Define Success Criteria
❌ "Make good questions"
✅ "Ensure questions test understanding, not just memorization"

### 4. Request Self-Documentation
❌ "Generate questions"
✅ "Each question must reference which section it comes from"

### 5. Balance Creativity and Constraint
- Allow: Question phrasing, distractor options, explanation style
- Constrain: Facts, structure, source attribution

## Evaluation Metrics

### Automatic Checks
1. **Grounding**: All answers must be in article (keyword matching)
2. **Structure**: JSON validation against schema
3. **Completeness**: All required fields present
4. **Difficulty Distribution**: Count of Easy/Medium/Hard

### Manual Checks (for sample data)
1. **Factual Accuracy**: Are facts correct per Wikipedia?
2. **Question Quality**: Clear, unambiguous, educational?
3. **Option Quality**: Plausible distractors, clear correct answer?
4. **Explanation Quality**: Helpful, references article, educational?

## Future Improvements

### 1. Dynamic Difficulty Adjustment
Based on article complexity, adjust target distribution:
- Simple articles: More Easy questions
- Complex articles: More Medium/Hard questions

### 2. Question Type Diversity
Currently all multiple-choice. Could add:
- True/False
- Fill-in-the-blank
- Matching
- Ordering

### 3. Adaptive Prompting
Analyze article type and adjust prompt:
- Biographical: Focus on timeline, achievements
- Scientific: Focus on concepts, applications
- Historical: Focus on causes, effects, key figures

### 4. Multi-Step Verification
1. Generate questions
2. Generate answers separately
3. Cross-check consistency
4. Request evidence for each answer

## Conclusion

The prompt engineering strategy for this project prioritizes:
1. **Factual Grounding** - Prevent hallucination
2. **Source Attribution** - Enable verification
3. **Structured Output** - Ensure reliability
4. **Educational Value** - Create learning opportunities

These principles, combined with careful heuristic design for entity extraction, create a robust system for automated quiz generation from Wikipedia content.
