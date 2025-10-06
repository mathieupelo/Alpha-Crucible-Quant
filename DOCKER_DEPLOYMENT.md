# Alpha Crucible Quant - Docker Deployment Guide

This guide explains how to deploy the Alpha Crucible Quant application using Docker containers with external access via Ngrok.

## Prerequisites

1. **Docker Desktop** installed and running
2. **Ngrok** installed (for external access)
3. **Supabase** database credentials
4. **Environment configuration** set up

## Quick Start

### 1. Environment Setup

Copy the environment template and configure your settings:

```bash
# Copy the template
cp .env_template .env

# Edit the .env file with your actual values
# The template already contains your Supabase credentials
```

### 2. Deploy the Application

**Windows:**
```cmd
scripts\deploy.bat
```

**Linux/Mac:**
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### 3. Set Up External Access

**Windows:**
```cmd
scripts\start_ngrok.bat
```

**Linux/Mac:**
```bash
chmod +x scripts/start_ngrok.sh
./scripts/start_ngrok.sh
```

## Architecture

The deployment consists of three main services:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx Proxy   │────│  React Frontend │────│  FastAPI Backend│
│   (Port 80)     │    │   (Port 3000)   │    │   (Port 8000)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                               │
         │                                               │
         │              ┌─────────────────┐              │
         └──────────────│   Supabase      │──────────────┘
                        │   PostgreSQL    │
                        │   Database      │
                        └─────────────────┘
```

## Services

### 1. Backend (FastAPI)
- **Port:** 8000
- **Database:** Supabase PostgreSQL
- **Features:** REST API, CORS enabled, health checks

### 2. Frontend (React + Vite)
- **Port:** 3000
- **Features:** Production build, environment-based API configuration

### 3. Nginx (Reverse Proxy)
- **Port:** 80
- **Features:** Load balancing, rate limiting, security headers, gzip compression

## Configuration

### Environment Variables

The application uses the following environment variables:

```bash
# Database Configuration (Supabase PostgreSQL)
DATABASE_URL=postgresql://postgres:password@host:port/database
DB_HOST=your-supabase-host
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your-password
DB_NAME=postgres

# Ngrok Configuration
NGROK_AUTHTOKEN=your-ngrok-auth-token

# Application Configuration
NODE_ENV=production
PYTHONPATH=/app

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:5173

# API Configuration
API_BASE_URL=http://localhost:8000
```

### Database Schema

The application expects the following PostgreSQL tables:
- `signal_raw` - Raw signal data
- `scores_combined` - Combined signal scores
- `portfolios` - Portfolio configurations
- `portfolio_positions` - Portfolio holdings
- `backtests` - Backtest configurations
- `backtest_nav` - Backtest performance data
- `universes` - Universe definitions
- `universe_tickers` - Universe ticker lists

## External Access Setup

### Using Ngrok

1. **Install Ngrok:**
   - Download from [ngrok.com](https://ngrok.com)
   - Or use the provided setup script: `python scripts/setup_ngrok.py`

2. **Configure Authentication:**
   ```bash
   ngrok config add-authtoken YOUR_AUTH_TOKEN
   ```

3. **Start Tunnel:**
   ```bash
   # Windows
   scripts\start_ngrok.bat
   
   # Linux/Mac
   ./scripts/start_ngrok.sh
   ```

4. **Update CORS:**
   The script will automatically update your `.env` file with the public URL.

## Management Commands

### Docker Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f nginx

# Rebuild and restart
docker-compose up --build -d

# Check status
docker-compose ps
```

### Service Management

```bash
# Restart specific service
docker-compose restart backend
docker-compose restart frontend
docker-compose restart nginx

# Scale services (if needed)
docker-compose up -d --scale backend=2
```

## Monitoring and Health Checks

### Health Endpoints

- **Application Health:** `http://localhost/health`
- **Backend Health:** `http://localhost:8000/health`
- **API Documentation:** `http://localhost:8000/api/docs`

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f nginx

# View logs with timestamps
docker-compose logs -f -t
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check Supabase credentials in `.env`
   - Verify network connectivity
   - Check if Supabase instance is running

2. **CORS Errors**
   - Update `CORS_ORIGINS` in `.env` with your public URL
   - Restart the backend service

3. **Frontend Not Loading**
   - Check if frontend container is running
   - Verify API URL configuration
   - Check browser console for errors

4. **Ngrok Tunnel Issues**
   - Verify auth token is correct
   - Check if port 80 is available
   - Restart Ngrok tunnel

### Debug Commands

```bash
# Check container status
docker-compose ps

# Check container logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs nginx

# Check environment variables
docker-compose exec backend env | grep DB_
docker-compose exec frontend env | grep VITE_

# Test database connection
docker-compose exec backend python -c "from src.database.manager import DatabaseManager; db = DatabaseManager(); print('Connected:', db.connect())"

# Test API endpoints
curl http://localhost:8000/health
curl http://localhost/health
```

## Security Considerations

1. **Environment Variables:** Never commit `.env` files to version control
2. **Database Credentials:** Use strong passwords and rotate regularly
3. **Ngrok Tokens:** Keep auth tokens secure
4. **CORS Configuration:** Only allow necessary origins
5. **Rate Limiting:** Configured in nginx for API protection

## Performance Optimization

1. **Gzip Compression:** Enabled in nginx
2. **Static File Caching:** Configured for 1 year
3. **Database Connection Pooling:** Handled by psycopg2
4. **Container Resource Limits:** Can be added to docker-compose.yml

## Backup and Recovery

### Database Backup

```bash
# Backup Supabase database (using Supabase CLI)
supabase db dump --file backup.sql

# Or use pg_dump directly
pg_dump "postgresql://postgres:password@host:port/database" > backup.sql
```

### Container Backup

```bash
# Save container images
docker save alpha-crucible-backend > backend.tar
docker save alpha-crucible-frontend > frontend.tar
```

## Updates and Maintenance

### Updating the Application

1. **Pull latest changes:**
   ```bash
   git pull origin main
   ```

2. **Rebuild containers:**
   ```bash
   docker-compose up --build -d
   ```

3. **Update environment variables if needed:**
   ```bash
   # Edit .env file
   # Restart services
   docker-compose restart
   ```

### Monitoring

- Check container health regularly
- Monitor database performance
- Review application logs
- Monitor Ngrok tunnel status

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review container logs
3. Verify environment configuration
4. Check network connectivity

## License

This deployment configuration is part of the Alpha Crucible Quant project.