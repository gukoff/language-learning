#!/usr/bin/env pwsh
<#
.SYNOPSIS
Test User Story 2: Study Flashcards implementation
.DESCRIPTION
Tests the complete study flashcards functionality
#>

Write-Host "🧪 Testing User Story 2: Study Flashcards" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# Test backend endpoints
Write-Host "`n🔧 Testing Backend API..." -ForegroundColor Cyan

try {
    # Test health endpoint
    Write-Host "  Testing health endpoint..." -NoNewline
    $health = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -ErrorAction Stop
    Write-Host " ✅" -ForegroundColor Green
    
    # Test flashcards endpoint
    Write-Host "  Testing flashcards endpoint..." -NoNewline
    $flashcards = Invoke-WebRequest -Uri "http://localhost:8000/api/flashcards" -UseBasicParsing -ErrorAction Stop
    Write-Host " ✅" -ForegroundColor Green
    
    # Create a test flashcard first
    Write-Host "  Creating test flashcard..." -NoNewline
    $testCard = @{
        front = "Hello"
        back = "Hola"
        tags = @("spanish", "greeting")
    } | ConvertTo-Json
    
    $createResult = Invoke-WebRequest -Uri "http://localhost:8000/api/flashcards" -Method POST -Body $testCard -ContentType "application/json" -UseBasicParsing -ErrorAction Stop
    Write-Host " ✅" -ForegroundColor Green
    
    # Test study session start
    Write-Host "  Testing study session start..." -NoNewline
    $sessionStart = Invoke-WebRequest -Uri "http://localhost:8000/api/study/start" -Method POST -UseBasicParsing -ErrorAction Stop
    $session = $sessionStart.Content | ConvertFrom-Json
    Write-Host " ✅" -ForegroundColor Green
    
    # Test get current flashcard
    Write-Host "  Testing get current flashcard..." -NoNewline
    $currentCard = Invoke-WebRequest -Uri "http://localhost:8000/api/study/$($session.session_id)/current" -UseBasicParsing -ErrorAction Stop
    Write-Host " ✅" -ForegroundColor Green
    
    # Test submit response
    Write-Host "  Testing submit response..." -NoNewline
    $response = @{
        is_correct = $true
        response_time_seconds = 2.5
    } | ConvertTo-Json
    
    $responseResult = Invoke-WebRequest -Uri "http://localhost:8000/api/study/$($session.session_id)/respond" -Method POST -Body $response -ContentType "application/json" -UseBasicParsing -ErrorAction Stop
    Write-Host " ✅" -ForegroundColor Green
    
    # Test get progress
    Write-Host "  Testing get progress..." -NoNewline
    $progress = Invoke-WebRequest -Uri "http://localhost:8000/api/study/$($session.session_id)/progress" -UseBasicParsing -ErrorAction Stop
    Write-Host " ✅" -ForegroundColor Green
    
    Write-Host "`n✅ All backend tests passed!" -ForegroundColor Green
    
} catch {
    Write-Host " ❌" -ForegroundColor Red
    Write-Host "Backend test failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test frontend
Write-Host "`n🌐 Testing Frontend..." -ForegroundColor Cyan

try {
    Write-Host "  Testing frontend server..." -NoNewline
    $frontend = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -ErrorAction Stop
    Write-Host " ✅" -ForegroundColor Green
    
    Write-Host "`n✅ Frontend server is running!" -ForegroundColor Green
    
} catch {
    Write-Host " ❌" -ForegroundColor Red
    Write-Host "Frontend test failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`n🎉 User Story 2 Implementation Test Results:" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host "✅ Backend API endpoints working" -ForegroundColor Green
Write-Host "✅ Study session creation working" -ForegroundColor Green
Write-Host "✅ Flashcard retrieval working" -ForegroundColor Green
Write-Host "✅ Response submission working" -ForegroundColor Green
Write-Host "✅ Progress tracking working" -ForegroundColor Green
Write-Host "✅ Frontend server running" -ForegroundColor Green

Write-Host "`n📋 Manual Testing Instructions:" -ForegroundColor Cyan
Write-Host "1. Open http://localhost:3000 in your browser" -ForegroundColor White
Write-Host "2. Create a few flashcards using the 'Create' button" -ForegroundColor White
Write-Host "3. Click 'Study' to start a study session" -ForegroundColor White
Write-Host "4. Click 'Start Study Session'" -ForegroundColor White
Write-Host "5. Review the flashcard front, click 'Show Answer'" -ForegroundColor White
Write-Host "6. Mark as Correct or Incorrect and proceed" -ForegroundColor White
Write-Host "7. Complete the session to see final results" -ForegroundColor White

Write-Host "`n🏆 User Story 2: Study Flashcards - IMPLEMENTED!" -ForegroundColor Green