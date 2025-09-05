# Directory Structure

This document explains the organization of the Alpha Crucible Quant codebase.

## Overview

The project follows a clear separation between source code, web application, operational scripts, and tests:

```
Alpha-Crucible-Quant/
├── src/                    # Core quantitative analysis source code
├── backend/                # FastAPI backend application
├── frontend/               # React frontend application
├── scripts/                # Operational scripts
├── tests/                  # Test files and demos
├── docs/                   # Documentation
├── data/                   # Data files
├── config/                 # Configuration files
├── temp/                   # Temporary files
├── docker-compose.yml      # Docker orchestration
└── nginx.conf              # Nginx configuration
```

## Directory Purposes

### `src/` - Core Source Code
Contains the main quantitative analysis code organized by functionality:

```
src/
├── backtest/              # Backtesting engine and models
├── database/              # Database operations and models
├── signals/               # Signal calculation and processing
├── solver/                # Portfolio optimization
└── utils/                 # Utility functions
```

### `backend/` - FastAPI Backend
Contains the REST API backend application:

```
backend/
├── api/                   # API route handlers
│   ├── backtests.py       # Backtest endpoints
│   ├── portfolios.py      # Portfolio endpoints
│   ├── signals.py         # Signal endpoints
│   └── nav.py             # NAV endpoints
├── models/                # Pydantic response models
├── services/              # Business logic services
│   └── database_service.py # Database abstraction
├── main.py                # FastAPI application entry point
├── requirements.txt       # Python dependencies
└── Dockerfile             # Backend container configuration
```

### `frontend/` - React Frontend
Contains the React web application:

```
frontend/
├── src/                   # React source code
│   ├── components/        # React components
│   │   ├── cards/         # Metric card components
│   │   ├── charts/        # Chart components
│   │   ├── common/        # Common components
│   │   └── tables/        # Table components
│   ├── pages/             # Page components
│   ├── services/          # API service layer
│   ├── types/             # TypeScript type definitions
│   ├── utils/             # Utility functions
│   └── styles/            # Styling files
├── public/                # Static assets
├── dist/                  # Built application
├── package.json           # Node.js dependencies
├── tsconfig.json          # TypeScript configuration
├── vite.config.ts         # Vite build configuration
└── Dockerfile             # Frontend container configuration
```

### `scripts/` - Operational Scripts
Contains scripts for running the system operations:

- **`run_backtest.py`** - Run backtests with various configurations
- **`calculate_signals.py`** - Calculate and store signal scores
- **`setup_database.py`** - Initialize database schema and tables
- **`query_portfolio_data.py`** - Query and analyze stored portfolio data

These are the main entry points for system operations.

### `tests/` - Test Files and Demos
Contains all testing and demonstration code:

- **`test_*.py`** - Unit and integration tests
- **`demo_*.py`** - Demonstration scripts
- **`conftest.py`** - pytest configuration
- **`__init__.py`** - Test package initialization

#### Test Files:
- **`test_database.py`** - Database functionality tests
- **`test_signals.py`** - Signal calculation tests
- **`test_utils.py`** - Utility function tests
- **`test_runner.py`** - Test runner and integration tests
- **`test_equal_weight_benchmark.py`** - Equal-weight benchmark tests
- **`test_forward_fill.py`** - Forward-fill functionality tests
- **`test_portfolio_storage.py`** - Portfolio storage tests

#### Demo Files:
- **`demo_forward_fill.py`** - Forward-fill demonstration

### `docs/` - Documentation
Contains all project documentation:

- **`ARCHITECTURE.md`** - System architecture overview
- **`USAGE.md`** - Usage instructions
- **`PORTFOLIO_STORAGE.md`** - Portfolio storage documentation
- **`FORWARD_FILL_SIGNALS.md`** - Forward-fill signals documentation
- **`EQUAL_WEIGHT_BENCHMARK.md`** - Equal-weight benchmark documentation
- **`DIRECTORY_STRUCTURE.md`** - This file

### `data/` - Data Files
Contains data files and datasets used by the system.

### `config/` - Configuration Files
Contains configuration files and settings.

### `temp/` - Temporary Files
Contains temporary files generated during operations.

## File Naming Conventions

### Scripts (`scripts/`)
- Use descriptive names: `run_backtest.py`, `calculate_signals.py`
- No prefixes needed (they are operational scripts)
- Should be executable and have proper shebang lines

### Tests (`tests/`)
- Use `test_` prefix for actual tests: `test_database.py`
- Use `demo_` prefix for demonstrations: `demo_forward_fill.py`
- Follow pytest naming conventions

### Source Code (`src/`)
- Use descriptive module names: `backtest`, `database`, `signals`
- Follow Python package conventions
- Include `__init__.py` files for proper imports

## Running the Application

### Web Application (Recommended)
```bash
# Start all services with Docker Compose
docker-compose up -d

# Or start individual services
docker-compose up mysql backend frontend nginx

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
```

### Development Mode
```bash
# Backend development
cd backend
pip install -r requirements.txt
python main.py

# Frontend development
cd frontend
npm install
npm run dev

# Database setup
python scripts/setup_database.py
```

### Operational Scripts
```bash
# Run a backtest
python scripts/run_backtest.py

# Calculate signals
python scripts/calculate_signals.py

# Setup database
python scripts/setup_database.py

# Query portfolio data
python scripts/query_portfolio_data.py
```

### Tests and Demos
```bash
# Run all tests
python -m pytest tests/

# Run specific test
python tests/test_database.py

# Run demo
python tests/demo_forward_fill.py

# Run test with pytest
pytest tests/test_signals.py
```

## Web Application Components

### Frontend Components
- **Dashboard**: Main overview with key metrics and charts
- **BacktestDetail**: Detailed analysis of individual backtests
- **PerformanceChart**: Interactive performance visualization
- **PortfolioDetail**: Portfolio composition and analysis
- **MetricCard**: Reusable metric display components

### Backend API Endpoints
- **Backtests**: `/api/backtests` - Backtest management and retrieval
- **Portfolios**: `/api/portfolios` - Portfolio data and positions
- **Signals**: `/api/signals` - Signal data and scores
- **NAV**: `/api/backtests/{run_id}/nav` - Net Asset Value data

### Database Integration
- **DatabaseService**: Abstraction layer for database operations
- **Response Models**: Pydantic models for API responses
- **Error Handling**: Comprehensive error handling and logging

## Best Practices

### Web Application
- **Frontend**: Use TypeScript for type safety, Material-UI for consistency
- **Backend**: Follow RESTful principles, use Pydantic for validation
- **API Design**: Consistent response formats, proper HTTP status codes
- **Error Handling**: User-friendly error messages, comprehensive logging

### Scripts Directory
- Keep only operational scripts
- Each script should have a clear purpose
- Include proper error handling and logging
- Should be executable from command line

### Tests Directory
- Include all test files and demos
- Use proper test naming conventions
- Include both unit tests and integration tests
- Demos should be educational and well-documented

### Source Code
- Organize by functionality
- Keep modules focused and cohesive
- Include proper docstrings and type hints
- Follow Python best practices

## Migration Notes

The following files were moved from `scripts/` to `tests/` for better organization:

- `test_equal_weight_benchmark.py` → `tests/test_equal_weight_benchmark.py`
- `test_forward_fill.py` → `tests/test_forward_fill.py`
- `test_portfolio_storage.py` → `tests/test_portfolio_storage.py`
- `demo_forward_fill.py` → `tests/demo_forward_fill.py`

This separation makes the codebase cleaner and follows standard Python project conventions.
