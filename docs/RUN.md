# How to Run Alpha-Crucible-Quant

This guide explains how to set up, test locally, and deploy the Alpha-Crucible-Quant application.

## 📋 Prerequisites

Before running the application, ensure you have the following installed and configured:

### Required Software

1. **Docker Desktop**
   - **Windows/Mac**: Download from [docker.com](https://www.docker.com/products/docker-desktop/)
   - **Linux**: Install via package manager: `sudo apt-get install docker.io docker-compose`
   - **Verify installation**: Run `docker --version` and `docker-compose --version`
   - **Important**: Docker Desktop must be running before deploying

2. **Ngrok** (Required for external access/deployment)
   - **Download**: Get from [ngrok.com](https://ngrok.com/download)
   - **Installation**: 
     - Windows: Extract to a folder in your PATH or add to PATH
     - Mac/Linux: Extract and add to PATH, or use package manager
   - **Verify**: Run `ngrok version`
   - **Get Auth Token**: Sign up at [ngrok.com](https://dashboard.ngrok.com/get-started/your-authtoken) to get your free auth token

3. **Python 3.11+** (For local development/testing)
   - **Windows**: Download from [python.org](https://www.python.org/downloads/)
   - **Mac**: `brew install python@3.11` or use [python.org](https://www.python.org/downloads/)
   - **Linux**: `sudo apt-get install python3.11 python3.11-venv`
   - **Verify**: Run `python --version` or `python3 --version`

4. **Node.js 18+** (For local development/testing)
   - **Windows/Mac**: Download from [nodejs.org](https://nodejs.org/)
   - **Linux**: `sudo apt-get install nodejs npm`
   - **Verify**: Run `node --version` and `npm --version`

5. **PostgreSQL Database** (Supabase recommended)
   - **Option 1**: Use [Supabase](https://supabase.com) (free tier available)
   - **Option 2**: Local PostgreSQL installation
   - You'll need: Host, Port, Database name, Username, Password

### Environment Configuration

1. **Create `.env` file** in the repository root:
   ```bash
   # Copy the template (if it exists)
   cp .env_template .env
   ```

2. **Configure `.env` file** with your settings:
   ```bash
   # Database Configuration (Supabase PostgreSQL)
   DATABASE_URL=postgresql://postgres:your_password@your_host:5432/postgres
   DB_HOST=your-supabase-host.supabase.co
   DB_PORT=5432
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_NAME=postgres

   # Ngrok Configuration
   NGROK_AUTHTOKEN=your_ngrok_auth_token_here

   # Application Configuration
   NODE_ENV=production
   PYTHONPATH=/app
   API_BASE_URL=http://localhost:8000
   API_KEY=your_api_key_here

   # CORS Configuration
   CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:5173
   ```

## 🧪 Local Testing (Development Mode)

For development and testing, you can run the application locally without Docker. This is **much faster** for development work.

### Option 1: Run Both Services Together (Recommended)

**Windows:**
```bash
scripts\dev_all.bat
```

This will:
- Start the FastAPI backend on `http://localhost:8000`
- Start the React frontend on `http://localhost:3000`
- Open both in separate terminal windows
- Enable hot reload for instant code changes

**Access Points:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs

### Option 2: Run Services Separately

**Terminal 1 - Backend:**
```bash
# Windows
scripts\dev_backend.bat

# Linux/Mac
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
# Windows
scripts\dev_frontend.bat

# Linux/Mac
cd frontend
npm run dev
```

### Initial Local Setup (One-Time)

Before running locally for the first time:

1. **Create Python Virtual Environment:**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
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

4. **Create `.env` file** (as described in Prerequisites section)

### Local Development Benefits

- ⚡ **Instant hot reload** - Changes reflect in < 1 second
- 🚀 **Fast startup** - Services start in < 5 seconds
- 🔧 **Better debugging** - Direct access to logs and errors
- 📝 **No Docker overhead** - Faster iteration cycle

## 🚀 Deployment with Scripts

### Full Deployment with Ngrok (Recommended for Production Testing)

This script handles everything automatically: Docker setup, health checks, and ngrok tunnel.

**Windows:**
```bash
scripts\prepare_and_start_ngrok_final.bat
```

**What this script does:**
1. Checks and fixes IIS port conflicts (Windows)
2. Verifies Docker Desktop is running
3. Builds and starts Docker containers
4. Fixes nginx configuration with correct IPs
5. Performs comprehensive health checks
6. Starts ngrok tunnel for public access

**Access Points After Deployment:**
- Local Frontend: http://localhost:8080
- Local Backend API: http://localhost:8000/api
- Public URL: Check ngrok dashboard at http://localhost:4040 or run `ngrok api tunnels list`

### Basic Docker Deployment (Without Ngrok)

For local Docker deployment without external access:

**Windows:**
```bash
scripts\deploy.bat
```

**Linux/Mac:**
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

**What this script does:**
1. Stops and removes existing containers
2. Removes old Docker images
3. Builds fresh containers
4. Starts all services
5. Shows container status

**Access Points:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api
- Nginx Proxy: http://localhost:8080
- API Documentation: http://localhost:8000/api/docs

### Manual Docker Deployment

If you prefer to run Docker commands manually:

```bash
# Start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## 🔍 Verifying the Deployment

### Check Container Status

```bash
docker-compose ps
```

All services should show as "Up" and healthy.

### Health Checks

Test these endpoints to verify everything is working:

```bash
# Backend health
curl http://localhost:8000/api/health

# Database health
curl http://localhost:8000/api/health/db

# Frontend (via nginx)
curl http://localhost:8080/health

# API documentation
# Open in browser: http://localhost:8000/api/docs
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f nginx
```

## 🛠️ Troubleshooting

### Docker Issues

**Problem: Docker Desktop not running**
- **Solution**: Start Docker Desktop and wait for it to fully load (whale icon in system tray)

**Problem: Port already in use**
- **Solution**: 
  - Windows: The deployment script automatically stops IIS if port 80 is in use
  - Linux/Mac: Stop conflicting services: `sudo lsof -i :80` then `sudo kill -9 <PID>`

**Problem: Containers fail to start**
- **Solution**: 
  ```bash
  # Check logs
  docker-compose logs
  
  # Rebuild from scratch
  docker-compose down -v
  docker-compose up --build -d
  ```

### Database Connection Issues

**Problem: Database connection failed**
- **Solution**: 
  1. Verify `.env` file has correct database credentials
  2. Check if Supabase database is accessible
  3. Verify network connectivity
  4. Test connection: `docker-compose exec backend python -c "from src.database.manager import DatabaseManager; db = DatabaseManager(); print('Connected:', db.connect())"`

### Ngrok Issues

**Problem: Ngrok auth token error**
- **Solution**: 
  1. Get your token from [ngrok dashboard](https://dashboard.ngrok.com/get-started/your-authtoken)
  2. Add to `.env`: `NGROK_AUTHTOKEN=your_token_here`
  3. Or configure manually: `ngrok config add-authtoken YOUR_TOKEN`

**Problem: Ngrok tunnel not starting**
- **Solution**: 
  ```bash
  # Check if ngrok is already running
  scripts\kill_ngrok.bat  # Windows
  # or
  pkill ngrok  # Linux/Mac
  
  # Then restart
  scripts\start_ngrok.bat  # Windows
  ```

### Frontend Not Loading

**Problem: Frontend shows errors**
- **Solution**: 
  1. Check browser console for errors
  2. Verify API URL in frontend configuration
  3. Check CORS settings in `.env`
  4. Verify backend is running: `curl http://localhost:8000/api/health`

### Backend Not Starting

**Problem: Backend fails to start**
- **Solution**: 
  1. Check backend logs: `docker-compose logs backend`
  2. Verify `.env` file exists and has correct values
  3. Check Python dependencies: `docker-compose exec backend pip list`
  4. Verify database connection

## 📝 Useful Commands

### Docker Management

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up --build -d

# View running containers
docker-compose ps

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart backend
docker-compose restart frontend
```

### Ngrok Management

```bash
# Start ngrok (Windows)
scripts\start_ngrok.bat

# Stop ngrok (Windows)
scripts\kill_ngrok.bat

# Check ngrok status
# Open: http://localhost:4040
# Or: curl http://localhost:4040/api/tunnels
```

### Cleanup

```bash
# Stop all containers and remove volumes
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Full cleanup (Windows)
scripts\cleanup_all.bat
```

## 🏗️ Architecture Overview

The application consists of three main services:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx Proxy   │────│  React Frontend │────│  FastAPI Backend│
│   (Port 8080)   │    │   (Port 3000)   │    │   (Port 8000)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                               │
         │                                               │
         │              ┌─────────────────┐              │
         └──────────────│   Supabase      │──────────────┘
                        │   PostgreSQL    │
                        │   Database      │
                        └─────────────────┘
```

### Services

1. **Backend (FastAPI)**
   - REST API server
   - Portfolio optimization and backtesting
   - Database operations
   - Port: 8000

2. **Frontend (React + Vite)**
   - User interface
   - Dashboard and visualizations
   - Port: 3000

3. **Nginx (Reverse Proxy)**
   - Routes API requests to backend
   - Serves frontend static files
   - Load balancing and rate limiting
   - Port: 8080

4. **Ngrok (External Access)**
   - Creates public tunnel to localhost:8080
   - Enables external access without port forwarding
   - Access via ngrok dashboard: http://localhost:4040

## 🔐 Security Notes

1. **Never commit `.env` files** - They contain sensitive credentials
2. **Use strong passwords** for database connections
3. **Keep ngrok tokens secure** - Don't share your auth token
4. **Update CORS origins** in `.env` for production
5. **Use HTTPS in production** - Configure SSL certificates

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/api/docs (when backend is running)
- **Architecture Details**: See `docs/ARCHITECTURE.md`
- **Development Guide**: See `docs/QUICK_START_DEVELOPMENT.md`
- **Docker Deployment**: See `docs/DOCKER_DEPLOYMENT.md`
- **Scripts Documentation**: See `scripts/README.md`

## 🆘 Getting Help

If you encounter issues:

1. **Check the logs**: `docker-compose logs -f`
2. **Verify prerequisites**: Ensure Docker, ngrok, and database are configured
3. **Review documentation**: Check the `docs/` directory
4. **Check health endpoints**: Verify services are responding
5. **Review troubleshooting section** above

## ✅ Quick Checklist

Before deploying, ensure:

- [ ] Docker Desktop is installed and running
- [ ] Ngrok is installed and auth token is configured
- [ ] `.env` file exists with correct database credentials
- [ ] `.env` file contains `NGROK_AUTHTOKEN`
- [ ] Database is accessible (test connection)
- [ ] Ports 3000, 8000, and 8080 are available
- [ ] (For local dev) Python 3.11+ and Node.js 18+ are installed

---

**Happy coding! 🚀**

