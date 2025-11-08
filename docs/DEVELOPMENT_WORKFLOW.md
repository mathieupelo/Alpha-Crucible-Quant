# Development Workflow - Quick Reference

## 🎯 When to Use What

### Daily Development (90% of the time)
```bash
scripts\dev_all.bat
```
- ✅ Fastest startup
- ✅ Instant hot reload
- ✅ Best debugging experience

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

### Docker Testing (When you need it)
```bash
# With hot reload
scripts\dev_docker.bat

# Full production stack
docker-compose up -d

# With ngrok for external access
scripts\prepare_and_start_ngrok_final.bat
```

## 📊 Time Comparison

| Activity | Old Method | New Method | Improvement |
|----------|-----------|------------|-------------|
| Frontend change | 5-10 min | < 1 sec | **99% faster** |
| Backend change | 5-10 min | < 5 sec | **95% faster** |
| Full startup | 5-10 min | < 5 sec | **98% faster** |

## 🚀 Getting Started

1. **First time setup:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt -r backend/requirements.txt
   cd frontend && npm install && cd ..
   ```

2. **Daily development:**
   ```bash
   scripts\dev_all.bat
   ```

3. **Make changes and see them instantly!**

For detailed documentation, see:
- [Quick Start Development Guide](docs/QUICK_START_DEVELOPMENT.md)
- [Development Improvements](docs/DEVELOPMENT_IMPROVEMENTS.md)

