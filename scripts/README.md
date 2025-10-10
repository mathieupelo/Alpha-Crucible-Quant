# Alpha Crucible Quant - Scripts Directory

This directory contains all deployment and utility scripts for the Alpha Crucible Quant application.

## Main Deployment Scripts

### `prepare_and_start_ngrok_final.bat` ⭐ **MAIN SCRIPT**
**The complete deployment solution that handles everything automatically.**

- **Purpose**: Complete deployment with automatic issue resolution
- **What it does**:
  - Fixes IIS port conflicts (stops IIS services)
  - Starts Docker services with retry logic
  - Fixes nginx configuration with correct IPs
  - Performs comprehensive health checks
  - Starts ngrok tunnel for public access
- **Usage**: `scripts\prepare_and_start_ngrok_final.bat`
- **Dependencies**: `fix_nginx_ips_v2.bat`, `start_ngrok.bat`

## Utility Scripts

### Deployment & Setup
- **`deploy.bat`** - Basic Docker deployment without ngrok
- **`quick_start.bat`** - Simple deployment workflow (calls deploy.bat)
- **`setup_database.py`** - Database initialization script
- **`setup_ngrok.py`** - Ngrok configuration script

### Ngrok Management
- **`start_ngrok.bat`** - Starts ngrok tunnel (called by main script)
- **`kill_ngrok.bat`** - Stops all ngrok processes
- **`check_ngrok.bat`** - Checks ngrok tunnel status

### System Management
- **`check_and_fix_iis.bat`** - IIS conflict detection and resolution
- **`fix_nginx_ips_v2.bat`** - Updates nginx configuration with correct container IPs
- **`verify_connectivity.bat`** - Tests container connectivity after deployment
- **`cleanup_all.bat`** - Complete cleanup (stops containers, removes images, etc.)

### Development & Testing
- **`run_backtest.py`** - Backtesting script
- **`test.py`** - General testing script
- **`deploy.sh`** - Linux deployment script

## Quick Start Guide

### For Complete Deployment (Recommended)
```bash
scripts\prepare_and_start_ngrok_final.bat
```

### For Basic Local Deployment
```bash
scripts\quick_start.bat
```

### For Cleanup
```bash
scripts\cleanup_all.bat
```

### For Ngrok Management
```bash
# Check status
scripts\check_ngrok.bat

# Stop ngrok
scripts\kill_ngrok.bat
```

## Script Dependencies

```
prepare_and_start_ngrok_final.bat
├── fix_nginx_ips_v2.bat
└── start_ngrok.bat
    └── kill_ngrok.bat (referenced)
```

## Notes

- All scripts are designed for Windows (`.bat` files)
- The main script (`prepare_and_start_ngrok_final.bat`) handles all common deployment issues automatically
- Scripts include comprehensive error handling and retry logic
- Health checks ensure services are ready before proceeding
- IIS conflicts are automatically detected and resolved

