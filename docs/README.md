# Alpha Crucible Quant Documentation

Welcome to the Alpha Crucible Quant documentation! This comprehensive guide covers all aspects of the quantitative investment system, from basic setup to advanced features.

## 📚 Documentation Overview

### Core Documentation
- **[Architecture](ARCHITECTURE.md)** - System design and component overview
- **[Directory Structure](DIRECTORY_STRUCTURE.md)** - Codebase organization and file structure
- **[Usage Guide](USAGE.md)** - Complete usage instructions and examples
- **[API Documentation](API.md)** - REST API endpoints and integration
- **[Deployment Guide](DEPLOYMENT.md)** - Setup and deployment instructions

### Feature Documentation
- **[Portfolio Storage](PORTFOLIO_STORAGE.md)** - Portfolio data storage and management
- **[Forward Fill Signals](FORWARD_FILL_SIGNALS.md)** - Signal forward-fill functionality
- **[Equal Weight Benchmark](EQUAL_WEIGHT_BENCHMARK.md)** - Equal-weight benchmark implementation

## 🚀 Quick Start

### Web Application (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd Alpha-Crucible-Quant

# Setup environment
cp env.example .env
# Edit .env with your database credentials

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
```

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..

# Setup database
python scripts/setup_database.py

# Start services
# Terminal 1: Backend
cd backend && python main.py

# Terminal 2: Frontend
cd frontend && npm run dev
```

## 🏗️ System Architecture

Alpha Crucible Quant is a full-stack quantitative investment system with:

### Frontend (React + TypeScript)
- **Dashboard**: Interactive performance monitoring
- **Backtest Analysis**: Detailed backtest visualization
- **Portfolio Management**: Portfolio composition and analysis
- **Real-time Updates**: Live data and performance metrics

### Backend (FastAPI + Python)
- **REST API**: Comprehensive API endpoints
- **Database Integration**: MySQL data persistence
- **Signal Processing**: Advanced signal calculation and combination
- **Portfolio Optimization**: CVXOPT-based portfolio optimization

### Core Engine (Python)
- **Signal System**: RSI, SMA, MACD, and custom signals
- **Backtesting Engine**: Historical performance analysis
- **Portfolio Solver**: Mean-variance optimization
- **Data Management**: Price fetching and data processing

## 📊 Key Features

### Quantitative Analysis
- **Multiple Signals**: RSI, SMA, MACD with customizable parameters
- **Signal Combination**: Equal-weight and custom weighting schemes
- **Portfolio Optimization**: Mean-variance optimization with constraints
- **Risk Management**: Comprehensive risk metrics and analysis

### Backtesting
- **Historical Analysis**: Multi-year backtesting capabilities
- **Performance Metrics**: Sharpe ratio, alpha, beta, drawdown, and more
- **Benchmark Comparison**: SPY and equal-weight benchmark options
- **Transaction Costs**: Realistic cost modeling

### Web Interface
- **Interactive Dashboard**: Real-time performance monitoring
- **Data Visualization**: Interactive charts and graphs
- **Portfolio Analysis**: Detailed portfolio composition views
- **API Integration**: Programmatic access to all functionality

### Data Management
- **Real-time Data**: yfinance integration for live stock prices
- **Historical Storage**: Comprehensive data persistence
- **Forward Fill**: Intelligent handling of missing data
- **Data Quality**: Robust data validation and error handling

## 🔧 Configuration

### Environment Variables
```bash
# Database Configuration
DB_HOST=mysql
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_secure_password
DB_NAME=signal_forge

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Frontend Configuration
VITE_API_URL=http://localhost:8000
```

### Database Schema
The system automatically creates the required database tables:
- `signal_scores` - Signal calculation results
- `portfolios` - Portfolio configurations
- `backtest_results` - Backtest performance data
- `portfolio_values` - Daily portfolio values
- `portfolio_weights` - Portfolio weight allocations

## 📈 Usage Examples

### Running a Backtest
```python
from src.backtest import BacktestEngine, BacktestConfig
from datetime import date

# Create backtest configuration
config = BacktestConfig(
    start_date=date(2024, 1, 1),
    end_date=date(2024, 12, 31),
    initial_capital=100000.0,
    rebalancing_frequency='monthly',
    use_equal_weight_benchmark=True
)

# Initialize and run backtest
engine = BacktestEngine()
result = engine.run_backtest(
    tickers=['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'],
    signals=['RSI', 'SMA', 'MACD'],
    config=config
)

print(f"Total Return: {result.total_return:.2%}")
print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
```

### Using the API
```python
import requests

# Get all backtests
response = requests.get("http://localhost:8000/api/backtests")
backtests = response.json()

# Get specific backtest details
backtest_id = "backtest_123"
response = requests.get(f"http://localhost:8000/api/backtests/{backtest_id}")
backtest = response.json()
```

### Web Application
Access the web interface at http://localhost:3000 to:
- View performance dashboards
- Analyze backtest results
- Explore portfolio compositions
- Monitor real-time metrics

## 🐳 Deployment

### Docker Compose (Recommended)
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Deployment
```bash
# Production environment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test modules
pytest tests/test_signals.py -v
pytest tests/test_database.py -v
pytest tests/test_utils.py -v
```

### Test Coverage
```bash
# Generate coverage report
pytest --cov=src tests/
```

## 📚 API Reference

### Core Endpoints
- `GET /api/backtests` - List all backtests
- `GET /api/backtests/{run_id}` - Get specific backtest
- `GET /api/portfolios/{portfolio_id}` - Get portfolio details
- `GET /api/signals` - Get signal data
- `GET /api/backtests/{run_id}/nav` - Get NAV data

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## 🔍 Monitoring and Logging

### Health Checks
```bash
# Check backend health
curl http://localhost:8000/health

# Check database connection
docker-compose exec backend python -c "from src.database import DatabaseManager; print('DB OK' if DatabaseManager().connect() else 'DB Error')"
```

### Logs
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 🛠️ Development

### Adding New Signals
1. Create a new signal class inheriting from `SignalBase`
2. Implement required methods (`calculate`, `get_min_lookback_period`, etc.)
3. Register the signal in the signal registry
4. Add tests for the new signal

### Adding New API Endpoints
1. Create new route in appropriate API module
2. Add response models in `backend/models/`
3. Implement business logic in `backend/services/`
4. Add tests for the new endpoint

### Frontend Development
1. Create new components in `frontend/src/components/`
2. Add new pages in `frontend/src/pages/`
3. Update routing in `frontend/src/App.tsx`
4. Add TypeScript types in `frontend/src/types/`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request

## 📞 Support

### Getting Help
1. **Documentation**: Check this documentation first
2. **API Docs**: Use the interactive API documentation
3. **Logs**: Check application logs for errors
4. **GitHub Issues**: Report issues on the project repository

### Common Issues
- **Database Connection**: Check MySQL service and credentials
- **Port Conflicts**: Ensure ports 3000, 8000, and 3306 are available
- **Dependencies**: Verify all dependencies are installed correctly
- **Environment**: Check environment variable configuration

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **yfinance**: For real-time stock price data
- **CVXOPT**: For portfolio optimization
- **FastAPI**: For the REST API framework
- **React**: For the frontend framework
- **Material-UI**: For the UI component library

---

For more detailed information, please refer to the individual documentation files linked above. Each document provides comprehensive coverage of specific aspects of the Alpha Crucible Quant system.
