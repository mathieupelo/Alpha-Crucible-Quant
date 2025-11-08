@echo off
REM Clear All Caches - Python, Vite, Node, Build artifacts
echo ==============================================
echo   Clearing All Caches
echo ==============================================
echo.

REM Move to repo root
cd /d "%~dp0.."

echo [1/5] Clearing Python cache files (__pycache__)...
for /d /r . %%d in (__pycache__) do @if exist "%%d" (
    echo   Removing: %%d
    rd /s /q "%%d" 2>nul
)
for /r . %%f in (*.pyc) do @if exist "%%f" (
    echo   Removing: %%f
    del /q "%%f" 2>nul
)
echo Python cache cleared!
echo.

echo [2/5] Clearing Vite cache directories...
REM Clear Vite cache in node_modules
if exist "frontend\node_modules\.vite" (
    echo   Removing: frontend\node_modules\.vite
    rd /s /q "frontend\node_modules\.vite" 2>nul
)
REM Clear any .vite directories in frontend
for /d /r frontend %%d in (.vite) do @if exist "%%d" (
    echo   Removing: %%d
    rd /s /q "%%d" 2>nul
)
echo Vite cache cleared!
echo.

echo [3/5] Clearing build output directories...
if exist "frontend\dist" (
    echo   Removing: frontend\dist
    rd /s /q "frontend\dist" 2>nul
)
if exist "backend\dist" (
    echo   Removing: backend\dist
    rd /s /q "backend\dist" 2>nul
)
echo Build artifacts cleared!
echo.

echo [4/5] Clearing TypeScript build info...
for /r frontend %%f in (*.tsbuildinfo) do @if exist "%%f" (
    echo   Removing: %%f
    del /q "%%f" 2>nul
)
echo TypeScript build info cleared!
echo.

echo [5/6] Clearing other cache files...
REM Clear .pytest_cache if exists
if exist ".pytest_cache" (
    echo   Removing: .pytest_cache
    rd /s /q ".pytest_cache" 2>nul
)
REM Clear .mypy_cache if exists
if exist ".mypy_cache" (
    echo   Removing: .mypy_cache
    rd /s /q ".mypy_cache" 2>nul
)
REM Clear .ruff_cache if exists
if exist ".ruff_cache" (
    echo   Removing: .ruff_cache
    rd /s /q ".ruff_cache" 2>nul
)
echo Other caches cleared!
echo.

echo [6/6] Clearing Docker build cache...
echo   Note: This will take longer. Run as admin if needed.
docker builder prune -f >nul 2>&1
if errorlevel 1 (
    echo   Warning: Could not clear Docker cache. Try running as admin.
) else (
    echo   Docker build cache cleared!
)
echo.

echo ==============================================
echo   All caches cleared successfully!
echo   NOTE: Clear your browser cache (Ctrl+Shift+Delete)
echo   or do a hard refresh (Ctrl+Shift+R / Ctrl+F5)
echo ==============================================
echo.
pause

