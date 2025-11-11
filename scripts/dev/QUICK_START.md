# Quick Start - Local Development

## 🚀 Fastest Way to Start Development

```bash
scripts\dev\dev_all.bat
```

This starts both frontend and backend. Done! ✅

## 📋 What You Get

- **Frontend:** http://localhost:3000 (with hot reload)
- **Backend:** http://localhost:8000 (using `python main.py`)
- **API Docs:** http://localhost:8000/api/docs

## 🔧 Backend Options

### Simple Mode (Default)
```bash
scripts\dev\dev_backend_simple.bat
```
- Uses `python main.py` from backend folder
- Matches your normal workflow
- **Best for:** Quick testing

### Uvicorn Mode (Hot Reload)
```bash
scripts\dev\dev_backend.bat
```
- Automatic reload on file changes
- **Best for:** Active development

To use uvicorn mode with dev_all:
```bash
scripts\dev\dev_all.bat uvicorn
```

## 🧪 Final Testing (Before Commit)

1. **Start Docker stack:**
   ```bash
   docker-compose up -d
   ```

2. **Start ngrok:**
   ```bash
   scripts\ngrok\Prepare_and_start_ngrok.bat
   ```

   This automatically detects your setup (local or Docker) and starts ngrok on the correct port.

## ✅ Prerequisites

- ✅ Python virtual environment created (`venv` folder exists)
- ✅ Dependencies installed (`pip install -r requirements.txt -r backend/requirements.txt`)
- ✅ Frontend dependencies installed (`cd frontend && npm install`)
- ✅ `.env` file exists in repo root with database credentials

## 🐛 Troubleshooting

**Backend won't start?**
- Check if port 8000 is free: `netstat -ano | findstr ":8000"`
- Verify venv is activated
- Check `.env` file exists

**Frontend won't start?**
- Check if port 3000 is free: `netstat -ano | findstr ":3000"`
- Run `cd frontend && npm install`

**Services can't connect?**
- Verify backend: http://localhost:8000/api/health
- Check browser console for errors
- Verify Vite proxy in `frontend/vite.config.ts`

## 📚 More Info

See `LOCAL_DEVELOPMENT_GUIDE.md` for detailed documentation.

