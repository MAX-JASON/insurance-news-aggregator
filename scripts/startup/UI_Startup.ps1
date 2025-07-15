# Cyberpunk Insurance News Aggregator Startup Script
# PowerShell version

# Clear screen and show header
Clear-Host
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗"
Write-Host "║  🤖 CYBERPUNK INSURANCE NEWS AGGREGATOR                  ║"
Write-Host "║  Insurance News Aggregator - Cyberpunk Business UI       ║"
Write-Host "║  🔧 Full API Endpoint Support Version                    ║"
Write-Host "╚══════════════════════════════════════════════════════════╝"
Write-Host ""

# Stop existing processes
Write-Host "🔄 Stopping existing processes..." -ForegroundColor Cyan
Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Check startup files and set priority
Write-Host "🔍 Checking startup files..." -ForegroundColor Cyan
$startFile = ""
$startType = ""

if (Test-Path "test_cyberpunk_ui.py") {
    $startFile = "test_cyberpunk_ui.py"
    $startType = "Cyberpunk Edition"
    Write-Host "✅ Found cyberpunk startup file - with full API support" -ForegroundColor Green
} elseif (Test-Path "apps\start_app.py") {
    $startFile = "apps\start_app.py"
    $startType = "Standard Edition"
    Write-Host "✅ Found standard startup file - with API routes" -ForegroundColor Green
} else {
    Write-Host "❌ Startup file not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please make sure one of the following files exists:"
    Write-Host "  - test_cyberpunk_ui.py (recommended - Cyberpunk Edition)"
    Write-Host "  - apps\start_app.py (Standard Edition)"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Ensure necessary Python packages are installed
Write-Host ""
Write-Host "📦 Checking necessary Python packages..." -ForegroundColor Cyan
Write-Host "  Checking virtual environment..."

if (Test-Path "venv\Scripts\python.exe") {
    & "venv\Scripts\python.exe" -m pip install flask flask-sqlalchemy flask-login flask-paginate flask-limiter --quiet 2>$null
    Write-Host "  ✅ Required packages installed" -ForegroundColor Green
} else {
    Write-Host "  ⚠️ Virtual environment not found, using system Python" -ForegroundColor Yellow
}

# Display startup information
Write-Host ""
Write-Host "📋 Startup configuration:" -ForegroundColor Cyan
Write-Host "  File: $startFile"
Write-Host "  Type: $startType"
Write-Host "  Features: Cyberpunk UI + Full API Endpoints"
Write-Host ""

# Start the server
Write-Host "🚀 Starting Cyberpunk server..." -ForegroundColor Green
Write-Host "  Loading API endpoints..."
Write-Host "  Initializing Cyberpunk interface..."

# Start Python in a new window
Start-Process -FilePath "cmd.exe" -ArgumentList "/k title 🤖 Cyberpunk News Center - Server && color 0A && echo 🤖 Cyberpunk server starting... && D:\insurance-news-aggregator\venv\Scripts\python.exe $startFile"

# Wait for server to start and verify
Write-Host "⏳ Waiting for server to start..." -ForegroundColor Cyan
for ($i = 1; $i -le 10; $i++) {
    Write-Host "  Loading $i/10 - Initializing API endpoints..."
    Start-Sleep -Seconds 1
}

# Test API endpoint availability
Write-Host ""
Write-Host "🔍 Validating API endpoints..." -ForegroundColor Cyan
Write-Host "  Checking basic services..."

# Add more wait time to allow server to fully start
Start-Sleep -Seconds 3

# Try to connect to health check API
$apiReady = $false
for ($i = 1; $i -le 3; $i++) {
    try {
        $response = Invoke-WebRequest -Uri 'http://127.0.0.1:5000/api/health' -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ /api/health - OK" -ForegroundColor Green
            $apiReady = $true
            break
        } else {
            Write-Host "  ⚠️ /api/health - Error" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ⚠️ /api/health - No response (Attempt $i/3)" -ForegroundColor Yellow
        if ($i -lt 3) {
            Start-Sleep -Seconds 2
        }
    }
}

# Check other API endpoints
if ($apiReady) {
    try {
        $response = Invoke-WebRequest -Uri 'http://127.0.0.1:5000/api/v1/stats' -TimeoutSec 3
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ /api/v1/stats - OK" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️ /api/v1/stats - Error" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ⚠️ /api/v1/stats - No response" -ForegroundColor Yellow
    }
    
    try {
        $response = Invoke-WebRequest -Uri 'http://127.0.0.1:5000/api/v1/crawler/status' -TimeoutSec 3
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ /api/v1/crawler/status - OK" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️ /api/v1/crawler/status - Error" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ⚠️ /api/v1/crawler/status - No response" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ⚠️ Main API check failed, skipping remaining API tests" -ForegroundColor Yellow
}

# Open browser
Write-Host ""
Write-Host "🌐 Opening Cyberpunk interface..." -ForegroundColor Cyan

if ($apiReady) {
    Start-Sleep -Seconds 1
    Write-Host "  🏠 Opening business homepage..."
    Start-Process "http://127.0.0.1:5000/business/"
    Start-Sleep -Seconds 2
    
    Write-Host "  🎮 Opening Cyber News Center..."
    Start-Process "http://127.0.0.1:5000/business/cyber-news"
    Start-Sleep -Seconds 1
} else {
    Write-Host "  ⚠️ API server failed to start properly, cannot open interface" -ForegroundColor Red
    Write-Host "  Please check command window for error messages" -ForegroundColor Red
    Start-Sleep -Seconds 3
}

# Display completion information and debugging tips
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗"
Write-Host "║  ✨ CYBERPUNK SYSTEM STARTUP COMPLETE!                   ║"
Write-Host "║                                                          ║"
Write-Host "║  🔗 Available Interfaces:                                ║"
Write-Host "║    🏠 Business Homepage: http://127.0.0.1:5000/business/ ║"
Write-Host "║    🎮 Cyber News Center: http://127.0.0.1:5000/business/cyber-news ║"
Write-Host "║    📊 Monitor Center: http://127.0.0.1:5000/monitor/     ║"
Write-Host "║                                                          ║"
Write-Host "║  🔌 API Endpoints:                                       ║"
Write-Host "║    🩺 Health Check: http://127.0.0.1:5000/api/health     ║"
Write-Host "║    📈 Statistics: http://127.0.0.1:5000/api/v1/stats     ║"
Write-Host "║    🤖 Crawler Status: http://127.0.0.1:5000/api/v1/crawler/status ║"
Write-Host "║    🎯 Cyber API: http://127.0.0.1:5000/api/cyber-news    ║"
Write-Host "║                                                          ║"
Write-Host "║  💡 Debug Information:                                   ║"
Write-Host "║    - If frontend shows 404 errors, check server window  ║"
Write-Host "║    - API endpoints have automatic fallback mechanism    ║"
Write-Host "║    - Supports drag-and-drop and keyboard shortcuts      ║"
Write-Host "║    - Closing the server window will stop the application║"
Write-Host "╚══════════════════════════════════════════════════════════╝"
Write-Host ""
Write-Host "🌟 Welcome to the Cyberpunk Business World!" -ForegroundColor Magenta
Write-Host "💊 If you encounter API errors, backup endpoints are auto-loaded" -ForegroundColor Cyan
Write-Host ""

Read-Host "Press Enter to exit"
