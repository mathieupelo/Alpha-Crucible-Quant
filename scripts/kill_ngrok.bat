@echo off
REM Kill all Ngrok processes

REM Stop all Ngrok processes silently
taskkill /f /im ngrok.exe >nul 2>&1
