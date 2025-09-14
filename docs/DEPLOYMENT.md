# Alpha Crucible Quant Deployment Guide

## Overview

This guide covers different deployment options for the Alpha Crucible Quant system, from local development to production deployment.

## Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Memory**: Minimum 4GB RAM, recommended 8GB+
- **Storage**: Minimum 10GB free space
- **Network**: Internet connection for data fetching

### Software Requirements
- **Docker**: Version 20.10+ with Docker Compose
- **Node.js**: Version 18+ (for development)
- **Python**: Version 3.9+ (for development)
- **MySQL**: Version 8.0+ (for local development)

## Deployment Options

### 1. Docker Compose (Recommended)

The easiest way to deploy the entire system is using Docker Compose.

#### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd Alpha-Crucible-Quant

# Create environment file
cp env.example .env
# Edit .env with your database credentials

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

#### Services
- **MySQL**: Database server (port 3306)
- **Backend**: FastAPI application (port 8000)
- **Frontend**: React application (port 3000)
- **Nginx**: Reverse proxy (port 80)

#### Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Database**: localhost:3306

### 2. Local Development Setup

For development and testing, you can run services locally.

#### Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt

# Setup database
python scripts/setup_database.py

# Start backend
cd backend
python main.py
```

#### Frontend Setup
```bash
# Install Node.js dependencies
cd frontend
npm install

# Start development server
npm run dev
```

#### Database Setup
```bash
# Install MySQL locally
# Create database
mysql -u root -p
CREATE DATABASE signal_forge;

# Run setup script
python scripts/setup_database.py
```

### 3. Production Deployment

#### Docker Production Setup
```bash
# Create production environment file
cp env.example .env.production

# Update environment variables for production
# DB_PASSWORD=secure_password
# LOG_LEVEL=WARNING

# Start production services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

#### Nginx Configuration
The system includes an Nginx configuration for production:

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }
    
    upstream frontend {
        server frontend:3000;
    }
    
    server {
        listen 80;
        
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Database Configuration
DB_HOST=mysql
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_secure_password
DB_NAME=signal_forge

# yfinance Configuration
YFINANCE_TIMEOUT=10
YFINANCE_RETRIES=3

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/alpha_crucible.log

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Frontend Configuration
VITE_API_URL=http://localhost:8000
```

### Database Configuration

#### MySQL Setup
```sql
-- Create database
CREATE DATABASE signal_forge;

-- Create user (optional)
CREATE USER 'quant_user'@'%' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON signal_forge.* TO 'quant_user'@'%';
FLUSH PRIVILEGES;
```

#### Database Schema
The system automatically creates the required tables:
- `signal_scores`: Signal calculation results
- `portfolios`: Portfolio configurations
- `backtest_results`: Backtest performance data
- `portfolio_values`: Daily portfolio values
- `portfolio_weights`: Portfolio weight allocations
- `signal_definitions`: Signal parameter definitions

## Monitoring and Logging

### Log Files
- **Backend Logs**: `logs/alpha_crucible.log`
- **Database Logs**: Available in Docker logs
- **Nginx Logs**: Available in Docker logs

### Health Checks
```bash
# Check backend health
curl http://localhost:8000/health

# Check database connection
docker-compose exec backend python -c "from src.database import DatabaseManager; print('DB OK' if DatabaseManager().connect() else 'DB Error')"

# Check frontend
curl http://localhost:3000
```

### Monitoring Commands
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mysql

# Check resource usage
docker stats

# Check service status
docker-compose ps
```

## Backup and Recovery

### Database Backup
```bash
# Create backup
docker-compose exec mysql mysqldump -u root -p signal_forge > backup.sql

# Restore backup
docker-compose exec -T mysql mysql -u root -p signal_forge < backup.sql
```

### Data Backup
```bash
# Backup data directory
tar -czf data_backup.tar.gz data/

# Restore data
tar -xzf data_backup.tar.gz
```

### Configuration Backup
```bash
# Backup configuration
cp .env .env.backup
cp docker-compose.yml docker-compose.yml.backup
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed
```bash
# Check if MySQL is running
docker-compose ps mysql

# Check MySQL logs
docker-compose logs mysql

# Restart MySQL
docker-compose restart mysql
```

#### 2. Backend Not Starting
```bash
# Check backend logs
docker-compose logs backend

# Check Python dependencies
docker-compose exec backend pip list

# Restart backend
docker-compose restart backend
```

#### 3. Frontend Not Loading
```bash
# Check frontend logs
docker-compose logs frontend

# Check Node.js dependencies
docker-compose exec frontend npm list

# Restart frontend
docker-compose restart frontend
```

#### 4. Port Conflicts
```bash
# Check port usage
netstat -tulpn | grep :3000
netstat -tulpn | grep :8000
netstat -tulpn | grep :3306

# Stop conflicting services
sudo systemctl stop apache2  # if using port 80
sudo systemctl stop mysql    # if using port 3306
```

### Performance Issues

#### 1. Slow Database Queries
```bash
# Check database performance
docker-compose exec mysql mysql -u root -p
SHOW PROCESSLIST;
SHOW STATUS LIKE 'Slow_queries';
```

#### 2. High Memory Usage
```bash
# Check memory usage
docker stats

# Restart services
docker-compose restart
```

#### 3. Slow API Responses
```bash
# Check backend logs for errors
docker-compose logs backend | grep ERROR

# Check database connection pool
docker-compose exec backend python -c "from src.database import DatabaseManager; db = DatabaseManager(); print(db.get_connection_info())"
```

## Security Considerations

### Production Security
1. **Change Default Passwords**: Update all default passwords
2. **Use HTTPS**: Configure SSL certificates for production
3. **Firewall Rules**: Restrict access to necessary ports only
4. **Database Security**: Use strong passwords and limit database access
5. **API Security**: Implement authentication and rate limiting

### Environment Security
```bash
# Secure environment file
chmod 600 .env

# Use secrets management
# Consider using Docker secrets or external secret management
```

## Scaling

### Horizontal Scaling
```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  backend:
    deploy:
      replicas: 3
  frontend:
    deploy:
      replicas: 2
```

### Load Balancing
```nginx
# nginx.conf for load balancing
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}
```

## Maintenance

### Regular Maintenance Tasks
1. **Database Cleanup**: Remove old data periodically
2. **Log Rotation**: Rotate log files to prevent disk space issues
3. **Security Updates**: Keep Docker images and dependencies updated
4. **Backup Verification**: Test backup and recovery procedures

### Update Procedures
```bash
# Update application
git pull origin main

# Rebuild and restart
docker-compose up --build -d

# Verify update
docker-compose ps
curl http://localhost:8000/health
```

## Support

### Getting Help
1. **Check Logs**: Always check logs first
2. **Documentation**: Review this guide and API documentation
3. **GitHub Issues**: Report issues on the project repository
4. **Community**: Join the project community for support

### Useful Commands
```bash
# System status
docker-compose ps
docker-compose logs --tail=50

# Restart services
docker-compose restart
docker-compose restart backend frontend

# Clean up
docker-compose down
docker system prune -f

# Full reset
docker-compose down -v
docker-compose up --build -d
```

## Conclusion

The Alpha Crucible Quant system is designed to be easily deployable and maintainable. The Docker Compose setup provides a simple way to get started, while the modular architecture allows for flexible deployment options. Follow this guide for successful deployment and operation of the system.
