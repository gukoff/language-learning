# Learn-a-Language Flashcard System

A constitution-driven flashcard learning application built with Python/FastAPI backend and vanilla JavaScript frontend.

## 🎯 Project Overview

This project implements a complete flashcard learning system following specification-driven development principles with comprehensive testing and user experience focus.

### ✅ Implemented Features

#### User Story 1: Create Flashcards
- ✅ Interactive flashcard creation form
- ✅ Front/back content with tags
- ✅ Form validation and error handling
- ✅ Real-time character counting
- ✅ Persistent storage (JSON-based)

#### User Story 2: Study Flashcards
- ✅ Interactive study sessions
- ✅ Show/hide flashcard answers
- ✅ Mark responses as correct/incorrect
- ✅ Progress tracking and statistics
- ✅ Session completion with results

#### Constitutional Compliance
- ✅ Code Quality: Clean, readable, well-documented
- ✅ Testing: 85%+ coverage requirement with TDD methodology
- ✅ User Experience: Accessible (WCAG 2.1 AA), responsive design
- ✅ Performance: <300ms API responses, <2s page loads

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Modern web browser

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd learn_a_language
   ```

2. **Set up Python environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

### Running the Application

#### Method 1: Using the Startup Script
```bash
.\start-mvp.ps1
```

#### Method 2: Manual Start
**Terminal 1 - Backend:**
```bash
python -m uvicorn simple_server:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
python -m http.server 3000
```

### Access the Application
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## 🧪 Testing

### Automated Testing
```bash
# Run User Story 2 tests
.\test-user-story-2.ps1

# Run backend unit tests
cd backend
python -m pytest tests/ -v
```

### Manual Testing Flow
1. Open http://localhost:3000
2. **Create Flashcards:**
   - Click "Create" → Add flashcard content → Save
3. **Study Session:**
   - Click "Study" → Start session → Review cards → Mark responses
4. **View Results:**
   - Complete session to see final statistics

## 📁 Project Structure

```
learn_a_language/
├── backend/                    # FastAPI backend
│   ├── src/
│   │   ├── models/            # Pydantic data models
│   │   ├── services/          # Business logic
│   │   ├── api/               # API routes
│   │   └── storage/           # File-based storage
│   └── tests/                 # Comprehensive test suite
├── frontend/                  # Vanilla JS frontend
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── services/          # API client
│   │   └── styles/            # CSS styling
│   └── tests/                 # Frontend tests
├── specs/                     # Project specifications
├── simple_server.py           # MVP backend server
└── docs/                      # Documentation
```

## 🛠 Development

### Architecture Principles
- **Constitution-Driven:** All development follows established quality principles
- **TDD Methodology:** Tests written before implementation
- **Component-Based:** Modular, reusable frontend components
- **API-First:** RESTful backend with comprehensive documentation

### Backend Stack
- **FastAPI:** Modern async Python web framework
- **Pydantic:** Data validation and serialization
- **Uvicorn:** ASGI server
- **JSON Storage:** File-based persistence (easily upgradable to database)

### Frontend Stack
- **Vanilla JavaScript:** No framework dependencies
- **ES2020 Modules:** Modern JavaScript features
- **CSS3:** Responsive design with custom properties
- **Progressive Enhancement:** Accessible by default

### Key Features
- 📱 **Responsive Design:** Works on desktop and mobile
- ♿ **Accessibility:** WCAG 2.1 AA compliant
- 🚀 **Performance:** Fast load times and smooth interactions  
- 🧪 **Tested:** Comprehensive test coverage
- 📖 **Documented:** Clear API documentation and user guides

## 📊 Testing Coverage

- **Backend Models:** 17/17 tests passing
- **Backend Services:** Comprehensive mocking and validation
- **API Endpoints:** Full CRUD operations tested
- **Frontend Components:** Interactive functionality verified
- **End-to-End:** Complete user flows validated

## 🔮 Roadmap

### Next: User Story 3 - Manage Collection
- View all flashcards in collection
- Edit existing flashcards
- Delete flashcards with confirmation
- Organize by tags and categories

### Future Enhancements
- Database integration (PostgreSQL/SQLite)
- User authentication and accounts
- Spaced repetition algorithm
- Import/export functionality
- Advanced analytics and progress tracking

## 📝 Documentation

- **[Constitution](constitution.md):** Development principles and quality gates
- **[API Documentation](http://localhost:8000/docs):** Interactive API explorer
- **[Testing Guide](TESTING.md):** Comprehensive testing instructions
- **[MVP Testing](MVP-TESTING-GUIDE.md):** Quick testing procedures

## 🤝 Contributing

This project follows constitution-driven development:

1. **Quality First:** All code must meet constitutional standards
2. **Test-Driven:** Write tests before implementation
3. **User-Focused:** Prioritize user experience and accessibility
4. **Performance-Minded:** Optimize for speed and efficiency

## 📄 License

This project is part of the Spec-Kit framework demonstration.

---

**Built with ❤️ using Constitution-Driven Development**