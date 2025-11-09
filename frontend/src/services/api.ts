/**
 * API Service for Alpha Crucible Quant Frontend
 * Handles all API calls to the FastAPI backend
 */

import axios, { AxiosResponse } from 'axios';
import {
  Backtest,
  BacktestListResponse,
  BacktestMetrics,
  Portfolio,
  PortfolioDetails,
  NavListResponse,
  Signal,
  Score,
  FilterOptions,
  Universe,
  UniverseCompany,
  UniverseCompanyListResponse,
  UniverseCompanyUpdateRequest,
  TickerValidation,
  UniverseCreateRequest,
  UniverseUpdateRequest,
  BacktestCreateRequest,
  TickerInfo,
  CompanyInfo,
  TickerListResponse,
  CompanySearchResponse
} from '@/types';

// Create axios instance with base configuration
// Use ngrok URL if we're running on ngrok domain, otherwise use localhost
const getBaseURL = () => {
  if (window.location.hostname.includes('ngrok-free.dev')) {
    return `${window.location.protocol}//${window.location.hostname}/api`;
  }
  
  // If VITE_API_URL is explicitly set, use it
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // For development (Vite dev server on any port), use relative URL
  // This allows Vite's proxy (configured in vite.config.ts) to forward /api requests to backend
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return '/api';
  }
  
  // Fallback: use relative URL
  return '/api';
};

const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 600000, // Increased to 5 minutes for backtest execution
  headers: {
    'Content-Type': 'application/json',
    'ngrok-skip-browser-warning': 'true', // Bypass ngrok browser warning
    'Authorization': `Bearer ${import.meta.env.VITE_API_KEY || 'my-awesome-key-123'}`,
  },
});

// Request interceptor for logging (avoid TS errors in production builds)
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    // Note: Do not assume header is a string in production builds
    try {
      const auth = (config.headers as any)?.['Authorization'];
      const preview = typeof auth === 'string' ? `${auth.slice(0, 20)}...` : '[hidden]';
      console.log(`API Key being sent: ${preview}`);
    } catch { /* noop */ }
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Backtest API calls
export const backtestApi = {
  // Get all backtests with pagination
  getBacktests: async (page: number = 1, size: number = 50): Promise<BacktestListResponse> => {
    const response: AxiosResponse<BacktestListResponse> = await api.get('/backtests', {
      params: { page, size }
    });
    return response.data;
  },

  // Get specific backtest by run ID
  getBacktest: async (runId: string): Promise<Backtest> => {
    const response: AxiosResponse<Backtest> = await api.get(`/backtests/${runId}`);
    return response.data;
  },

  // Get backtest performance metrics
  getBacktestMetrics: async (runId: string): Promise<BacktestMetrics> => {
    const response: AxiosResponse<BacktestMetrics> = await api.get(`/backtests/${runId}/metrics`);
    return response.data;
  },

  // Get portfolios for a backtest
  getBacktestPortfolios: async (runId: string): Promise<{ portfolios: Portfolio[]; total: number; run_id: string }> => {
    const response = await api.get(`/backtests/${runId}/portfolios`);
    return response.data;
  },

  // Get signals for a backtest
  getBacktestSignals: async (runId: string, filters?: FilterOptions): Promise<{ signals: Signal[]; total: number; run_id: string }> => {
    const response = await api.get(`/backtests/${runId}/signals`, {
      params: {
        start_date: filters?.startDate,
        end_date: filters?.endDate
      }
    });
    return response.data;
  },

  // Get only used signals (definitions) for a backtest
  getBacktestUsedSignals: async (runId: string): Promise<{ signals: Array<{ signal_id: number; name: string; description?: string }>; total: number; run_id: string }> => {
    const response = await api.get(`/backtests/${runId}/used-signals`);
    return response.data;
  },

  // Get scores for a backtest
  getBacktestScores: async (runId: string, filters?: FilterOptions): Promise<{ scores: Score[]; total: number; run_id: string }> => {
    const response = await api.get(`/backtests/${runId}/scores`, {
      params: {
        start_date: filters?.startDate,
        end_date: filters?.endDate
      }
    });
    return response.data;
  },

  // Create new backtest
  createBacktest: async (request: BacktestCreateRequest): Promise<Backtest> => {
    const response: AxiosResponse<Backtest> = await api.post('/backtests', request);
    return response.data;
  },

  // Check if backtest name exists
  checkBacktestName: async (name: string): Promise<{ name: string; exists: boolean; available: boolean }> => {
    const response = await api.get(`/backtests/check-name?name=${encodeURIComponent(name)}`);
    return response.data;
  },

  // Delete backtest
  deleteBacktest: async (runId: string): Promise<{ message: string; run_id: string }> => {
    const response = await api.delete(`/backtests/${runId}`);
    return response.data;
  }
};

// Portfolio API calls
export const portfolioApi = {
  // Get portfolio details by ID
  getPortfolio: async (portfolioId: number): Promise<PortfolioDetails> => {
    const response: AxiosResponse<PortfolioDetails> = await api.get(`/portfolios/${portfolioId}`);
    return response.data;
  },

  // Get portfolio positions
  getPortfolioPositions: async (portfolioId: number): Promise<{ positions: any[]; total: number; portfolio_id: number }> => {
    const response = await api.get(`/portfolios/${portfolioId}/positions`);
    return response.data;
  },

  // Get portfolio signal scores
  getPortfolioSignals: async (portfolioId: number): Promise<{ signals: any[]; total: number; portfolio_id: number }> => {
    const response = await api.get(`/portfolios/${portfolioId}/signals`);
    return response.data;
  },

  // Get portfolio combined scores
  getPortfolioScores: async (portfolioId: number): Promise<{ scores: any[]; total: number; portfolio_id: number }> => {
    const response = await api.get(`/portfolios/${portfolioId}/scores`);
    return response.data;
  },

  // Get portfolio universe tickers
  getPortfolioUniverseTickers: async (portfolioId: number): Promise<{ tickers: string[]; total: number; portfolio_id: number; universe_id: number }> => {
    const response = await api.get(`/portfolios/${portfolioId}/universe-tickers`);
    return response.data;
  }
};

// NAV API calls
export const navApi = {
  // Get NAV data for a backtest
  getBacktestNav: async (runId: string, startDate?: string, endDate?: string): Promise<NavListResponse> => {
    const response: AxiosResponse<NavListResponse> = await api.get(`/backtests/${runId}/nav`, {
      params: {
        start_date: startDate,
        end_date: endDate
      }
    });
    return response.data;
  }
};

// Signal API calls
export const signalApi = {
  // Get all signals with filtering
  getSignals: async (filters?: FilterOptions): Promise<{ signals: Signal[]; total: number }> => {
    const response = await api.get('/signals', {
      params: {
        tickers: filters?.tickers?.join(','),
        signal_names: filters?.signalNames?.join(','),
        start_date: filters?.startDate,
        end_date: filters?.endDate
      }
    });
    return response.data;
  },

  // Get available signal types
  getSignalTypes: async (): Promise<{ signal_types: Array<{signal_id: string; name: string; parameters: any; min_lookback: number; max_lookback: number}>; total: number }> => {
    const response = await api.get('/signal-types');
    return response.data;
  },

  // Get all scores with filtering
  getScores: async (filters?: FilterOptions): Promise<{ scores: Score[]; total: number }> => {
    const response = await api.get('/scores', {
      params: {
        tickers: filters?.tickers?.join(','),
        methods: filters?.methods?.join(','),
        start_date: filters?.startDate,
        end_date: filters?.endDate
      }
    });
    return response.data;
  }
};

// Universe API calls
export const universeApi = {
  // Get all universes
  getUniverses: async (): Promise<{ universes: Universe[]; total: number }> => {
    const response = await api.get('/universes');
    return response.data;
  },

  // Get specific universe by ID
  getUniverse: async (universeId: number): Promise<Universe> => {
    const response = await api.get(`/universes/${universeId}`);
    return response.data;
  },

  // Create new universe
  createUniverse: async (request: UniverseCreateRequest): Promise<Universe> => {
    const response = await api.post('/universes', request);
    return response.data;
  },

  // Update universe
  updateUniverse: async (universeId: number, request: UniverseUpdateRequest): Promise<Universe> => {
    const response = await api.put(`/universes/${universeId}`, request);
    return response.data;
  },

  // Delete universe
  deleteUniverse: async (universeId: number): Promise<{ success: boolean; message: string }> => {
    const response = await api.delete(`/universes/${universeId}`);
    return response.data;
  },

  // Get universe companies (Varrock schema)
  getUniverseCompanies: async (universeId: number): Promise<UniverseCompanyListResponse> => {
    const response = await api.get(`/universes/${universeId}/companies`);
    return response.data;
  },

  // Update universe companies (accepts tickers, auto-resolves to companies)
  updateUniverseCompanies: async (universeId: number, request: UniverseCompanyUpdateRequest): Promise<UniverseCompanyListResponse> => {
    const response = await api.put(`/universes/${universeId}/companies`, request);
    return response.data;
  },

  // Add single company to universe (accepts ticker, auto-resolves to company)
  addUniverseCompany: async (universeId: number, ticker: string): Promise<UniverseCompany> => {
    const response = await api.post(`/universes/${universeId}/companies`, null, {
      params: { ticker }
    });
    return response.data;
  },

  // Remove company from universe
  removeUniverseCompany: async (universeId: number, companyUid: string): Promise<{ success: boolean; message: string }> => {
    const response = await api.delete(`/universes/${universeId}/companies/${companyUid}`);
    return response.data;
  },

  // Validate tickers
  validateTickers: async (tickers: string[]): Promise<TickerValidation[]> => {
    const response = await api.post('/tickers/validate', tickers);
    return response.data;
  }
};

// Market Data API calls
export const marketApi = {
  // Get market data for a symbol
  getMarketData: async (symbol: string, startDate: string, endDate: string): Promise<{
    symbol: string;
    start_date: string;
    end_date: string;
    data: Array<{
      date: string;
      close: number;
      open: number;
      high: number;
      low: number;
      volume: number;
    }>;
    total_points: number;
  }> => {
    const response = await api.get(`/market-data/${symbol}`, {
      params: {
        start_date: startDate,
        end_date: endDate
      }
    });
    return response.data;
  },

  // Get normalized market data for a symbol
  getNormalizedMarketData: async (
    symbol: string, 
    startDate: string, 
    endDate: string, 
    startValue: number = 100
  ): Promise<{
    symbol: string;
    start_date: string;
    end_date: string;
    start_value: number;
    data: Array<{
      date: string;
      value: number;
      return_since_start: number;
    }>;
    total_points: number;
  }> => {
    const response = await api.get(`/market-data/${symbol}/normalized`, {
      params: {
        start_date: startDate,
        end_date: endDate,
        start_value: startValue
      }
    });
    return response.data;
  },

  // Get live price for a symbol
  getLivePrice: async (symbol: string): Promise<{
    symbol: string;
    price: number;
    previous_close: number;
    daily_change: number;
    daily_change_percent: number;
    timestamp: string;
  }> => {
    const response = await api.get(`/market-data/live/${symbol}`);
    return response.data;
  },

  // Get live prices for multiple tickers
  getLivePricesBatch: async (tickers: string[]): Promise<{
    results: Array<{
      symbol: string;
      price: number | null;
      previous_close: number | null;
      daily_change: number | null;
      daily_change_percent: number | null;
      timestamp?: string;
      error?: string;
    }>;
    timestamp: string;
  }> => {
    const response = await api.post('/market-data/live/batch', tickers);
    return response.data;
  },

  // Get intraday price data (5-minute intervals)
  getIntradayPriceData: async (symbol: string): Promise<{
    symbol: string;
    date: string;
    data: Array<{
      timestamp: string;
      datetime: string;
      open: number | null;
      high: number | null;
      low: number | null;
      close: number | null;
      volume: number;
    }>;
    total_points: number;
    interval: string;
  }> => {
    const response = await api.get(`/market-data/${symbol}/intraday`);
    return response.data;
  }
};

// News API calls
export const newsApi = {
  // Get news for a universe
  getUniverseNews: async (universeName: string, maxItems: number = 10): Promise<{
    universe_name: string;
    tickers: string[];
    news: Array<{
      ticker: string;
      title: string;
      summary: string;
      publisher: string;
      link: string;
      pub_date: string;
      image_url?: string;
      sentiment: {
        label: string;
        score: number;
        label_display: string;
        scores?: {
          positive: number;
          negative: number;
          neutral: number;
        };
      };
    }>;
    total: number;
  }> => {
    const response = await api.get(`/news/universe/${encodeURIComponent(universeName)}`, {
      params: { max_items: maxItems }
    });
    return response.data;
  },

  // Get news for a specific ticker
  getTickerNews: async (ticker: string, maxItems: number = 10): Promise<{
    ticker: string;
    news: Array<{
      ticker: string;
      title: string;
      summary: string;
      publisher: string;
      link: string;
      pub_date: string;
      image_url?: string;
      sentiment: {
        label: string;
        score: number;
        label_display: string;
        scores?: {
          positive: number;
          negative: number;
          neutral: number;
        };
      };
    }>;
    total: number;
  }> => {
    const response = await api.get(`/news/ticker/${ticker}`, {
      params: { max_items: maxItems }
    });
    return response.data;
  },

  // Get news for multiple tickers
  getMultipleTickersNews: async (tickers: string[], maxItems: number = 10): Promise<{
    tickers: string[];
    news: Array<{
      ticker: string;
      title: string;
      summary: string;
      publisher: string;
      link: string;
      pub_date: string;
      image_url?: string;
      sentiment: {
        label: string;
        score: number;
        label_display: string;
        scores?: {
          positive: number;
          negative: number;
          neutral: number;
        };
      };
    }>;
    total: number;
  }> => {
    const response = await api.get('/news/tickers', {
      params: { 
        tickers: tickers.join(','),
        max_items: maxItems 
      }
    });
    return response.data;
  },

  // Get today's news aggregated by ticker
  getTodayNewsAggregated: async (universeName: string): Promise<{
    universe_name: string;
    date: string;
    tickers: {
      [ticker: string]: Array<{
        ticker: string;
        title: string;
        summary: string;
        publisher: string;
        link: string;
        pub_date: string;
        image_url?: string;
        sentiment: {
          label: string;
          score: number;
          label_display: string;
        };
      }>;
    };
  }> => {
    const response = await api.get(`/news/universe/${encodeURIComponent(universeName)}/today-aggregated`);
    return response.data;
  },

  // Analyze news with GPT-4o-mini
  analyzeNews: async (request: {
    ticker: string;
    title: string;
    summary: string;
    sentiment: {
      label: string;
      score: number;
      label_display: string;
    };
    price_data: {
      price: number;
      previous_close: number;
      daily_change: number;
      daily_change_percent: number;
    };
    pub_date: string;
  }): Promise<{
    ticker: string;
    analysis: string;
    model: string;
    timestamp: string;
  }> => {
    const response = await api.post('/news/analyze', request);
    return response.data;
  },

  // Get news statistics
  getNewsStatistics: async (universeName: string): Promise<{
    universe_name: string;
    date: string;
    top_tickers: Array<{
      ticker: string;
      avg_sentiment_score: number;
      positive_count: number;
      negative_count: number;
      neutral_count: number;
      total_news: number;
    }>;
    bottom_tickers: Array<{
      ticker: string;
      avg_sentiment_score: number;
      positive_count: number;
      negative_count: number;
      neutral_count: number;
      total_news: number;
    }>;
    sector_trends_today: {
      positive_percent: number;
      negative_percent: number;
      neutral_percent: number;
      total_news: number;
    };
    sector_trends_week: {
      positive_percent: number;
      negative_percent: number;
      neutral_percent: number;
      total_news: number;
    };
    time_based_changes: Array<{
      hour: number;
      positive: number;
      negative: number;
      neutral: number;
      total: number;
    }>;
  }> => {
    const response = await api.get(`/news/universe/${encodeURIComponent(universeName)}/statistics`);
    return response.data;
  }
};

// Health check
export const healthApi = {
  check: async (): Promise<{ status: string; service: string }> => {
    const response = await api.get('/health');
    return response.data;
  }
};

// Ticker Management API calls
export const tickerApi = {
  // Fetch ticker info from yfinance (without saving)
  fetchTickerInfo: async (ticker: string): Promise<TickerInfo> => {
    const response = await api.get('/tickers/fetch-info', {
      params: { ticker }
    });
    return response.data;
  },

  // Create a new ticker in the database
  createTicker: async (ticker: string, yfinanceInfo?: TickerInfo): Promise<{ message: string }> => {
    const response = await api.post('/tickers/create', {
      ticker,
      yfinance_info: yfinanceInfo
    });
    return response.data;
  },

  // Add alternative ticker to existing company
  addAlternativeTicker: async (companyUid: string, ticker: string, market: string): Promise<{
    message: string;
    company_uid: string;
    company_name?: string;
    main_ticker?: string;
    new_ticker: string;
    market: string;
  }> => {
    const response = await api.post('/tickers/add-alternative', {
      company_uid: companyUid,
      ticker,
      market
    });
    return response.data;
  },

  // Get company info for validation
  getCompanyInfo: async (companyUid: string): Promise<CompanyInfo> => {
    const response = await api.get(`/tickers/company/${companyUid}`);
    return response.data;
  },

  // Get all tickers with pagination
  getAllTickers: async (page: number = 1, size: number = 50): Promise<TickerListResponse> => {
    const response = await api.get('/tickers/all', {
      params: { page, size }
    });
    return response.data;
  },

  // Search companies
  searchCompanies: async (query: string, limit: number = 10): Promise<CompanySearchResponse> => {
    const response = await api.get('/tickers/search', {
      params: { query, limit }
    });
    return response.data;
  }
};

export default api;

