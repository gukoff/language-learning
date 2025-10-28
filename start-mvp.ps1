#!/usr/bin/env pwsh
<#
.SYNOPSIS
Start MVP servers for Learn-a-Language Flashcard System
.DESCRIPTION
Starts both backend and frontend servers for MVP testing
#>

Write-Host "🚀 Starting Learn-a-Language MVP" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Function to test if port is available
function Test-Port {
    param($Port)
    try {
        $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Any, $Port)
        $listener.Start()
        $listener.Stop()
        return $true
    } catch {
        return $false
    }
}

# Check ports
if (-not (Test-Port 8000)) {
    Write-Host "⚠️  Port 8000 is already in use" -ForegroundColor Yellow
}

if (-not (Test-Port 3000)) {
    Write-Host "⚠️  Port 3000 is already in use" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📋 Manual Startup Instructions:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Start Backend (in this terminal):" -ForegroundColor White
Write-Host "   python -m uvicorn simple_server:app --reload --port 8000" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Start Frontend (in new terminal):" -ForegroundColor White
Write-Host "   cd frontend" -ForegroundColor Gray
Write-Host "   python -m http.server 3000" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Test the MVP:" -ForegroundColor White
Write-Host "   Backend API: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host "   Frontend UI: http://localhost:3000" -ForegroundColor Gray
Write-Host ""
Write-Host "📖 For detailed testing instructions, see: MVP-TESTING-GUIDE.md" -ForegroundColor Cyan

$startServers = Read-Host "`nWould you like to start both backend and frontend servers now? (y/n)"
if ($startServers -eq 'y' -or $startServers -eq 'Y') {
    Write-Host "`n🔧 Starting servers..." -ForegroundColor Cyan
    Write-Host "Backend: http://localhost:8000/docs" -ForegroundColor Green
    Write-Host "Frontend: http://localhost:3000" -ForegroundColor Green
    
    # Start backend in background job
    $backendJob = Start-Job -ScriptBlock {
        python -m uvicorn simple_server:app --reload --port 8000
    }
    
    # Start frontend in background job
    $frontendJob = Start-Job -ScriptBlock {
        Set-Location frontend
        python -m http.server 3000
    }
    
    # Wait for user to stop
    try {
        Write-Host "`nBoth servers are running. Press any key to stop..." -ForegroundColor Cyan
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    } finally {
        # Clean up jobs
        Write-Host "`n🛑 Stopping servers..." -ForegroundColor Yellow
        Stop-Job $backendJob, $frontendJob -ErrorAction SilentlyContinue
        Remove-Job $backendJob, $frontendJob -ErrorAction SilentlyContinue
        Write-Host "✅ Servers stopped" -ForegroundColor Green
    }
}
