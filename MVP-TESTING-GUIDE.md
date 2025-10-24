# Manual MVP Testing Guide

## Quick Setup & Testing

### 1. Start Backend Server

Open a PowerShell terminal in the project root and run:

```powershell
python -m uvicorn simple_server:app --reload --port 8000
```

You should see output like:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using StatReload
INFO:     Started server process [xxxxx]
INFO:     Application startup complete.
```

### 2. Test Backend API

Open a **new** PowerShell terminal (keep the server running) and test:

```powershell
# Test health endpoint
Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing

# Test flashcards endpoint
Invoke-WebRequest -Uri "http://localhost:8000/api/flashcards" -UseBasicParsing

# Test API documentation
Start-Process "http://localhost:8000/docs"
```

### 3. Start Frontend Server

From the frontend directory:

```powershell
cd frontend
python -m http.server 3000
```

Or use Node.js if available:
```powershell
npx http-server -p 3000
```

### 4. Test Complete MVP Flow

1. Open http://localhost:3000 in your browser
2. Click "Create" button
3. Fill out the form:
   - Front: "Hello"
   - Back: "Hola"
   - Tags: "spanish, greeting"
4. Click "Save Flashcard"
5. Verify the flashcard appears in the list

### 5. Test API Endpoints Manually

Using PowerShell (with backend running):

```powershell
# Create a flashcard
$body = @{
    front = "Bonjour"
    back = "Hello"
    tags = @("french", "greeting")
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/flashcards" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing

# Get all flashcards
Invoke-WebRequest -Uri "http://localhost:8000/api/flashcards" -UseBasicParsing
```

## Expected Results

✅ **Backend Health Check**: Should return `{"status":"healthy","flashcards_count":0}`

✅ **Empty Flashcards List**: Should return `[]`

✅ **Frontend Loads**: Should display "Learn a Language" interface

✅ **Create Flashcard**: Should successfully save and display new flashcard

✅ **API Documentation**: Should be accessible at http://localhost:8000/docs

## Troubleshooting

### Backend Issues
- **Port 8000 in use**: Kill existing processes or use different port
- **Module not found**: Ensure you're in the project root directory
- **Import errors**: Run `pip install fastapi uvicorn pydantic`

### Frontend Issues
- **Port 3000 in use**: Use different port like `python -m http.server 3001`
- **CORS errors**: Ensure backend is running with CORS configured
- **File not found**: Ensure you're in the frontend directory

### API Testing Issues
- **Connection refused**: Backend server not running
- **404 errors**: Check endpoint URLs are correct
- **JSON errors**: Ensure proper content-type headers

## Success Criteria

The MVP is working correctly if:

1. ✅ Backend server starts without errors
2. ✅ Health endpoint returns healthy status
3. ✅ Frontend interface loads properly
4. ✅ Can create flashcards via web interface
5. ✅ Can create flashcards via API
6. ✅ Flashcards persist during session
7. ✅ API documentation is accessible
8. ✅ No CORS errors in browser console

## Next Steps After Testing

Once MVP is confirmed working:

1. **Test additional User Stories** from the spec
2. **Run comprehensive test suite** (backend/tests/)
3. **Deploy to production environment**
4. **Implement User Story 2: Study Flashcards**
5. **Add persistent storage** (replace in-memory with file/database)

## Constitutional Compliance Check

Verify the implementation meets our principles:

- ✅ **Code Quality**: Clean, readable, well-documented
- ✅ **Testing**: Basic API testing completed
- ✅ **User Experience**: Intuitive interface, accessible design
- ✅ **Performance**: Fast responses, smooth interactions