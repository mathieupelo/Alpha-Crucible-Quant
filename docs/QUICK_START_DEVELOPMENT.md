# Quick Start - Development Workflow

## 🚀 Fastest Way to Develop (Recommended)

For most development work, **run services locally** instead of using Docker. This is **10-100x faster** than Docker rebuilds.

### Option 1: Run Everything Locally (FASTEST)

```bash
# Start both frontend and backend in separate windows
scripts\dev_all.bat
```

Or start individually:

```bash
# Terminal 1: Backend
scripts\dev_backend.bat

# Terminal 2: Frontend  
scripts\dev_frontend.bat
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

**Benefits:**
- ✅ Instant hot reload (changes reflect in < 1 second)
- ✅ Fast startup (< 5 seconds)
- ✅ No Docker overhead
- ✅ Better debugging experience

**Requirements:**
- Python 3.11+ installed
- Node.js 18+ installed
- Virtual environment (run `python -m venv venv` once)
- Dependencies installed (`pip install -r requirements.txt -r backend/requirements.txt`)

---

### Option 2: Docker with Hot Reload (Middle Ground)

When you need Docker but want fast iteration:

```bash
scripts\dev_docker.bat
```

**Benefits:**
- ✅ Still uses Docker environment
- ✅ Hot reload enabled (code changes don't require rebuilds)
- ✅ Faster than full Docker rebuilds

**Note:** First run will build images, but subsequent code changes are instant.

---

### Option 3: Full Docker Stack (Production Testing)

Only when you need to test the full production setup:

```bash
docker-compose up -d
```

Or with ngrok for external access:

```bash
scripts\prepare_and_start_ngrok_final.bat
```

**Use when:**
- Testing nginx proxy configuration
- Testing production-like environment
- Before deploying
- When sharing with external users via ngrok

---

## Development Workflow Recommendations

### For Frontend Changes
1. Use `scripts\dev_frontend.bat` (fastest)
2. Backend can run in Docker or locally (your choice)
3. Make changes → See them instantly (< 1 second)

### For Backend Changes  
1. Use `scripts\dev_backend.bat` (fastest)
2. Frontend can run locally pointing to local backend
3. Make changes → Auto-reloads (< 5 seconds)

### For Full Stack Testing
1. Use `scripts\dev_all.bat` for both locally
2. OR use `scripts\dev_docker.bat` if you prefer Docker

### For API-Only Testing
1. Just run backend: `scripts\dev_backend.bat`
2. Use API docs at http://localhost:8000/api/docs
3. Test endpoints directly without frontend

---

## Environment Setup (One-Time)

### Initial Setup

1. **Create Virtual Environment** (if not exists):
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

2. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r backend/requirements.txt
   ```

3. **Install Node Dependencies**:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Create .env File** (if not exists):
   - Copy `.env_template` to `.env`
   - Add your Supabase database credentials

### Frontend Environment Variables

The frontend will automatically create `.env.local` with:
```
VITE_API_URL=http://localhost:8000/api
VITE_API_KEY=dev-key-change-in-production
```

You can customize this if needed.

---

## Troubleshooting

### Backend won't start
- Check if port 8000 is already in use
- Ensure virtual environment is activated
- Verify `.env` file exists with correct database credentials
- Check if dependencies are installed

### Frontend won't start
- Check if port 3000 is already in use
- Ensure `node_modules` exists (run `npm install` in `frontend/`)
- Check `package.json` scripts

### Database Connection Errors
- Verify `.env` file has correct Supabase credentials
- Check if Supabase database is accessible
- Ensure network connection is working

### Import Errors in Backend
- Check if `PYTHONPATH` includes project root (scripts set this automatically)
- Verify `src/` directory structure is correct

---

## Time Comparison

| Task | Old Workflow | New Workflow | Time Saved |
|------|-------------|--------------|------------|
| Frontend change | 5-10 min (Docker rebuild) | < 1 sec (hot reload) | **99%** |
| Backend change | 5-10 min (Docker rebuild) | < 5 sec (auto-reload) | **95%** |
| Initial startup | 5-10 min | < 5 sec (local) | **98%** |

**Daily time saved:** 1-2 hours for active development

---

## Best Practices

1. **Default to Local Development**: Use `dev_all.bat` for daily work
2. **Use Docker Only When Needed**: For production testing or specific Docker features
3. **Test Locally First**: Faster feedback loop
4. **Use API Docs**: Test backend independently at `/api/docs`
5. **Keep Docker Clean**: Use it for final integration testing before deployment

---

## Next Steps

1. Try `scripts\dev_all.bat` now!
2. Make a small change to frontend or backend
3. See it update instantly
4. Enjoy faster development! 🎉

For more details, see [DEVELOPMENT_IMPROVEMENTS.md](./DEVELOPMENT_IMPROVEMENTS.md)

