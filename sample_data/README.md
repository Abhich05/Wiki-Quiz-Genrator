# Sample Test Cases for Wikipedia Quiz Generator

This folder contains sample Wikipedia URLs and expected API outputs for testing the quiz generation system.

## Test Cases

### 1. Technology Article
**URL**: https://en.wikipedia.org/wiki/Python_(programming_language)
**Expected Features**:
- People: Guido van Rossum
- Organizations: Python Software Foundation, Google
- Locations: Netherlands
- Sections: History, Design philosophy, Syntax, Libraries
- Difficulty: Mix of Easy/Medium/Hard

### 2. Historical Event
**URL**: https://en.wikipedia.org/wiki/World_War_II
**Expected Features**:
- People: Adolf Hitler, Winston Churchill, Franklin D. Roosevelt
- Organizations: United Nations, League of Nations
- Locations: Europe, Asia, Pacific, Germany, Japan
- Sections: Causes, Course of war, Consequences
- Difficulty: Mostly Medium/Hard

### 3. Scientific Topic
**URL**: https://en.wikipedia.org/wiki/Artificial_intelligence
**Expected Features**:
- People: Alan Turing, John McCarthy, Marvin Minsky
- Organizations: MIT, Stanford University, DeepMind
- Locations: United States, United Kingdom
- Sections: History, Applications, Ethics, Future
- Difficulty: Mix of all levels

### 4. Biographical Article
**URL**: https://en.wikipedia.org/wiki/Albert_Einstein
**Expected Features**:
- People: Albert Einstein, Max Planck, Niels Bohr
- Organizations: ETH Zurich, Princeton University
- Locations: Germany, Switzerland, United States
- Sections: Early life, Scientific career, Personal life
- Difficulty: Easy/Medium focus

### 5. Environmental Topic
**URL**: https://en.wikipedia.org/wiki/Climate_change
**Expected Features**:
- Organizations: IPCC, NASA, NOAA
- Locations: Global, Arctic, Antarctica
- Sections: Causes, Effects, Mitigation, Adaptation
- Difficulty: Medium/Hard focus

## Testing Checklist

### Entity Extraction Quality
- [ ] People extracted correctly with proper names
- [ ] Organizations identified (universities, companies, institutions)
- [ ] Locations extracted (countries, cities, regions)
- [ ] No false positives (e.g., regular nouns classified as entities)

### Question Quality
- [ ] Questions are answerable from article content
- [ ] No hallucinated information
- [ ] Section references are accurate
- [ ] Options are distinct and plausible
- [ ] Explanations reference article content

### Difficulty Distribution
- [ ] Mix of Easy, Medium, Hard questions
- [ ] Easy: Basic facts (Who, What, When)
- [ ] Medium: Understanding (How, Why)
- [ ] Hard: Analysis, comparison, synthesis

### Related Topics
- [ ] 5-8 related Wikipedia articles suggested
- [ ] Topics are genuinely related
- [ ] Valid Wikipedia article titles

## Expected Response Format

See `sample_ai_response.json` for a complete example API response.

## Running Tests

```bash
# Test Article 1: Python
curl -X POST "http://localhost:8000/api/generate-quiz" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://en.wikipedia.org/wiki/Python_(programming_language)"}'

# Test Article 2: World War II
curl -X POST "http://localhost:8000/api/generate-quiz" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://en.wikipedia.org/wiki/World_War_II"}'

# Test Article 3: AI
curl -X POST "http://localhost:8000/api/generate-quiz" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://en.wikipedia.org/wiki/Artificial_intelligence"}'
```

## Evaluation Criteria

### 1. Prompt Quality (40%)
- Grounding: Questions reference article sections
- No hallucination: All information from article
- Clarity: Questions are unambiguous
- Variety: Different question types (factual, conceptual, analytical)

### 2. Entity Extraction (30%)
- Accuracy: Correct classification (people vs organizations vs locations)
- Coverage: All major entities identified
- Precision: No false positives
- Recall: No major entities missed

### 3. Quiz Quality (30%)
- Answerability: All questions can be answered from article
- Difficulty balance: Appropriate mix of Easy/Medium/Hard
- Explanation quality: Clear, references article content
- Options quality: Plausible distractors, clear correct answer
