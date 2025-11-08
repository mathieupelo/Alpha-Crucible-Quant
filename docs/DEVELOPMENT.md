# Development Guide

This guide covers the development workflow for Alpha Crucible Quant, including local setup, best practices, and daily workflow.

## Quick Start

### Fastest Development Setup (Recommended)

For daily development work, run services locally for instant hot reload:

```bash
# Start both frontend and backend
scripts\dev_all.bat  # Windows
# or
scripts/dev_all.sh   # Linux/Mac
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

**Benefits:**
- ⚡ Instant hot reload (changes reflect in < 1 second)
- 🚀 Fast startup (< 5 seconds)
- 🔧 Better debugging experience
- 📝 No Docker overhead

### Initial Setup (One-Time)

1. **Create Virtual Environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

2. **Install Python Dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r backend/requirements.txt
   ```

3. **Install Node.js Dependencies:**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Create `.env` File:**
   ```bash
   cp .env_template .env
   # Edit .env with your Supabase database credentials
   ```

## Development Workflow

### Daily Development

**Default workflow (90% of the time):**
```bash
scripts\dev_all.bat
```

This starts both services with hot reload. Make changes and see them instantly!

### Backend-Only Development

```bash
scripts\dev_backend.bat
```

- Test APIs at http://localhost:8000/api/docs
- No frontend needed
- Fastest for backend work

### Frontend-Only Development

```bash
scripts\dev_frontend.bat
```

- Backend can stay running in Docker or locally
- Instant frontend updates
- Fastest for UI work

### Docker Testing (When Needed)

```bash
# With hot reload
scripts\dev_docker.bat

# Full production stack
docker-compose up -d

# With ngrok for external access
scripts\prepare_and_start_ngrok_final.bat
```

## Time Comparison

| Task | Old Method | New Method | Improvement |
|------|-----------|------------|-------------|
| Frontend change | 5-10 min | < 1 sec | **99% faster** |
| Backend change | 5-10 min | < 5 sec | **95% faster** |
| Full startup | 5-10 min | < 5 sec | **98% faster** |

**Daily time saved:** 1-2 hours for active development

## Best Practices

### 1. Default to Local Development
- Use `dev_all.bat` for daily work
- Only use Docker when testing production setup

### 2. Use API Docs for Backend Testing
- Test endpoints independently at `/api/docs`
- Faster feedback loop than full stack testing

### 3. Keep Docker Clean
- Use Docker for final integration testing
- Don't rebuild Docker for every small change

### 4. Environment Variables
- Frontend automatically creates `.env.local` with API URL
- Backend uses `.env` for database configuration
- Both can be customized if needed

## Troubleshooting

### Backend Won't Start
- Check if port 8000 is already in use
- Ensure virtual environment is activated
- Verify `.env` file exists with correct database credentials
- Check if dependencies are installed

### Frontend Won't Start
- Check if port 3000 is already in use
- Ensure `node_modules` exists (run `npm install` in `frontend/`)
- Check `package.json` scripts

### Database Connection Errors
- Verify `.env` file has correct Supabase credentials
- Check if Supabase database is accessible
- Ensure network connection is working

### Import Errors in Backend
- Scripts automatically set `PYTHONPATH` to include project root
- Verify `src/` directory structure is correct
- Check that virtual environment is activated

## Project Structure

### Backend Development
- **Entry Point**: `backend/main.py`
- **API Routes**: `backend/api/`
- **Services**: `backend/services/`
- **Core Logic**: `src/` (shared with CLI scripts)

### Frontend Development
- **Entry Point**: `frontend/src/main.tsx`
- **Components**: `frontend/src/components/`
- **Pages**: `frontend/src/pages/`
- **API Service**: `frontend/src/services/api.ts`

### Hot Reload
- **Backend**: Uses uvicorn `--reload` flag
- **Frontend**: Uses Vite HMR (Hot Module Replacement)
- Both detect file changes automatically

## Code Quality

### Python Backend
- Type hints recommended
- Follow PEP 8 style guide
- Use proper error handling
- Add docstrings for functions

### TypeScript Frontend
- Strong typing enforced
- Use React hooks properly
- Follow Material-UI patterns
- Handle loading and error states

## Testing

### Run Tests
```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_database.py -v

# With coverage
pytest tests/ -v --cov=src
```

### Test API Endpoints
- Use FastAPI's interactive docs at `/api/docs`
- Test endpoints directly from browser
- See request/response schemas automatically

## Debugging

### Backend Debugging
- Use Python debugger (`pdb` or IDE debugger)
- Check logs in terminal where backend is running
- Use FastAPI's automatic error pages

### Frontend Debugging
- Use browser DevTools
- React DevTools extension recommended
- Check Network tab for API calls
- Use console.log for debugging (remove before commit)

## Performance Tips

1. **Use Local Development**: 10-100x faster than Docker rebuilds
2. **Test Incrementally**: Test small changes frequently
3. **Use API Docs**: Test backend independently
4. **Cache Dependencies**: Don't reinstall unless needed
5. **Keep Docker Clean**: Only rebuild when dependencies change

## Next Steps

1. Try `scripts\dev_all.bat` now!
2. Make a small change to frontend or backend
3. See it update instantly
4. Enjoy faster development! 🎉

For more information:
- [Deployment Guide](DEPLOYMENT.md) - Production deployment
- [Architecture](ARCHITECTURE.md) - System design
- [API Documentation](API.md) - API endpoints

