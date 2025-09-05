# Alpha Crucible Quant Dashboard

A professional, polished React + FastAPI web application for visualizing and analyzing quantitative trading strategies and backtest results.

## 🚀 Features

### **Dashboard Overview**
- **Backtest Selector**: Choose from all available backtests
- **Performance Metrics**: Key metrics cards (Total Return, Sharpe Ratio, Max Drawdown, Volatility)
- **Performance Charts**: Interactive line charts showing portfolio vs benchmark performance
- **Backtest List**: Grid view of all backtests with metadata

### **Backtest Detail Page**
- **Performance Overview**: Large performance chart with key metrics
- **Portfolio History**: Collapsible list of all portfolio rebalances
- **Portfolio Details**: Click to view detailed portfolio information
- **Signal Analysis**: View raw signals and combined scores

### **Portfolio Analysis**
- **Position Details**: Stock weights, prices, and allocations
- **Signal Scores**: RSI, SMA, MACD values for each stock
- **Combined Scores**: Equal-weight combined signal scores
- **Interactive Tables**: Sortable, filterable data tables

### **Professional UI/UX**
- **Dark Theme**: Modern, professional dark theme
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Smooth Animations**: Framer Motion animations and transitions
- **Real-time Updates**: Auto-refresh data every 30 seconds
- **Export Features**: Download charts and data as CSV/PNG

## 🏗️ Architecture

### **Backend (FastAPI)**
```
backend/
├── main.py                 # FastAPI application entry point
├── api/                    # API route modules
│   ├── backtests.py       # Backtest endpoints
│   ├── portfolios.py      # Portfolio endpoints
│   ├── signals.py         # Signal endpoints
│   └── nav.py             # NAV data endpoints
├── models/                 # Pydantic response models
│   └── responses.py       # API response schemas
├── services/               # Business logic layer
│   └── database_service.py # Database operations
└── requirements.txt        # Python dependencies
```

### **Frontend (React + TypeScript)**
```
frontend/
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── charts/        # Chart components
│   │   ├── tables/        # Table components
│   │   ├── cards/         # Card components
│   │   └── common/        # Common components
│   ├── pages/             # Main application pages
│   │   ├── Dashboard.tsx  # Main dashboard
│   │   └── BacktestDetail.tsx # Backtest detail page
│   ├── services/          # API service layer
│   │   └── api.ts         # API client
│   ├── types/             # TypeScript type definitions
│   │   └── index.ts       # All type definitions
│   ├── App.tsx            # Main app component
│   └── main.tsx           # Application entry point
├── package.json           # Node.js dependencies
└── vite.config.ts         # Vite configuration
```

## 🛠️ Technology Stack

### **Backend**
- **FastAPI**: High-performance Python web framework
- **Pydantic**: Data validation and serialization
- **MySQL**: Database with existing schema
- **Uvicorn**: ASGI server

### **Frontend**
- **React 18**: Modern React with hooks
- **TypeScript**: Type-safe JavaScript
- **Material-UI**: Professional component library
- **Recharts**: Beautiful, responsive charts
- **React Query**: Data fetching and caching
- **React Router**: Client-side routing
- **Vite**: Fast build tool and dev server

### **Deployment**
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Nginx**: Reverse proxy and static file serving

## 🚀 Quick Start

### **Prerequisites**
- Docker and Docker Compose
- Node.js 18+ (for development)
- Python 3.11+ (for development)

### **Development Setup**

1. **Clone and navigate to the project:**
   ```bash
   cd Alpha-Crucible-Quant
   ```

2. **Start the database:**
   ```bash
   docker-compose up mysql -d
   ```

3. **Set up the database schema:**
   ```bash
   python scripts/setup_database.py
   ```

4. **Install backend dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

5. **Start the backend:**
   ```bash
   python main.py
   ```

6. **Install frontend dependencies:**
   ```bash
   cd ../frontend
   npm install
   ```

7. **Start the frontend:**
   ```bash
   npm run dev
   ```

8. **Open the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/api/docs

### **Production Deployment**

1. **Set environment variables:**
   ```bash
   export DB_PASSWORD=your_secure_password
   export DB_USER=your_db_user
   ```

2. **Deploy with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

3. **Access the application:**
   - Application: http://localhost
   - API: http://localhost/api

## 📊 Data Flow

### **1. Signal Calculation**
- Raw signals (RSI, SMA, MACD) → `signals_raw` table
- Combined scores → `scores_combined` table

### **2. Portfolio Optimization**
- Signal scores → Portfolio optimization → `portfolios` table
- Individual positions → `portfolio_positions` table

### **3. Backtest Execution**
- Portfolio rebalancing → NAV tracking → `backtest_nav` table
- Backtest metadata → `backtests` table

### **4. Visualization**
- Database → FastAPI → React → Interactive Charts

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

## 🎨 UI Components

### **Charts**
- **PerformanceChart**: Portfolio vs benchmark performance
- **MetricCard**: Key performance indicators
- **Interactive Tables**: Sortable, filterable data

### **Navigation**
- **Layout**: Main application layout with header/footer
- **Dashboard**: Overview of all backtests
- **BacktestDetail**: Detailed backtest analysis
- **PortfolioDetail**: Portfolio composition analysis

## 🔒 Security Features

- **CORS Configuration**: Secure cross-origin requests
- **Input Validation**: Pydantic model validation
- **SQL Injection Protection**: Parameterized queries
- **Rate Limiting**: API rate limiting with Nginx
- **Security Headers**: XSS, CSRF protection

## 📱 Responsive Design

- **Mobile-First**: Optimized for mobile devices
- **Breakpoints**: xs, sm, md, lg, xl responsive breakpoints
- **Touch-Friendly**: Large touch targets and gestures
- **Progressive Enhancement**: Works without JavaScript

## 🚀 Performance Optimizations

- **React Query**: Intelligent data caching
- **Code Splitting**: Lazy loading of components
- **Image Optimization**: Optimized static assets
- **Gzip Compression**: Compressed responses
- **CDN Ready**: Static asset optimization

## 🧪 Testing

### **Backend Testing**
```bash
cd backend
python -m pytest tests/
```

### **Frontend Testing**
```bash
cd frontend
npm test
```

## 📈 Monitoring

- **Health Checks**: Built-in health check endpoints
- **Error Logging**: Comprehensive error logging
- **Performance Metrics**: Response time monitoring
- **Database Monitoring**: Query performance tracking

## 🔧 Configuration

### **Environment Variables**
```bash
# Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=password
DB_NAME=signal_forge

# API
API_HOST=0.0.0.0
API_PORT=8000

# Frontend
VITE_API_URL=http://localhost:8000
```

## 📚 Documentation

- **API Documentation**: Available at `/api/docs`
- **Type Definitions**: Comprehensive TypeScript types
- **Component Documentation**: JSDoc comments
- **Database Schema**: Well-documented database models

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
- Review the component documentation

---

**Alpha Crucible Quant Dashboard** - Professional quantitative trading analysis made simple! 🚀

