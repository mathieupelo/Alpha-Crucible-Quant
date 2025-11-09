# Deployment Guide

This guide covers all deployment options for Alpha Crucible Quant, from local development to production deployment with external access.

## Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Memory**: Minimum 4GB RAM, recommended 8GB+
- **Storage**: Minimum 10GB free space
- **Network**: Internet connection for data fetching

### Software Requirements
- **Docker Desktop** (for Docker deployment)
  - Windows/Mac: Download from [docker.com](https://www.docker.com/products/docker-desktop/)
  - Linux: `sudo apt-get install docker.io docker-compose`
  - Verify: `docker --version` and `docker-compose --version`
- **Python 3.11+** (for local development)
- **Node.js 18+** (for local development)
- **PostgreSQL Database** (Supabase recommended - free tier available)
- **Ngrok** (optional, for external access)

## Environment Configuration

Create a `.env` file in the repository root:

```bash
cp .env_template .env
```

Configure with your settings:

```bash
# Database Configuration (Supabase PostgreSQL)
DATABASE_URL=postgresql://postgres:password@host:port/database
DB_HOST=your-supabase-host.supabase.co
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your-password
DB_NAME=postgres

# Ngrok Configuration (optional)
NGROK_AUTHTOKEN=your_ngrok_auth_token

# Application Configuration
API_BASE_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:5173
```

## Deployment Options

### Option 1: Local Development (Fastest - Recommended for Development)

For daily development work, run services locally for instant hot reload.

**Start both services:**
```bash
# Windows
scripts\dev_all.bat

# Linux/Mac
scripts/dev_all.sh
```

**Or start individually:**
```bash
# Terminal 1 - Backend
scripts\dev_backend.bat  # Windows
# or
cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Frontend
scripts\dev_frontend.bat  # Windows
# or
cd frontend && npm run dev
```

**Access Points:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

**Benefits:**
- ⚡ Instant hot reload (< 1 second for frontend, < 5 seconds for backend)
- 🚀 Fast startup (< 5 seconds)
- 🔧 Better debugging experience
- 📝 No Docker overhead

**Initial Setup (one-time):**
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..
```

### Option 2: Docker Development (With Hot Reload)

For Docker environment with code hot reload:

```bash
# Uses docker-compose.dev.yml with volume mounts
scripts\dev_docker.bat  # Windows
# or
docker-compose -f docker-compose.dev.yml up
```

**Benefits:**
- ✅ Still uses Docker environment
- ✅ Hot reload enabled (code changes don't require rebuilds)
- ✅ Faster than full Docker rebuilds

### Option 3: Docker Production (Full Stack)

For production-like testing:

**Quick deployment:**
```bash
# Windows
scripts\deploy.bat

# Linux/Mac
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

**Or manually:**
```bash
# Start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Access Points:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Nginx Proxy: http://localhost:8080
- API Docs: http://localhost:8000/api/docs

### Option 4: Docker with External Access (Ngrok)

For external access via ngrok:

```bash
# Windows
scripts\prepare_and_start_ngrok_final.bat

# Linux/Mac
scripts/prepare_and_start_ngrok_final.sh
```

This script:
1. Checks and fixes port conflicts
2. Builds and starts Docker containers
3. Performs health checks
4. Starts ngrok tunnel for public access

**Access Points:**
- Local: http://localhost:8080
- Public: Check ngrok dashboard at http://localhost:4040

## Architecture

The deployment consists of three main services:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx Proxy   │────│  React Frontend │────│  FastAPI Backend│
│   (Port 8080)   │    │   (Port 3000)   │    │   (Port 8000)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                               │
         │              ┌─────────────────┐              │
         └──────────────│   Supabase       │──────────────┘
                        │   PostgreSQL    │
                        │   Database      │
                        └─────────────────┘
```

### Services

1. **Backend (FastAPI)**
   - Port: 8000
   - Database: Supabase PostgreSQL
   - Features: REST API, CORS enabled, health checks

2. **Frontend (React + Vite)**
   - Port: 3000
   - Features: Production build, environment-based API configuration

3. **Nginx (Reverse Proxy)**
   - Port: 8080 (mapped from container port 80)
   - Features: Load balancing, rate limiting, security headers, gzip compression

## Configuration

### Environment Variables

Key environment variables:

```bash
# Database (Supabase PostgreSQL)
DATABASE_URL=postgresql://postgres:password@host:port/database
DB_HOST=your-supabase-host.supabase.co
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your-password
DB_NAME=postgres

# Application
API_BASE_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:5173

# Ngrok (optional)
NGROK_AUTHTOKEN=your_token
```

### Nginx Configuration

The system uses two nginx configuration files:

1. **Root `nginx.conf`**: Reverse proxy for Docker Compose (routes `/api/` to backend, everything else to frontend)
2. **Frontend `frontend/nginx.conf`**: Serves built React app when frontend runs standalone

Both are automatically configured and don't require manual changes.

## Health Checks

Test these endpoints to verify deployment:

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

## Monitoring and Logs

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f nginx

# With timestamps
docker-compose logs -f -t
```

### Check Status

```bash
# Container status
docker-compose ps

# Resource usage
docker stats
```

## Troubleshooting

### Common Issues

**Docker Desktop not running**
- Start Docker Desktop and wait for it to fully load

**Port already in use**
- Windows: Deployment scripts automatically stop IIS if port 80 is in use
- Linux/Mac: `sudo lsof -i :PORT` then `sudo kill -9 <PID>`

**Database connection failed**
- Verify `.env` file has correct Supabase credentials
- Check if Supabase database is accessible
- Test connection: `docker-compose exec backend python -c "from src.database.manager import DatabaseManager; db = DatabaseManager(); print('Connected:', db.connect())"`

**Containers fail to start**
```bash
# Check logs
docker-compose logs

# Rebuild from scratch
docker-compose down -v
docker-compose up --build -d
```

**Frontend not loading**
- Check browser console for errors
- Verify API URL in frontend configuration
- Check CORS settings in `.env`
- Verify backend is running: `curl http://localhost:8000/api/health`

**Ngrok issues**
- Verify auth token: `ngrok config add-authtoken YOUR_TOKEN`
- Check if ngrok is already running: `scripts\kill_ngrok.bat` (Windows)
- Restart ngrok tunnel

## Management Commands

### Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up --build -d

# Restart specific service
docker-compose restart backend
docker-compose restart frontend

# View running containers
docker-compose ps
```

### Cleanup

```bash
# Stop and remove volumes
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Full cleanup (Windows)
scripts\cleanup_all.bat
```

## Security Considerations

1. **Environment Variables**: Never commit `.env` files to version control
2. **Database Credentials**: Use strong passwords and rotate regularly
3. **Ngrok Tokens**: Keep auth tokens secure
4. **CORS Configuration**: Only allow necessary origins
5. **Rate Limiting**: Configured in nginx for API protection
6. **HTTPS**: Configure SSL certificates for production

## Production Deployment

### Recommendations

1. **Use HTTPS**: Configure SSL certificates
2. **Change Default Passwords**: Update all default passwords
3. **Firewall Rules**: Restrict access to necessary ports only
4. **Database Security**: Use strong passwords and limit database access
5. **API Security**: Implement authentication and rate limiting
6. **Monitoring**: Set up alerts for failed services
7. **Backups**: Regular database backups

### Scaling

For horizontal scaling, modify `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      replicas: 3
  frontend:
    deploy:
      replicas: 2
```

## Next Steps

1. **For Development**: Use `scripts\dev_all.bat` for fastest iteration
2. **For Testing**: Use Docker with `docker-compose up -d`
3. **For Production**: Follow security recommendations and configure HTTPS
4. **For External Access**: Use ngrok scripts for temporary access

For more details, see:
- [Development Guide](DEVELOPMENT.md) - Local development workflow
- [Architecture](ARCHITECTURE.md) - System design
- [API Documentation](API.md) - API endpoints
