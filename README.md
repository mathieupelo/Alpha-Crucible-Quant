# Alpha-Crucible - Quantitative Investment System

A comprehensive quantitative investment system focused on portfolio optimization, backtesting, and performance analysis. Features a modern React + FastAPI web application for visualizing and analyzing trading strategies.

## 🚀 Features

### **Core Functionality**
- **Portfolio Optimization**: CVXOPT-based portfolio weight optimization
- **Backtesting Engine**: Historical performance analysis with customizable parameters
- **Signal Integration**: Reads computed signals from external signal repository
- **Web Dashboard**: Interactive React-based visualization and analysis
- **REST API**: Comprehensive FastAPI backend with full documentation

### **Web Application**
- **Dashboard Overview**: Performance metrics, backtest history, and interactive charts
- **Backtest Analysis**: Detailed backtest visualization with portfolio compositions
- **Portfolio Management**: Universe creation, ticker validation, and position analysis
- **Real-time Data**: Live market data integration and signal monitoring
- **Professional UI**: Modern dark theme with responsive design

## 🏗️ Architecture

This system is part of a two-repository architecture:

### **Alpha-Crucible** (this repo)
- Portfolio optimization and backtesting
- Web application (React + FastAPI)
- Database management and API
- Signal reading from external repository

### **Signals Repository** (separate)
- Signal computation and data ingestion
- Writes to `signal_forge.signal_raw` table
- Handles alternative data sources

### **Key Components**

1. **Signal Reader** (`src/signals/`): Read computed signals from `signal_forge.signal_raw`
2. **Portfolio Solver** (`src/solver/`): Optimize portfolio weights using CVXOPT
3. **Backtesting Engine** (`src/backtest/`): Run historical performance analysis
4. **Database Layer** (`src/database/`): PostgreSQL database for portfolios, backtests, and results
5. **Web Application** (`frontend/`, `backend/`): User interface and API
6. **Utilities** (`src/utils/`): Common utilities and data fetching

## 🚀 Quick Start

### **Prerequisites**
- Node.js 18+ (for development)
- Python 3.11+ (for development)
- PostgreSQL database (Supabase recommended)
- Docker and Docker Compose (for production/testing)

### **⚡ Fastest: Local Development (Recommended for Daily Work)**

**Start both frontend and backend instantly with hot reload:**

```bash
# Windows
scripts\dev_all.bat

# Or start individually:
scripts\dev_backend.bat    # Terminal 1: Backend
scripts\dev_frontend.bat   # Terminal 2: Frontend
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

**Benefits:**
- ⚡ **Instant hot reload** (changes reflect in < 1 second)
- 🚀 **Fast startup** (< 5 seconds)
- 🔧 **Better debugging experience**
- 📝 **See [Development Guide](docs/DEVELOPMENT.md) for details**

**Initial Setup (one-time):**
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..
```

### **🐳 Docker Development (With Hot Reload)**

For Docker environment with code hot reload:

```bash
# Uses docker-compose.dev.yml with volume mounts
scripts\dev_docker.bat
```

### **🐳 Docker Production (Full Stack Testing)**

For production-like testing:

```bash
# Clone the repository
git clone <repository-url>
cd Alpha-Crucible-Quant

# Setup environment
cp .env_template .env
# Edit .env with your database credentials

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
# Nginx Proxy: http://localhost:8080

# For external access via ngrok (automatically starts Docker Desktop if needed)
scripts\ngrok\prepare_and_start_ngrok_final.bat
```

## 📊 Database Schema

The system uses PostgreSQL with the following key tables:

- `signal_raw`: Raw signal scores (read from signals repository)
- `portfolios`: Portfolio configurations and metadata
- `portfolio_positions`: Individual position weights
- `backtests`: Backtest run configurations
- `backtest_nav`: Daily NAV data for backtests
- `universes`: Ticker universe definitions
- `universe_tickers`: Ticker membership in universes
- `scores_combined`: Combined signal scores

## 🔧 API Endpoints

### **Backtests**
- `GET /api/backtests` - List all backtests
- `GET /api/backtests/{run_id}` - Get specific backtest
- `GET /api/backtests/{run_id}/metrics` - Get performance metrics
- `GET /api/backtests/{run_id}/portfolios` - Get portfolios
- `GET /api/backtests/{run_id}/nav` - Get NAV data

### **Portfolios**
- `GET /api/portfolios/{portfolio_id}` - Get portfolio details
- `GET /api/portfolios/{portfolio_id}/positions` - Get positions

### **Signals & Scores**
- `GET /api/signals` - Get raw signals
- `GET /api/scores` - Get combined scores

### **Universes**
- `GET /api/universes` - List all universes
- `POST /api/universes` - Create new universe
- `PUT /api/universes/{id}` - Update universe
- `DELETE /api/universes/{id}` - Delete universe

## 💻 Usage Examples

### **Read Signals**
```python
from src.signals import SignalReader
from datetime import date, timedelta

# Initialize signal reader
reader = SignalReader()

# Get signals for a date range
end_date = date.today()
start_date = end_date - timedelta(days=30)

signals_df = reader.get_signals(
    tickers=['AAPL', 'MSFT'],
    signal_names=['SENTIMENT_YT'],
    start_date=start_date,
    end_date=end_date
)
```

### **Run Backtest**
```python
from src.backtest import BacktestEngine

engine = BacktestEngine()
result = engine.run_backtest(
    tickers=['AAPL', 'MSFT', 'GOOGL'],
    signals=['RSI', 'SMA'],
    start_date='2024-01-01',
    end_date='2024-12-31'
)
```

### **API Usage**
```python
import requests

# Get all backtests
response = requests.get("http://localhost:8000/api/backtests")
backtests = response.json()

# Get specific backtest metrics
response = requests.get("http://localhost:8000/api/backtests/123/metrics")
metrics = response.json()
```

## 🧪 Testing

### **Run All Tests**
```bash
pytest tests/ -v --cov=src
```

### **Run Specific Test Suites**
```bash
# Solver tests
python -m pytest tests/unit/solver/ -v

# Signal tests
python -m pytest tests/unit/signals/ -v

# Integration tests
python -m pytest tests/integration/ -v
```

### **Comprehensive Test Suite**
```bash
python tests/run_comprehensive_tests.py
```

## 🛠️ Technology Stack

### **Backend**
- **FastAPI**: High-performance Python web framework
- **Pydantic**: Data validation and serialization
- **PostgreSQL**: Database with Supabase integration
- **Uvicorn**: ASGI server
- **CVXOPT**: Portfolio optimization

### **Frontend**
- **React 18**: Modern React with hooks
- **TypeScript**: Type-safe JavaScript
- **Material-UI**: Professional component library
- **Recharts**: Beautiful, responsive charts
- **React Query**: Data fetching and caching
- **Vite**: Fast build tool and dev server

### **Deployment**
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Nginx**: Reverse proxy and static file serving
- **Supabase**: Cloud PostgreSQL database

## 📁 Project Structure

```
Alpha-Crucible-Quant/
├── src/                    # Core quantitative analysis source code
│   ├── backtest/          # Backtesting engine and models
│   ├── database/          # Database operations and models
│   ├── signals/           # Signal reading and processing
│   ├── solver/            # Portfolio optimization
│   └── utils/             # Utility functions
├── backend/               # FastAPI backend application
│   ├── api/               # API route handlers
│   ├── models/            # Pydantic response models
│   ├── services/          # Business logic services
│   └── main.py            # FastAPI application entry point
├── frontend/              # React frontend application
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Main application pages
│   │   ├── services/      # API service layer
│   │   └── types/         # TypeScript type definitions
│   └── package.json       # Node.js dependencies
├── scripts/               # Operational scripts
├── tests/                 # Test files and demos
├── docs/                  # Detailed documentation
├── docker-compose.yml     # Docker orchestration
└── nginx.conf             # Nginx configuration
```

## 🔧 Configuration

### **Environment Variables**
```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:password@host:port/database
DB_HOST=your-supabase-host
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your-password
DB_NAME=postgres

# API Configuration
API_BASE_URL=http://localhost:8000

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:5173
```

## 📚 Documentation

Detailed documentation is available in the `docs/` directory:

- **[Architecture](docs/ARCHITECTURE.md)** - System design and component overview
- **[Directory Structure](docs/DIRECTORY_STRUCTURE.md)** - Codebase organization
- **[Usage Guide](docs/USAGE.md)** - Complete usage instructions
- **[API Documentation](docs/API.md)** - REST API endpoints
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Setup and deployment
- **[Docker Deployment](docs/DOCKER_DEPLOYMENT.md)** - Docker-specific deployment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/api/docs`
- Review the detailed documentation in `docs/`

---

**Alpha Crucible Quant** - Professional quantitative trading analysis made simple! 🚀