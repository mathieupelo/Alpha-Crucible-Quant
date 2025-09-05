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
  FilterOptions
} from '@/types';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
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

  // Get scores for a backtest
  getBacktestScores: async (runId: string, filters?: FilterOptions): Promise<{ scores: Score[]; total: number; run_id: string }> => {
    const response = await api.get(`/backtests/${runId}/scores`, {
      params: {
        start_date: filters?.startDate,
        end_date: filters?.endDate
      }
    });
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

// Health check
export const healthApi = {
  check: async (): Promise<{ status: string; service: string }> => {
    const response = await api.get('/health');
    return response.data;
  }
};

export default api;

