"""
Test script to verify backend setup and generate a sample quiz.
Run this after setting up the database and environment variables.
"""

import os
import sys
import json
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

def test_environment():
    """Test environment variable configuration"""
    print("=" * 60)
    print("STEP 1: Testing Environment Configuration")
    print("=" * 60)
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GOOGLE_API_KEY')
    db_url = os.getenv('DATABASE_URL')
    
    if not api_key:
        print("❌ GOOGLE_API_KEY not set in .env file")
        return False
    else:
        masked_key = api_key[:10] + "..." + api_key[-4:]
        print(f"✅ GOOGLE_API_KEY found: {masked_key}")
    
    if not db_url:
        print("⚠️  DATABASE_URL not set, will use SQLite default")
    else:
        # Mask password in URL
        if '@' in db_url:
            parts = db_url.split('@')
            user_pass = parts[0].split('//')[-1]
            if ':' in user_pass:
                user = user_pass.split(':')[0]
                masked = f"postgresql://{user}:****@{parts[1]}"
            else:
                masked = db_url
        else:
            masked = db_url
        print(f"✅ DATABASE_URL found: {masked}")
    
    print()
    return True

def test_imports():
    """Test that all required packages are installed"""
    print("=" * 60)
    print("STEP 2: Testing Package Imports")
    print("=" * 60)
    
    required_packages = [
        ('fastapi', 'FastAPI'),
        ('sqlalchemy', 'SQLAlchemy'),
        ('google.generativeai', 'Google Generative AI'),
        ('bs4', 'BeautifulSoup4'),
        ('requests', 'Requests'),
        ('pydantic', 'Pydantic'),
    ]
    
    all_imported = True
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"✅ {name} imported successfully")
        except ImportError:
            print(f"❌ {name} not installed. Run: pip install {package}")
            all_imported = False
    
    print()
    return all_imported

def test_database():
    """Test database connection and table creation"""
    print("=" * 60)
    print("STEP 3: Testing Database Connection")
    print("=" * 60)
    
    try:
        from database import engine, init_db
        from sqlalchemy import inspect
        
        # Initialize database
        init_db()
        print("✅ Database initialized successfully")
        
        # Check if tables exist
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = ['wiki_articles', 'quizzes', 'quiz_questions', 'quiz_attempts']
        for table in expected_tables:
            if table in tables:
                print(f"✅ Table '{table}' created")
            else:
                print(f"❌ Table '{table}' not found")
                return False
        
        print()
        return True
    except Exception as e:
        print(f"❌ Database error: {str(e)}")
        print()
        return False

def test_wikipedia_scraping():
    """Test Wikipedia scraping functionality"""
    print("=" * 60)
    print("STEP 4: Testing Wikipedia Scraping")
    print("=" * 60)
    
    try:
        from wikipedia_service import WikipediaService
        
        service = WikipediaService()
        test_url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
        
        print(f"Scraping: {test_url}")
        print("This may take 10-20 seconds...")
        
        data = service.scrape_full_article(test_url)
        
        print(f"✅ Successfully scraped article")
        print(f"   Title: {data['title']}")
        print(f"   Summary length: {len(data['summary'])} characters")
        print(f"   Content length: {len(data['content'])} characters")
        print(f"   People found: {len(data['key_entities']['people'])}")
        print(f"   Organizations found: {len(data['key_entities']['organizations'])}")
        print(f"   Locations found: {len(data['key_entities']['locations'])}")
        print(f"   Sections found: {len(data['sections'])}")
        
        # Show sample entities
        if data['key_entities']['people']:
            print(f"   Sample people: {', '.join(data['key_entities']['people'][:3])}")
        if data['key_entities']['organizations']:
            print(f"   Sample organizations: {', '.join(data['key_entities']['organizations'][:3])}")
        
        print()
        return True, data
    except Exception as e:
        print(f"❌ Scraping error: {str(e)}")
        print()
        return False, None

def test_ai_generation(article_data):
    """Test AI quiz generation"""
    print("=" * 60)
    print("STEP 5: Testing AI Quiz Generation")
    print("=" * 60)
    
    try:
        from ai_service import AIService
        
        service = AIService()
        
        print(f"Generating quiz for: {article_data['title']}")
        print("This may take 20-40 seconds...")
        
        quiz_data = service.generate_comprehensive_quiz(
            title=article_data['title'],
            content=article_data['content'][:5000],  # First 5000 chars for testing
            sections=article_data['sections'],
            num_questions=5  # Just 5 for testing
        )
        
        print(f"✅ Successfully generated quiz")
        print(f"   Questions generated: {len(quiz_data['questions'])}")
        print(f"   Difficulty distribution:")
        for difficulty, count in quiz_data['difficulty_distribution'].items():
            print(f"      {difficulty}: {count}")
        print(f"   Related topics: {len(quiz_data['related_topics'])}")
        
        # Show sample question
        if quiz_data['questions']:
            q = quiz_data['questions'][0]
            print(f"\n   Sample question:")
            print(f"   Q: {q['question']}")
            print(f"   A: {q['option_a']}")
            print(f"   B: {q['option_b']}")
            print(f"   C: {q['option_c']}")
            print(f"   D: {q['option_d']}")
            print(f"   Correct: {q['correct_answer']}")
            print(f"   Difficulty: {q['difficulty']}")
            print(f"   Section: {q['section_reference']}")
        
        print()
        return True
    except Exception as e:
        print(f"❌ AI generation error: {str(e)}")
        import traceback
        traceback.print_exc()
        print()
        return False

def test_api_integration():
    """Test complete API workflow"""
    print("=" * 60)
    print("STEP 6: Testing Complete API Workflow")
    print("=" * 60)
    
    try:
        from database import get_db
        from db_models import WikiArticle, Quiz
        
        db = next(get_db())
        
        # Check if any articles exist
        article_count = db.query(WikiArticle).count()
        quiz_count = db.query(Quiz).count()
        
        print(f"✅ Database query successful")
        print(f"   Articles in database: {article_count}")
        print(f"   Quizzes in database: {quiz_count}")
        
        if article_count > 0:
            latest_article = db.query(WikiArticle).order_by(WikiArticle.id.desc()).first()
            print(f"   Latest article: {latest_article.title}")
        
        if quiz_count > 0:
            latest_quiz = db.query(Quiz).order_by(Quiz.id.desc()).first()
            print(f"   Latest quiz: {latest_quiz.total_questions} questions")
        
        print()
        return True
    except Exception as e:
        print(f"❌ API integration error: {str(e)}")
        print()
        return False

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "Wikipedia Quiz Generator - Setup Test" + " " * 10 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    results = []
    
    # Step 1: Environment
    results.append(("Environment", test_environment()))
    
    # Step 2: Imports
    if results[-1][1]:
        results.append(("Package Imports", test_imports()))
    else:
        print("⚠️  Skipping remaining tests due to environment issues\n")
        return
    
    # Step 3: Database
    if results[-1][1]:
        results.append(("Database", test_database()))
    else:
        print("⚠️  Skipping remaining tests due to import issues\n")
        return
    
    # Step 4: Wikipedia Scraping
    if results[-1][1]:
        scraping_success, article_data = test_wikipedia_scraping()
        results.append(("Wikipedia Scraping", scraping_success))
    else:
        print("⚠️  Skipping remaining tests due to database issues\n")
        return
    
    # Step 5: AI Generation
    if results[-1][1] and article_data:
        results.append(("AI Generation", test_ai_generation(article_data)))
    else:
        print("⚠️  Skipping AI test due to scraping issues\n")
    
    # Step 6: API Integration
    if any(r[1] for r in results):
        results.append(("API Integration", test_api_integration()))
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(r[1] for r in results)
    
    print()
    if all_passed:
        print("🎉 All tests passed! Backend is ready to use.")
        print()
        print("Next steps:")
        print("1. Run the backend server:")
        print("   uvicorn main_complete:app --reload")
        print()
        print("2. Open frontend in browser:")
        print("   Open frontend/index_enhanced.html")
        print()
        print("3. Try generating a quiz!")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print()
        print("Common solutions:")
        print("- Install missing packages: pip install -r requirements_full.txt")
        print("- Check .env file has GOOGLE_API_KEY set")
        print("- Verify database connection in DATABASE_URL")
    
    print()

if __name__ == "__main__":
    main()
