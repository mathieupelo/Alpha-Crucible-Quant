# Fixing Port 3000 Issues

## The Problem
Sometimes when you run `restart_all.bat`, you see an old version of the frontend. This happens because:
- A lingering Node.js/Vite process is still using port 3000
- The old process wasn't properly killed
- Your browser connects to the old process instead of the new one

## The Solution

### Automatic Fix (Recommended)
The `restart_all.bat` script now automatically:
1. ✅ Kills processes by window title
2. ✅ Kills Node.js processes with "vite" in command line
3. ✅ **Uses PowerShell to find and kill ANY process listening on port 3000** (most reliable)
4. ✅ Falls back to netstat method if PowerShell fails
5. ✅ Verifies port 3000 is free before starting

**Just run `scripts\restart_all.bat` and it should handle it automatically now.**

### Manual Fix (If Automatic Doesn't Work)
If you still see the old version, run:
```batch
scripts\kill_port_3000.bat
```

This script:
- Finds ALL processes listening on port 3000 using PowerShell
- Kills them forcefully
- Stops Docker containers
- Verifies the port is free

### Quick Manual Command
If you just want a one-liner:
```powershell
Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

### Nuclear Option (Kill ALL Node.js)
If nothing else works:
```batch
taskkill /F /IM node.exe
```
⚠️ **Warning:** This kills ALL Node.js processes on your system!

## Why This Happens
- Vite dev server crashes but process doesn't fully terminate
- Windows sometimes holds onto the port even after process ends
- Docker containers might bind to port 3000
- Browser cache (always do Ctrl+Shift+R after restarting)

## Prevention
- Always use `restart_all.bat` instead of manually stopping/starting
- Check port 3000 before starting: `netstat -ano | findstr ":3000"`
- Clear browser cache (Ctrl+Shift+Delete) after restarting

