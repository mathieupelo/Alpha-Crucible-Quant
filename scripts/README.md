# Alpha Crucible Quant - Scripts Directory

This directory contains all deployment, development, and utility scripts for the Alpha Crucible Quant application.

## Main Deployment Scripts

### `prepare_and_start_ngrok_final.bat` ⭐ **MAIN DEPLOYMENT SCRIPT**
**The complete deployment solution that handles everything automatically.**
- **Purpose**: Complete deployment with automatic issue resolution
- **What it does**:
  - Fixes IIS port conflicts (stops IIS services)
  - Starts Docker services with retry logic
  - Fixes nginx configuration with correct IPs
  - Performs comprehensive health checks
  - Starts ngrok tunnel for public access
- **Usage**: `scripts\prepare_and_start_ngrok_final.bat`
- **Dependencies**: `fix_nginx_ips_v2.bat`

### `quick_start.bat`
**Simple deployment workflow.**
- **Purpose**: Quick deployment without ngrok
- **What it does**: Sets up .env, checks Docker, calls `deploy.bat`
- **Usage**: `scripts\quick_start.bat`

### `deploy.bat` / `deploy.sh`
**Basic Docker deployment.**
- **Purpose**: Standard Docker Compose deployment
- **Usage**: `scripts\deploy.bat` (Windows) or `scripts\deploy.sh` (Linux)

## Development Scripts

### `dev_all.bat` ⭐ **MAIN DEV SCRIPT**
**Start both frontend and backend in development mode.**
- **Purpose**: Start full stack development servers
- **What it does**: Opens separate windows for backend and frontend
- **Usage**: `scripts\dev_all.bat`
- **Output**: Backend on http://localhost:8000, Frontend on http://localhost:3000

### `dev_backend.bat`
**Start backend only.**
- **Purpose**: Run FastAPI backend in development mode
- **Usage**: `scripts\dev_backend.bat`

### `dev_frontend.bat`
**Start frontend only.**
- **Purpose**: Run React frontend in development mode
- **Usage**: `scripts\dev_frontend.bat`

### `dev_docker.bat`
**Start development stack with Docker.**
- **Purpose**: Run development environment in Docker with hot reload
- **Usage**: `scripts\dev_docker.bat`

## Restart Scripts

### `full_restart.bat` ⭐ **MAIN RESTART SCRIPT**
**Complete restart with cache clearing.**
- **Purpose**: Clear all caches and restart everything
- **What it does**:
  - Clears Python cache (__pycache__, *.pyc)
  - Clears Vite cache
  - Kills existing processes
  - Stops Docker containers
  - Starts fresh servers via `dev_all.bat`
- **Usage**: `scripts\full_restart.bat`

### `restart_all.bat`
**Alias for `full_restart.bat`.**
- **Purpose**: Convenience alias
- **Note**: Simply calls `full_restart.bat`
- **Usage**: `scripts\restart_all.bat`

### `restart_backend.bat`
**Restart backend only.**
- **Purpose**: Clear cache and restart backend
- **Usage**: `scripts\restart_backend.bat`

### `full_restart_with_docker.bat`
**Restart with Docker containers.**
- **Purpose**: Full restart including Docker containers
- **Usage**: `scripts\full_restart_with_docker.bat`

## Ngrok Management Scripts

### `start_ngrok.bat`
**Start ngrok tunnel (manual use).**
- **Purpose**: Configure and start ngrok on port 8080 (assumes services already running)
- **Usage**: `scripts\ngrok\start_ngrok.bat`
- **Note**: Only use if Docker services are already running. For full deployment, use `prepare_and_start_ngrok_final.bat`

### `start_ngrok_dev.bat`
**Start ngrok for development (auto-detects local/Docker).**
- **Purpose**: Automatically detects if services are running locally or in Docker and starts ngrok accordingly
- **Usage**: `scripts\ngrok\start_ngrok_dev.bat`
- **Note**: Best for development use - works with both local dev servers and Docker

### `kill_ngrok.bat`
**Stop all ngrok processes.**
- **Purpose**: Kill all running ngrok.exe processes
- **Usage**: `scripts\kill_ngrok.bat`

### `check_ngrok.bat`
**Check ngrok tunnel status.**
- **Purpose**: Verify if ngrok is running and get tunnel URL
- **Usage**: `scripts\check_ngrok.bat`

## System Management Scripts

### `fix_nginx_ips_v2.bat`
**Update nginx configuration with container IPs.**
- **Purpose**: Fix nginx.conf with correct Docker container IPs
- **Usage**: Called automatically by deployment scripts

### `check_and_fix_iis.bat`
**IIS conflict detection and resolution.**
- **Purpose**: Check for IIS port conflicts and resolve them
- **Usage**: `scripts\check_and_fix_iis.bat`

### `kill_port_3000.bat`
**Kill processes using port 3000.**
- **Purpose**: Free port 3000 for frontend
- **Usage**: `scripts\kill_port_3000.bat`

### `clear_all_cache.bat`
**Clear all cache files.**
- **Purpose**: Remove Python and Vite caches
- **Usage**: `scripts\clear_all_cache.bat`

### `fix_frontend_cache.bat`
**Fix frontend cache issues.**
- **Purpose**: Clear frontend-specific caches
- **Usage**: `scripts\fix_frontend_cache.bat`

### `cleanup_all.bat`
**Complete cleanup.**
- **Purpose**: Stop containers, remove images, clear caches
- **Usage**: `scripts\cleanup_all.bat`

### `rebuild_docker_no_cache.bat`
**Rebuild Docker images without cache.**
- **Purpose**: Force rebuild all Docker images
- **Usage**: `scripts\rebuild_docker_no_cache.bat`

### `verify_connectivity.bat`
**Test container connectivity.**
- **Purpose**: Verify services are reachable after deployment
- **Usage**: `scripts\verify_connectivity.bat`

### `test_db_connection.bat`
**Test database connection.**
- **Purpose**: Verify database connectivity
- **Usage**: `scripts\test_db_connection.bat`

## Python Scripts

### `setup_database.py`
**Database initialization.**
- **Purpose**: Create database schema and tables
- **Usage**: `python scripts\setup_database.py`

### `setup_dev.py`
**Development environment setup.**
- **Purpose**: Set up development environment
- **Usage**: `python scripts\setup_dev.py`

### `setup_ngrok.py`
**Ngrok configuration.**
- **Purpose**: Configure ngrok authentication
- **Usage**: `python scripts\setup_ngrok.py`

### `run_backtest.py`
**Run backtest.**
- **Purpose**: Execute backtesting with various configurations
- **Usage**: `python scripts\run_backtest.py`

### `migrate_to_signals_table.py`
**Database migration script.**
- **Purpose**: One-time migration to signals table structure
- **Usage**: `python scripts\migrate_to_signals_table.py`
- **Note**: One-time use only - migration should be complete

### `test_imports.py`
**Test backend imports.**
- **Purpose**: Verify all backend imports work correctly
- **Usage**: `python scripts\test_imports.py`

### `test_openai_key.py`
**Test OpenAI API key.**
- **Purpose**: Verify OpenAI API key is valid
- **Usage**: `python scripts\test_openai_key.py`

## Quick Reference

### Most Common Workflows

**Start Development:**
```bash
scripts\dev_all.bat
```

**Full Restart:**
```bash
scripts\full_restart.bat
```

**Deploy with Ngrok:**
```bash
scripts\prepare_and_start_ngrok_final.bat
```

**Clean Everything:**
```bash
scripts\cleanup_all.bat
```

## Script Redundancy Notes

The following scripts are aliases or have overlapping functionality:
- `restart_all.bat` → calls `full_restart.bat` (can be kept as convenience alias)
- Multiple ngrok scripts serve different purposes (start, kill, check) - all needed
- `quick_start.bat` vs `deploy.bat` - quick_start adds .env setup, both useful

## Notes

- All `.bat` scripts are designed for Windows
- The main deployment script (`prepare_and_start_ngrok_final.bat`) handles all common deployment issues automatically
- Scripts include comprehensive error handling and retry logic
- Health checks ensure services are ready before proceeding
- IIS conflicts are automatically detected and resolved
