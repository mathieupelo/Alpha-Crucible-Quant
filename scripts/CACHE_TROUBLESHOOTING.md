# Cache Troubleshooting Guide

If you're seeing old versions of the frontend after making changes, try these steps in order:

## Quick Fix (Most Common)

1. **Hard refresh your browser:**
   - Windows/Linux: `Ctrl + Shift + R` or `Ctrl + F5`
   - Mac: `Cmd + Shift + R`

2. **Clear browser cache manually:**
   - Chrome/Edge: `Ctrl + Shift + Delete` → Check "Cached images and files" → Clear
   - Or open DevTools (F12) → Right-click refresh button → "Empty Cache and Hard Reload"

## If Hard Refresh Doesn't Work

### For Local Development (without Docker)

1. Run `scripts\clear_all_cache.bat` to clear all local caches
2. Restart your dev servers with `scripts\full_restart.bat`
3. Hard refresh browser (Ctrl+Shift+R)

### For Docker Development

1. **Stop containers:**
   ```batch
   docker-compose down
   ```

2. **Clear all caches and rebuild:**
   ```batch
   scripts\rebuild_docker_no_cache.bat
   ```
   OR
   ```batch
   scripts\full_restart_with_docker.bat
   ```

3. **Clear browser cache** (Ctrl+Shift+Delete or Ctrl+Shift+R)

### Nuclear Option (Complete Reset)

If nothing else works:

1. Stop all containers: `docker-compose down`
2. Clear Docker everything:
   ```batch
   docker system prune -a --volumes
   ```
   (This removes ALL unused Docker data - use with caution!)
3. Run `scripts\clear_all_cache.bat`
4. Rebuild: `scripts\rebuild_docker_no_cache.bat`
5. Clear browser cache completely

## Why This Happens

1. **Browser Cache**: Nginx serves files with 1-year cache headers, so browsers cache aggressively
2. **Docker Layer Cache**: Docker caches build layers, so changes might not rebuild
3. **Vite Cache**: Vite caches compiled modules in `node_modules/.vite`
4. **Python Cache**: `__pycache__` folders can cause stale imports

## Prevention

- Use development mode (`scripts\dev_all.bat` or `docker-compose.dev.yml`) for active development
- Use production Docker only for final builds/deployment
- Add cache-busting to your build process if needed

