# Local Development Guide

This guide explains how to run the Alpha Crucible Quant application locally for development.

## Quick Start

### Option 1: Start Everything at Once (Recommended)

```bash
scripts\dev\dev_all.bat
```

This starts both frontend and backend in separate windows. The backend uses `python main.py` by default.

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

### Option 2: Start Services Individually

**Backend (Simple Mode - Recommended):**
```bash
scripts\dev\dev_backend_simple.bat
```
This runs `python main.py` from the backend folder - the simplest way.

**Backend (Uvicorn Mode - with hot reload):**
```bash
scripts\dev\dev_backend.bat
```
This uses uvicorn with hot reload for faster development.

**Frontend:**
```bash
scripts\dev\dev_frontend.bat
```

## Development Workflow

### Daily Development (Local)

1. **Start local services:**
   ```bash
   scripts\dev\dev_all.bat
   ```

2. **Make changes** - Both frontend and backend support hot reload:
   - Frontend: Changes reflect instantly (< 1 second)
   - Backend: Changes reload automatically (2-5 seconds)

3. **Test your changes** at:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api/docs

### Final Testing (Docker + Ngrok)

Before committing, test the full production-like stack:

1. **Start Docker services:**
   ```bash
   docker-compose up -d
   ```

2. **Start ngrok for external access:**
   ```bash
   scripts\ngrok\start_ngrok_dev.bat
   ```

   This script automatically:
   - Detects if services are running locally or in Docker
   - Starts ngrok on the appropriate port
   - Provides a public URL for testing

## Backend Options

### Simple Mode (`python main.py`)
- **Script:** `dev_backend_simple.bat`
- **Pros:** Simplest, matches your normal workflow
- **Cons:** No hot reload (need to restart manually)
- **Best for:** Quick testing, when you prefer `python main.py`

### Uvicorn Mode (with hot reload)
- **Script:** `dev_backend.bat`
- **Pros:** Automatic hot reload on file changes
- **Cons:** Slightly more complex setup
- **Best for:** Active development with frequent changes

## Frontend Configuration

The frontend automatically:
- Creates `.env.local` if it doesn't exist
- Configures API URL to `http://localhost:8000/api`
- Uses Vite proxy to forward `/api` requests to backend

## Troubleshooting

### Backend Won't Start

1. **Check virtual environment:**
   ```bash
   # From repo root
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt -r backend/requirements.txt
   ```

2. **Check .env file:**
   - Ensure `.env` exists in repo root
   - Verify database credentials are correct

3. **Check port 8000:**
   ```bash
   netstat -ano | findstr ":8000"
   ```
   If port is in use, stop the process or change the port in `backend/main.py`

### Frontend Won't Start

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Check port 3000:**
   ```bash
   netstat -ano | findstr ":3000"
   ```

### Services Can't Connect

1. **Verify backend is running:**
   - Check http://localhost:8000/api/health
   - Should return: `{"status":"healthy","service":"alpha-crucible-api"}`

2. **Verify frontend proxy:**
   - Check `frontend/vite.config.ts` - proxy should point to `http://localhost:8000`
   - Frontend uses relative URLs (`/api`) which Vite proxies to backend

3. **Check CORS:**
   - Backend allows `http://localhost:3000` by default
   - If issues persist, check `backend/main.py` CORS configuration

## Ngrok Setup

The `start_ngrok_dev.bat` script:

1. **Detects your setup:**
   - If Docker is running (port 8080): Uses Docker setup
   - If local services running: Uses local setup
   - Automatically selects the correct port

2. **Works with both:**
   - Local development (ports 3000/8000)
   - Docker production stack (port 8080)

3. **Requirements:**
   - `.env` file with `NGROK_AUTHTOKEN=your_token`
   - Services must be running before starting ngrok

## Best Practices

1. **Use local development for daily work:**
   - Fastest iteration
   - Better debugging experience
   - No Docker overhead

2. **Test with Docker before committing:**
   - Ensures production-like environment
   - Catches Docker-specific issues
   - Validates full stack integration

3. **Use ngrok for final testing:**
   - Test external access
   - Share with team for testing
   - Verify production-like behavior

## File Structure

```
Alpha-Crucible-Quant/
├── backend/
│   └── main.py              # Backend entry point
├── frontend/
│   ├── src/                 # Frontend source
│   └── vite.config.ts       # Vite config with proxy
├── scripts/
│   ├── dev/
│   │   ├── dev_all.bat      # Start both services
│   │   ├── dev_backend.bat  # Backend (uvicorn)
│   │   ├── dev_backend_simple.bat  # Backend (python main.py)
│   │   └── dev_frontend.bat # Frontend
│   └── ngrok/
│       └── start_ngrok_dev.bat  # Ngrok setup (dev)
└── .env                     # Environment variables
```

## Next Steps

1. Try `scripts\dev\dev_all.bat` to start everything
2. Make a change and see it update instantly
3. When ready to test, run `scripts\ngrok\start_ngrok_dev.bat`

Happy coding! 🚀

