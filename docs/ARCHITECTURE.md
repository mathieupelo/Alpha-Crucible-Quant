# Alpha Crucible Quant Architecture

## Overview

Alpha Crucible Quant is a comprehensive quantitative investment system that combines signal generation, portfolio optimization, backtesting, and web-based visualization in a unified platform. This document describes the architecture, design decisions, and key components of the full-stack application.

## Architecture Principles

### 1. Full-Stack Architecture
- **Frontend**: React-based web dashboard with Material-UI components
- **Backend**: FastAPI REST API with comprehensive endpoints
- **Database**: MySQL for persistent data storage
- **Containerization**: Docker-based deployment with docker-compose

### 2. Unified Repository
- **Single Source of Truth**: All components in one repository
- **Simplified Dependencies**: No complex inter-repository dependencies
- **Easy Deployment**: Single installation and configuration

### 3. Local-First Design
- **Local Database**: MySQL hosted on your machine (127.0.0.1:3306)
- **Real-time Data**: yfinance integration for live stock prices
- **No External Dependencies**: No reliance on external services

### 4. DataFrame-Centric Communication
- **Pandas Integration**: All data operations use pandas DataFrames
- **Type Safety**: Strong typing with dataclasses and type hints
- **Memory Efficiency**: Optimized data structures and operations

### 5. Modular Design
- **Separation of Concerns**: Clear boundaries between components
- **Extensible**: Easy to add new signals, solvers, or strategies
- **Testable**: Comprehensive unit tests for all modules

## System Components

### 1. Signal System (`src/signals/`)

**Purpose**: Calculate investment signals from alternative data

**Key Classes**:
- `SignalBase`: Abstract base class for all signals
- `RSISignal`: Relative Strength Index implementation
- `SMASignal`: Simple Moving Average implementation
- `MACDSignal`: Moving Average Convergence Divergence implementation
- `SignalCalculator`: Orchestrates signal calculation
- `SignalRegistry`: Manages available signals

**Design Decisions**:
- **Abstract Base Class**: Ensures consistent interface across all signals
- **Parameterized Signals**: Each signal can be configured with different parameters
- **Validation**: Built-in data validation and error handling
- **Caching**: In-memory caching for performance

### 2. Portfolio Solver (`src/solver/`)

**Purpose**: Optimize portfolio weights using CVXOPT

**Key Classes**:
- `PortfolioSolver`: Main optimization engine
- `SolverConfig`: Configuration for optimization parameters
- `Portfolio`: Portfolio data structure with positions and metadata

**Design Decisions**:
- **CVXOPT Integration**: Proven optimization library for portfolio problems
- **Risk Aversion**: Configurable risk-return tradeoff
- **Constraints**: Flexible weight constraints (long-only, max weight, etc.)
- **Validation**: Portfolio validation and error handling

### 3. Backtesting Engine (`src/backtest/`)

**Purpose**: Run historical performance analysis

**Key Classes**:
- `BacktestEngine`: Main backtesting orchestrator
- `BacktestConfig`: Configuration for backtesting parameters
- `BacktestResult`: Comprehensive results with performance metrics

**Design Decisions**:
- **Monthly Rebalancing**: Configurable rebalancing frequency
- **Transaction Costs**: Realistic cost modeling
- **Benchmark Comparison**: Built-in benchmark analysis
- **Performance Metrics**: Comprehensive risk and return metrics

### 4. Database Layer (`src/database/`)

**Purpose**: Simplified MySQL database operations

**Key Classes**:
- `DatabaseManager`: Main database interface
- `SignalScore`: Signal score data model
- `Portfolio`: Portfolio data model
- `BacktestResult`: Backtest result data model

**Design Decisions**:
- **Simplified Schema**: Only essential data stored
- **DataFrame Integration**: All operations return pandas DataFrames
- **Connection Management**: Automatic connection handling
- **Error Handling**: Robust error handling and logging

### 5. Web Application (`frontend/` and `backend/`)

**Purpose**: Modern web interface for system interaction and visualization

**Frontend Components**:
- `App.tsx`: Main React application with routing
- `Dashboard.tsx`: Main dashboard with performance metrics
- `BacktestDetail.tsx`: Detailed backtest analysis page
- `PerformanceChart.tsx`: Interactive performance visualization
- `PortfolioDetail.tsx`: Portfolio composition analysis
- `MetricCard.tsx`: Reusable metric display components

**Backend Components**:
- `main.py`: FastAPI application with CORS and error handling
- `api/backtests.py`: Backtest data endpoints
- `api/portfolios.py`: Portfolio data endpoints
- `api/signals.py`: Signal data endpoints
- `api/nav.py`: NAV (Net Asset Value) endpoints
- `services/database_service.py`: Database abstraction layer

**Design Decisions**:
- **React + TypeScript**: Type-safe frontend development
- **Material-UI**: Consistent, professional UI components
- **FastAPI**: High-performance async API with automatic documentation
- **RESTful Design**: Clean API endpoints with proper HTTP methods
- **CORS Support**: Cross-origin requests for development and production
- **Error Handling**: Comprehensive error responses and logging

### 6. Utilities (`src/utils/`)

**Purpose**: Common utilities and data fetching

**Key Classes**:
- `PriceFetcher`: yfinance integration for stock prices
- `DateUtils`: Date and time utilities

**Design Decisions**:
- **yfinance Integration**: Real-time stock price fetching
- **Caching**: In-memory price caching for performance
- **Fallback Mechanisms**: Graceful handling of missing data
- **Date Utilities**: Comprehensive date manipulation functions

## Data Flow

### 1. Signal Calculation Flow
```
Price Data (yfinance) → Signal Calculator → Signal Scores → Database
```

### 2. Portfolio Optimization Flow
```
Signal Scores → Signal Combination → Portfolio Solver → Portfolio Weights
```

### 3. Backtesting Flow
```
Historical Data → Signal Calculation → Portfolio Optimization → Performance Analysis
```

### 4. Web Application Flow
```
Frontend (React) → Backend API (FastAPI) → Database Service → MySQL Database
```

### 5. Real-time Data Flow
```
User Request → Frontend → API Endpoint → Database Query → Response → UI Update
```

## Database Schema

### Tables

#### `signal_scores`
- `id`: Primary key
- `ticker`: Stock ticker symbol
- `signal_id`: Signal identifier
- `date`: Date of calculation
- `score`: Signal score (-1 to 1)
- `created_at`: Timestamp

#### `portfolios`
- `portfolio_id`: Primary key
- `creation_date`: Portfolio creation date
- `weights`: JSON string of portfolio weights
- `signal_weights`: JSON string of signal weights
- `risk_aversion`: Risk aversion parameter
- `max_weight`: Maximum weight constraint
- `created_at`: Timestamp

#### `backtest_results`
- `backtest_id`: Primary key
- `start_date`: Backtest start date
- `end_date`: Backtest end date
- `tickers`: Comma-separated list of tickers
- `signals`: Comma-separated list of signals
- `total_return`: Total return
- `annualized_return`: Annualized return
- `sharpe_ratio`: Sharpe ratio
- `max_drawdown`: Maximum drawdown
- `volatility`: Volatility
- `alpha`: Alpha vs benchmark
- `information_ratio`: Information ratio
- `execution_time_seconds`: Execution time
- `created_at`: Timestamp

#### `signal_definitions`
- `signal_id`: Primary key
- `name`: Human-readable signal name
- `parameters`: JSON string of signal parameters
- `enabled`: Whether signal is enabled
- `created_at`: Timestamp

## Configuration

### Environment Variables
- `DB_HOST`: Database host (default: 127.0.0.1)
- `DB_PORT`: Database port (default: 3306)
- `DB_USER`: Database username (default: root)
- `DB_PASSWORD`: Database password
- `DB_NAME`: Database name (default: quant_project)
- `YFINANCE_TIMEOUT`: yfinance timeout (default: 10)
- `YFINANCE_RETRIES`: yfinance retries (default: 3)

### Configuration Files
- `env.example`: Environment variable template
- `requirements.txt`: Python dependencies
- `pyproject.toml`: Project configuration

## Error Handling

### 1. Data Validation
- **Input Validation**: All inputs validated before processing
- **Type Checking**: Strong typing with type hints
- **Range Checking**: Signal scores, weights, and dates validated

### 2. Error Recovery
- **Graceful Degradation**: System continues with partial data
- **Retry Mechanisms**: Automatic retry for transient failures
- **Fallback Strategies**: Alternative data sources when primary fails

### 3. Logging
- **Comprehensive Logging**: All operations logged with appropriate levels
- **Error Tracking**: Detailed error information for debugging
- **Performance Monitoring**: Execution time and resource usage tracking

## Performance Considerations

### 1. Caching
- **Price Caching**: In-memory caching of stock prices
- **Signal Caching**: Caching of calculated signals
- **Database Caching**: Connection pooling and query optimization

### 2. Optimization
- **Vectorized Operations**: Pandas and NumPy for efficient computation
- **Batch Processing**: Bulk operations for database and API calls
- **Memory Management**: Efficient memory usage and garbage collection

### 3. Scalability
- **Modular Design**: Easy to scale individual components
- **Configuration**: Tunable parameters for different use cases
- **Monitoring**: Built-in performance monitoring and metrics

## Security Considerations

### 1. Data Protection
- **Environment Variables**: Sensitive data in environment variables
- **Database Security**: Secure database connections
- **Input Sanitization**: All inputs sanitized and validated

### 2. Access Control
- **Local Database**: Database hosted locally for security
- **No External Services**: No reliance on external APIs for sensitive data
- **Audit Trail**: Comprehensive logging for audit purposes

## Testing Strategy

### 1. Unit Tests
- **Comprehensive Coverage**: Tests for all modules and functions
- **Edge Cases**: Testing of boundary conditions and error cases
- **Mocking**: Extensive use of mocks for external dependencies

### 2. Integration Tests
- **End-to-End Testing**: Full workflow testing
- **Database Testing**: Database operations testing
- **API Testing**: yfinance integration testing

### 3. Performance Tests
- **Load Testing**: Testing under various load conditions
- **Memory Testing**: Memory usage and leak detection
- **Speed Testing**: Performance benchmarking

## Web Application Architecture

### Frontend Architecture
- **React 18**: Modern React with hooks and functional components
- **TypeScript**: Type-safe development with comprehensive type definitions
- **Material-UI**: Professional component library with dark theme
- **React Router**: Client-side routing for single-page application
- **React Query**: Data fetching and caching with automatic refetching
- **Recharts**: Interactive data visualization and charting
- **Vite**: Fast build tool and development server

### Backend Architecture
- **FastAPI**: Modern Python web framework with automatic API documentation
- **Pydantic**: Data validation and serialization
- **SQLAlchemy**: Database ORM for MySQL operations
- **CORS**: Cross-origin resource sharing for frontend integration
- **Logging**: Comprehensive logging with different levels
- **Error Handling**: Global exception handling with proper HTTP status codes

### API Design
- **RESTful Endpoints**: Standard HTTP methods and status codes
- **Pagination**: Efficient data pagination for large datasets
- **Filtering**: Query parameter-based filtering
- **Response Models**: Consistent response structure with Pydantic models
- **Documentation**: Automatic OpenAPI/Swagger documentation

## Deployment

### 1. Local Development
- **Virtual Environment**: Isolated Python environment
- **Database Setup**: Local MySQL database
- **Configuration**: Environment variable configuration
- **Hot Reload**: Frontend and backend hot reloading for development

### 2. Docker Deployment
- **Multi-container Setup**: Separate containers for frontend, backend, database, and nginx
- **Docker Compose**: Orchestrated deployment with single command
- **Volume Mounting**: Persistent data storage and code synchronization
- **Network Isolation**: Secure container networking

### 3. Production Deployment
- **Nginx Reverse Proxy**: Load balancing and SSL termination
- **Container Orchestration**: Docker Compose for production
- **Monitoring**: Performance and error monitoring
- **Backup**: Database backup and recovery procedures

## Future Enhancements

### 1. Additional Signals
- **Sentiment Analysis**: News and social media sentiment
- **Technical Indicators**: Additional technical analysis signals
- **Fundamental Analysis**: Financial statement analysis

### 2. Advanced Features
- **Machine Learning**: ML-based signal generation
- **Risk Management**: Advanced risk models
- **Real-time Trading**: Live trading integration

### 3. Infrastructure
- **Cloud Deployment**: AWS/Azure deployment options
- **API Interface**: REST API for external access
- **Web Interface**: Enhanced web-based user interface
- **Real-time Updates**: WebSocket support for live data
- **Mobile App**: React Native mobile application
- **Advanced Analytics**: Machine learning integration for insights

## Conclusion

The Alpha Crucible Quant architecture provides a comprehensive foundation for quantitative investment strategies with modern web-based visualization and interaction. The full-stack design combines powerful quantitative analysis with an intuitive user interface, making it suitable for both research and production use. The modular architecture allows for easy extension and customization while maintaining reliability and performance across all components.
