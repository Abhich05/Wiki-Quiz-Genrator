# 🧠 Wiki Quiz Generator - AI-Powered Learning Platform

**Generate unlimited quizzes from any Wikipedia article using Google Gemini AI!**

![Status](https://img.shields.io/badge/status-production--ready-success)
![AI](https://img.shields.io/badge/AI-Google%20Gemini%202.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Features

- 🤖 **Google Gemini 2.0 Flash AI** - State-of-the-art question generation
- 📚 **Wikipedia Integration** - Use any Wikipedia article
- 🎯 **3 Difficulty Levels** - Easy, Medium, Hard
- 📊 **1-20 Questions** - Customize quiz length
- 💡 **Detailed Explanations** - Learn from each question
- 🎨 **Beautiful UI** - Modern, responsive design
- ⚡ **Real-time Scoring** - Instant feedback
- 🌐 **RESTful API** - Easy integration

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Google API Key ([Get it free](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone or Download** this repository

2. **Install Dependencies**
```bash
cd backend
pip install -r requirements_prod.txt
```

3. **Configure Environment**

Create `backend/.env` file:
```env
GOOGLE_API_KEY=your-google-api-key-here
PORT=8000
HOST=127.0.0.1
```

4. **Start the Server**

**Option A: Using Scripts**
- Windows: Double-click `start_production.bat`
- PowerShell: `.\start_production.ps1`

**Option B: Manual**
```bash
cd backend
python main.py
```

5. **Open Frontend**

Double-click `frontend/app.html` or open in browser.

---

## 📖 Usage

### Via Web Interface

1. **Open** `frontend/app.html` in your browser
2. **Enter** any Wikipedia URL (e.g., `https://en.wikipedia.org/wiki/Python_(programming_language)`)
3. **Select** number of questions (1-20)
4. **Choose** difficulty level (Easy/Medium/Hard)
5. **Click** "Generate Quiz with AI"
6. **Take the quiz** and see your score!

### Via API

```bash
curl -X POST "http://localhost:8000/api/v2/articles/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://en.wikipedia.org/wiki/Artificial_intelligence",
    "num_questions": 5,
    "difficulty": "medium"
  }'
```

---

## 📁 Project Structure

```
Wiki Quiz Generator/
├── backend/
│   ├── main.py                  # Production server
│   ├── requirements_prod.txt    # Dependencies
│   ├── .env                     # Configuration
│   └── test_*.py               # Test scripts
├── frontend/
│   └── app.html                 # Production frontend
├── start_production.bat         # Windows launcher
├── start_production.ps1         # PowerShell launcher
├── README.md                    # This file
├── README_DEPLOY.md            # Deployment guide
└── PRODUCTION_READY.md         # Production checklist
```

---

## 🎮 Example Quizzes

Try these Wikipedia articles:
- Python Programming: `/wiki/Python_(programming_language)`
- Artificial Intelligence: `/wiki/Artificial_intelligence`
- Quantum Computing: `/wiki/Quantum_computing`
- Machine Learning: `/wiki/Machine_learning`
- Climate Change: `/wiki/Climate_change`
- History of Internet: `/wiki/History_of_the_Internet`

---

## 🔧 API Documentation

### Endpoints

#### Health Check
```http
GET /
```

#### Generate Quiz
```http
POST /api/v2/articles/generate
Content-Type: application/json

{
  "url": "https://en.wikipedia.org/wiki/Topic",
  "num_questions": 5,
  "difficulty": "medium"
}
```

#### Get Quiz
```http
GET /api/v2/quizzes/{quiz_id}
```

#### List Quizzes
```http
GET /api/v2/quizzes
```

### Interactive Docs

Visit `http://localhost:8000/docs` when server is running for Swagger UI.

---

## 🚢 Deployment

### Local Development
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Production Deployment

#### Option 1: Render.com
1. Push to GitHub
2. Create Web Service on Render
3. Set start command: `cd backend && python main.py`
4. Add `GOOGLE_API_KEY` environment variable
5. Deploy!

#### Option 2: Railway.app
1. Connect GitHub repository
2. Set root directory: `backend`
3. Add environment variables
4. Auto-deploy

#### Option 3: Docker
```bash
cd backend
docker build -t wiki-quiz .
docker run -p 8000:8000 --env-file .env wiki-quiz
```

See [README_DEPLOY.md](README_DEPLOY.md) for detailed deployment instructions.

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_API_KEY` | ✅ Yes | - | Google Gemini API key |
| `PORT` | No | 8000 | Server port |
| `HOST` | No | 127.0.0.1 | Server host |

### Frontend Configuration

Update `API_BASE` in `frontend/app.html` (line 212) for production:
```javascript
const API_BASE = 'https://your-api-domain.com';
```

---

## 🧪 Testing

### Test Setup
```bash
cd backend
python test_setup.py
```

### Test Full AI Generation
```bash
python test_gemini_full.py
```

### Test Wikipedia Scraping
```bash
python test_scraping.py
```

---

## 📊 Performance

- **Generation Time:** 10-20 seconds per quiz
- **Concurrent Users:** Supports multiple simultaneous users
- **Storage:** In-memory (can add database)
- **Rate Limits:** None (add for public deployment)

---

## 🔒 Security

For production deployment:
- ✅ Use HTTPS
- ✅ Add rate limiting
- ✅ Implement authentication
- ✅ Validate all inputs
- ✅ Use environment variables
- ✅ Enable CORS only for trusted domains

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Google Gemini AI** - Question generation
- **Beautiful Soup** - Wikipedia scraping
- **Pydantic** - Data validation

### Frontend
- **Vanilla JavaScript** - No framework needed
- **Tailwind CSS** - Utility-first styling
- **HTML5** - Semantic markup

---

## 📈 Future Enhancements

- [ ] Database integration (PostgreSQL)
- [ ] User accounts & authentication
- [ ] Quiz sharing capabilities
- [ ] Leaderboards & competitions
- [ ] Multi-language support
- [ ] Mobile app (React Native)
- [ ] PDF export
- [ ] Analytics dashboard
- [ ] More AI model options
- [ ] Custom quiz templates

---

## 🐛 Troubleshooting

### Server Won't Start
- Check Python version: `python --version` (need 3.11+)
- Install dependencies: `pip install -r requirements_prod.txt`
- Verify .env file exists with valid `GOOGLE_API_KEY`

### "AI service not available"
- Check `GOOGLE_API_KEY` is set in `.env`
- Verify API key is valid at https://makersuite.google.com
- Run `python test_setup.py` to verify configuration

### Frontend Can't Connect
- Ensure server is running on http://localhost:8000
- Check browser console (F12) for errors
- Verify `API_BASE` URL in `app.html`

### Quiz Generation Fails
- Try a different Wikipedia article
- Check article URL is valid
- Some Wikipedia pages may not work (redirects, disambiguation)

---

## 📝 License

MIT License - feel free to use this project for learning or commercial purposes!

---

## 🙏 Acknowledgments

- **Google Gemini AI** - Powering intelligent question generation
- **Wikipedia** - The free encyclopedia
- **FastAPI** - Amazing Python framework
- **Tailwind CSS** - Beautiful styling made easy

---

## 📞 Support

### Having Issues?

1. Check [PRODUCTION_READY.md](PRODUCTION_READY.md) for setup verification
2. Review [README_DEPLOY.md](README_DEPLOY.md) for deployment help
3. Run `python backend/test_setup.py` to verify configuration
4. Check server logs in terminal
5. Inspect browser console (F12)

---

## 🎉 Success Stories

Generate quizzes on:
- 🐍 **Python Programming** - Learn coding concepts
- 🤖 **Artificial Intelligence** - Master AI fundamentals
- ⚛️ **Quantum Physics** - Understand the quantum world
- 🌍 **World History** - Test historical knowledge
- 🧬 **Biology** - Study life sciences
- 🎨 **Art History** - Explore artistic movements

**Any topic on Wikipedia = Instant quiz!**

---

## 🚀 Get Started Now!

1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements_prod.txt
   ```

2. **Add your Google API key** to `backend/.env`

3. **Start the server:**
   ```bash
   python main.py
   ```

4. **Open** `frontend/app.html` in your browser

5. **Generate your first AI-powered quiz!** 🎯

---

**Made with ❤️ using Google Gemini AI & Wikipedia**

*Start learning smarter, not harder!* 📚✨
