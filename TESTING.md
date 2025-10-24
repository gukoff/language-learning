# 🧪 Testing the Flashcard Learning MVP

This guide will help you test the **User Story 1: Create Flashcards** MVP functionality.

## 📋 Prerequisites

- Python 3.12+ installed
- Node.js 16+ installed  
- PowerShell or terminal access
- Git (already available)

## 🚀 Quick Start Testing

### Option 1: Automated Test Script (Recommended)

```powershell
# Run the automated test script
.\test-mvp.ps1
```

### Option 2: Manual Step-by-Step

Follow the detailed instructions below for manual testing.

---

## 🔧 Backend Setup & Testing

### 1. Install Backend Dependencies

```powershell
cd backend
pip install -r requirements.txt
```

### 2. Run Backend Tests (TDD Validation)

```powershell
# Run all tests
pytest -v

# Run tests with coverage
pytest --cov=src --cov-report=html

# Run specific User Story 1 tests
pytest tests/unit/test_flashcard_model.py -v
pytest tests/unit/test_flashcard_service.py -v
pytest tests/integration/test_flashcard_routes.py -v
```

### 3. Start Backend Server

```powershell
# Start the FastAPI server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 4. Test Backend API Endpoints

Open a new terminal and test the API:

```powershell
# Health check
curl http://localhost:8000/health

# API documentation (open in browser)
start http://localhost:8000/docs

# Create a test flashcard
curl -X POST "http://localhost:8000/api/flashcards" -H "Content-Type: application/json" -d "{\"front\":\"Hello\",\"back\":\"Hola\"}"

# Get all flashcards
curl http://localhost:8000/api/flashcards
```

---

## 🎨 Frontend Setup & Testing

### 1. Install Frontend Dependencies

```powershell
cd frontend
npm install
```

### 2. Run Frontend Tests

```powershell
# Run all frontend tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode (for development)
npm run test:watch

# Lint the code
npm run lint
```

### 3. Start Frontend Server

```powershell
# Start the frontend development server
npm start
```

**Expected Output:**
```
Starting up http-server, serving ./
http-server version: 14.1.1
Available on:
  http://127.0.0.1:8080
  http://[your-ip]:8080
Hit CTRL-C to stop the server
```

---

## 🧪 Manual MVP Testing Scenarios

### Test Scenario 1: Complete Flashcard Creation Flow

1. **Open the application**: http://localhost:8080
2. **Verify welcome screen** displays with navigation buttons
3. **Check API status** - should show "Connected ✓"
4. **Click "Create Your First Flashcard"**
5. **Fill out the form**:
   - Front: "What is the Spanish word for hello?"
   - Back: "Hola"
6. **Click "Create Flashcard"**
7. **Verify success message** appears
8. **Check form is cleared** after creation

### Test Scenario 2: Form Validation

1. **Navigate to Create Flashcard**
2. **Try to submit empty form** - should show validation errors
3. **Enter only front text** - should require back text
4. **Enter whitespace only** - should show "cannot be empty" errors
5. **Enter very long text (500+ chars)** - should be truncated or show error
6. **Verify character counters** update as you type

### Test Scenario 3: API Integration

1. **Open browser developer tools** (F12)
2. **Go to Network tab**
3. **Create a flashcard**
4. **Verify API calls**:
   - POST to `/api/flashcards` returns 201
   - Response contains created flashcard with ID
   - No network errors in console

### Test Scenario 4: Error Handling

1. **Stop the backend server** (Ctrl+C)
2. **Try to create a flashcard**
3. **Verify error message** about network/connection issues
4. **Restart backend server**
5. **Verify health status** returns to "Connected"

### Test Scenario 5: Accessibility Testing

1. **Use Tab key** to navigate through the form
2. **Verify focus indicators** are visible
3. **Use screen reader** (if available) to test labels
4. **Check form works without mouse**

---

## 📊 Performance Testing

### Backend Performance

```powershell
# Test API response times (requires curl or similar)
Measure-Command { curl http://localhost:8000/api/flashcards }
```

### Frontend Performance

1. **Open browser developer tools**
2. **Go to Network tab**
3. **Reload page and measure**:
   - Initial page load < 2 seconds (constitution requirement)
   - API calls < 300ms (constitution requirement)

---

## 🐛 Troubleshooting

### Backend Issues

**Port already in use:**
```powershell
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID [process_id] /F

# Or use different port
uvicorn src.main:app --reload --port 8001
```

**Import errors:**
```powershell
# Ensure you're in backend directory
cd backend
pip install -r requirements.txt
```

### Frontend Issues

**Port already in use:**
```powershell
# Kill process on port 8080
netstat -ano | findstr :8080
taskkill /PID [process_id] /F

# Or use different port
http-server -p 8081
```

**CORS errors:**
- Ensure backend is running on correct port
- Check backend CORS configuration in `src/main.py`

---

## ✅ Success Criteria

Your MVP passes testing if:

- ✅ Backend server starts without errors
- ✅ All backend tests pass (pytest)
- ✅ All frontend tests pass (npm test)
- ✅ API documentation is accessible at `/docs`
- ✅ Frontend loads at http://localhost:8080
- ✅ You can create flashcards successfully
- ✅ Form validation works properly
- ✅ Error handling displays appropriate messages
- ✅ API health check shows "Connected"

---

## 🎯 Next Steps After MVP Testing

Once User Story 1 testing is complete:

1. **Document any bugs found**
2. **Verify constitution compliance** (performance, accessibility)
3. **Proceed to User Story 2** (Study Flashcards)
4. **Consider deployment** of MVP for user feedback

---

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **Backend Code**: `backend/src/`
- **Frontend Code**: `frontend/src/`  
- **Test Files**: `backend/tests/` and `frontend/tests/`
- **Constitution**: `specs/001-flashcard-system/constitution.md`