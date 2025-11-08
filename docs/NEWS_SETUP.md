# News Feed Setup Instructions

## Issue: 404 Error When Loading News

If you're seeing a 404 error, it's likely because:
1. The backend server needs to be restarted to load the new news router
2. The transformers library may not be installed (but this is now optional)

## Quick Fix Steps

### 1. Restart Backend Server
The backend must be restarted to load the new `/api/news` routes.

**If using Docker:**
```bash
docker-compose restart backend
```

**If running manually:**
- Stop the backend server (Ctrl+C)
- Restart it: `cd backend && python main.py` or `uvicorn main:app --reload`

### 2. Install Optional Dependencies (For Full FinBERT Support)

For AI-powered sentiment analysis with FinBERT:
```bash
cd backend
pip install transformers torch
```

**Note:** The news feed will work without these dependencies using a simple keyword-based sentiment analysis fallback.

### 3. Verify the Route is Working

Test the endpoint:
```bash
curl -X GET "http://localhost:8000/api/news/universe/GameCore-12%20(GC-12)" \
  -H "Authorization: Bearer my-awesome-key-123"
```

### 4. Check Backend Logs

Look for these log messages:
- `News router loaded successfully` (when backend starts)
- `Fetching news for universe: 'GameCore-12 (GC-12)'` (when request is made)

## Troubleshooting

### Still Getting 404?
1. Check that `backend/api/news.py` exists
2. Check that `backend/main.py` includes: `app.include_router(news.router, prefix="/api", ...)`
3. Verify backend server logs show no import errors
4. Try accessing the API docs: `http://localhost:8000/api/docs` - you should see a "news" tag

### News Feed Shows But No Articles?
- This is normal if Yahoo Finance has no recent news for the tickers
- Check backend logs for any errors fetching from yfinance
- The feed will show "No news available at this time" if empty

### Sentiment Analysis Not Working?
- If transformers isn't installed, it will use simple keyword-based sentiment (still works!)
- To get FinBERT, install: `pip install transformers torch`
- First run will download the model (~500MB) - be patient

