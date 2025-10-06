# Alpha Crucible Quant - Complete Project Reset Script
# This script completely resets all caches, dependencies, and temporary files
# Run this script from the project root directory

param(
    [switch]$SkipConfirmation,
    [switch]$SkipBackend,
    [switch]$SkipFrontend
)

# Function to write colored output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# Function to check if we're in the right directory
function Test-ProjectRoot {
    $hasFrontend = Test-Path "frontend\package.json"
    $hasBackend = Test-Path "backend\requirements.txt"
    $hasSrc = Test-Path "src\__init__.py"
    
    return $hasFrontend -and $hasBackend -and $hasSrc
}

# Main execution
Write-ColorOutput "🔄 Alpha Crucible Quant - Complete Project Reset" "Yellow"
Write-ColorOutput "=================================================" "Yellow"

# Check if we're in the project root
if (-not (Test-ProjectRoot)) {
    Write-ColorOutput "❌ Error: Please run this script from the project root directory" "Red"
    Write-ColorOutput "   Expected to find: frontend/package.json, backend/requirements.txt, src/__init__.py" "Red"
    exit 1
}

# Confirmation prompt
if (-not $SkipConfirmation) {
    Write-ColorOutput "⚠️  This will completely reset all caches and dependencies!" "Red"
    Write-ColorOutput "   - Remove all node_modules and package-lock.json files" "Red"
    Write-ColorOutput "   - Clear all Python __pycache__ directories" "Red"
    Write-ColorOutput "   - Clear npm and pip caches" "Red"
    Write-ColorOutput "   - Remove build artifacts" "Red"
    Write-ColorOutput ""
    $confirmation = Read-Host "Are you sure you want to continue? (y/N)"
    if ($confirmation -ne "y" -and $confirmation -ne "Y") {
        Write-ColorOutput "❌ Reset cancelled by user" "Yellow"
        exit 0
    }
}

Write-ColorOutput ""
Write-ColorOutput "🚀 Starting complete project reset..." "Green"

# Step 1: Stop running processes
Write-ColorOutput "⏹️  Step 1: Stopping running processes..." "Blue"
try {
    Get-Process | Where-Object {$_.ProcessName -like "*node*" -or $_.ProcessName -like "*python*" -or $_.ProcessName -like "*vite*"} | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-ColorOutput "   ✓ Processes stopped" "Green"
} catch {
    Write-ColorOutput "   ⚠️  Some processes may still be running" "Yellow"
}

# Step 2: Frontend Reset
if (-not $SkipFrontend) {
    Write-ColorOutput ""
    Write-ColorOutput "🎨 Step 2: Resetting frontend..." "Blue"
    
    if (Test-Path "frontend") {
        Set-Location frontend
        
        # Clear npm cache
        Write-ColorOutput "   🧹 Clearing npm cache..." "Cyan"
        npm cache clean --force 2>$null
        
        # Remove node_modules and package-lock.json
        Write-ColorOutput "   🗑️  Removing node_modules and package-lock.json..." "Cyan"
        if (Test-Path "node_modules") {
            Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
        }
        if (Test-Path "package-lock.json") {
            Remove-Item -Force package-lock.json -ErrorAction SilentlyContinue
        }
        
        # Remove build artifacts
        if (Test-Path "dist") {
            Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
        }
        if (Test-Path "build") {
            Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
        }
        
        # Reinstall dependencies
        Write-ColorOutput "   📦 Reinstalling frontend dependencies..." "Cyan"
        npm install
        
        Set-Location ..
        Write-ColorOutput "   ✓ Frontend reset complete" "Green"
    } else {
        Write-ColorOutput "   ⚠️  Frontend directory not found" "Yellow"
    }
} else {
    Write-ColorOutput ""
    Write-ColorOutput "🎨 Step 2: Skipping frontend reset (--SkipFrontend)" "Yellow"
}

# Step 3: Backend Reset
if (-not $SkipBackend) {
    Write-ColorOutput ""
    Write-ColorOutput "🐍 Step 3: Resetting backend..." "Blue"
    
    # Remove Python cache files
    Write-ColorOutput "   🧹 Removing Python cache files..." "Cyan"
    Get-ChildItem -Path . -Recurse -Name "__pycache__" -ErrorAction SilentlyContinue | ForEach-Object {
        Remove-Item -Recurse -Force $_ -ErrorAction SilentlyContinue
    }
    
    # Remove .pyc files
    Get-ChildItem -Path . -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
    
    # Clear pip cache
    Write-ColorOutput "   🧹 Clearing pip cache..." "Cyan"
    pip cache purge 2>$null
    
    # Remove virtual environment if it exists
    $venvPaths = @(".venv", "venv", "env")
    foreach ($venvPath in $venvPaths) {
        if (Test-Path $venvPath) {
            Write-ColorOutput "   🗑️  Removing virtual environment: $venvPath" "Cyan"
            Remove-Item -Recurse -Force $venvPath -ErrorAction SilentlyContinue
        }
    }
    
    Write-ColorOutput "   ✓ Backend reset complete" "Green"
} else {
    Write-ColorOutput ""
    Write-ColorOutput "🐍 Step 3: Skipping backend reset (--SkipBackend)" "Yellow"
}

# Step 4: System-wide cleanup
Write-ColorOutput ""
Write-ColorOutput "🧹 Step 4: System-wide cleanup..." "Blue"

# Remove root node_modules if it exists
if (Test-Path "node_modules") {
    Write-ColorOutput "   🗑️  Removing root node_modules..." "Cyan"
    Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
}

# Remove build artifacts
$buildDirs = @("dist", "build", ".next", "out")
foreach ($dir in $buildDirs) {
    if (Test-Path $dir) {
        Write-ColorOutput "   🗑️  Removing $dir..." "Cyan"
        Remove-Item -Recurse -Force $dir -ErrorAction SilentlyContinue
    }
}

# Clear Windows temp files (optional)
Write-ColorOutput "   🧹 Clearing temporary files..." "Cyan"
Remove-Item -Path "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue

Write-ColorOutput "   ✓ System cleanup complete" "Green"

# Step 5: Summary and next steps
Write-ColorOutput ""
Write-ColorOutput "✅ Reset complete! Ready to start fresh." "Green"
Write-ColorOutput "=================================================" "Yellow"
Write-ColorOutput ""
Write-ColorOutput "📋 Next steps:" "Cyan"
Write-ColorOutput "   1. Activate virtual environment: .venv\Scripts\Activate.ps1" "White"
Write-ColorOutput "   2. Install Python dependencies: pip install -r requirements.txt" "White"
Write-ColorOutput "   3. Install backend dependencies: pip install -r backend/requirements.txt" "White"
Write-ColorOutput "   4. Start backend: cd backend && python main.py" "White"
Write-ColorOutput "   5. Start frontend: cd frontend && npm run dev" "White"
Write-ColorOutput ""
Write-ColorOutput "🎉 Happy coding!" "Green"
