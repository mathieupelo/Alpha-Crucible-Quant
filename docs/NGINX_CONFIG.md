# Nginx Configuration Files

This project uses two nginx configuration files for different purposes:

## 1. Root `nginx.conf` (Reverse Proxy)

**Location:** `nginx.conf` (repository root)

**Purpose:** Reverse proxy for Docker Compose setup that routes traffic between frontend and backend services.

**Usage:**
- Mounted in `docker-compose.yml` and `docker-compose.dev.yml` for the nginx service
- Routes `/api/` requests to the backend container
- Routes all other requests to the frontend container
- Provides rate limiting, security headers, and gzip compression

**Configuration:**
- Listens on port 80 (mapped to 8080 on host)
- Proxies to `backend:8000` for API requests
- Proxies to `frontend:3000` for frontend requests

## 2. Frontend `frontend/nginx.conf` (Frontend Server)

**Location:** `frontend/nginx.conf`

**Purpose:** Nginx server configuration for the frontend container that serves the built React application.

**Usage:**
- Copied into frontend Docker container during build (see `frontend/Dockerfile`)
- Serves static files from `/usr/share/nginx/html` (built React app)
- Handles client-side routing with `try_files`
- Proxies `/api/` requests to backend (when frontend runs standalone)

**Configuration:**
- Listens on port 3000
- Serves static assets with caching
- Handles SPA routing (all routes fallback to `index.html`)

## When Each Is Used

- **Root nginx.conf**: Used when running full stack with Docker Compose (includes nginx reverse proxy service)
- **Frontend nginx.conf**: Used when frontend container runs standalone or in production builds

Both configurations are necessary and serve different roles in the architecture.

