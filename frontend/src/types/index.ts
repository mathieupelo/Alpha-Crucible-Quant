/**
 * TypeScript type definitions for Alpha Crucible Quant Frontend
 */

export interface Backtest {
  id: number;
  run_id: string;
  name?: string;
  start_date: string;
  end_date: string;
  frequency: string;
  universe_id: number;
  universe?: Record<string, any>;
  universe_name?: string;
  benchmark?: string;
  params?: Record<string, any>;
  created_at: string;
}

export interface BacktestListResponse {
  backtests: Backtest[];
  total: number;
  page: number;
  size: number;
}

export interface BacktestMetrics {
  run_id: string;
  total_return: number;
  annualized_return: number;
  volatility: number;
  sharpe_ratio: number;
  max_drawdown: number;
  win_rate: number;
  alpha: number;
  beta: number;
  information_ratio: number;
  tracking_error: number;
  num_rebalances: number;
  avg_turnover: number;
  avg_num_positions: number;
  max_concentration: number;
  execution_time_seconds: number;
}

export interface Portfolio {
  id: number;
  run_id: string;
  universe_id: number;
  universe_name?: string;
  asof_date: string;
  method: string;
  params?: Record<string, any>;
  cash: number;
  total_value?: number;
  notes?: string;
  created_at: string;
  position_count?: number;
}

export interface Position {
  id: number;
  portfolio_id: number;
  ticker: string;
  weight: number;
  price_used: number;
  company_uid?: string;
  company_name?: string;
  main_ticker?: string;
  created_at: string;
}

export interface PortfolioDetails extends Portfolio {
  positions: Position[];
}

export interface Signal {
  id: number;
  asof_date: string;
  ticker: string;
  signal_name: string;
  value: number;
  metadata?: Record<string, any>;
  company_uid?: string;
  company_name?: string;
  main_ticker?: string;
  created_at: string;
}

export interface Score {
  id: number;
  asof_date: string;
  ticker: string;
  score: number;
  method: string;
  params?: Record<string, any>;
  company_uid?: string;
  company_name?: string;
  main_ticker?: string;
  created_at: string;
}

export interface NavData {
  id: number;
  run_id: string;
  nav_date: string;
  portfolio_nav: number;
  benchmark_nav?: number;
  pnl?: number;
}

export interface NavListResponse {
  nav_data: NavData[];
  total: number;
  run_id: string;
  start_date: string;
  end_date: string;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

export interface ChartDataPoint {
  date: string;
  value: number;
  benchmark?: number;
}

export interface SignalWeights {
  RSI: number;
  SMA: number;
  MACD: number;
}

export interface Theme {
  mode: 'light' | 'dark';
  primary: string;
  secondary: string;
  success: string;
  error: string;
  warning: string;
  background: string;
  surface: string;
  text: string;
}

export interface FilterOptions {
  startDate?: string;
  endDate?: string;
  tickers?: string[];
  signalNames?: string[];
  methods?: string[];
}

export interface Universe {
  id: number;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
  ticker_count: number;
}

export interface UniverseTicker {
  id: number;
  universe_id: number;
  ticker: string;
  added_at: string;
}

export interface TickerValidation {
  ticker: string;
  is_valid: boolean;
  company_name?: string;
  error_message?: string;
}

export interface UniverseCreateRequest {
  name: string;
  description?: string;
}

export interface UniverseUpdateRequest {
  name?: string;
  description?: string;
}

export interface UniverseTickerUpdateRequest {
  tickers: string[];
}

export interface UniverseCompany {
  id: number;
  universe_id: number;
  company_uid: string;
  company_name: string;
  main_ticker: string;
  all_tickers: string[];
  added_at: string;
}

export interface UniverseCompanyListResponse {
  companies: UniverseCompany[];
  total: number;
  universe_id: number;
}

export interface UniverseCompanyUpdateRequest {
  tickers: string[];
}

export interface BacktestCreateRequest {
  start_date: string;
  end_date: string;
  universe_id: number;
  signals: string[];
  name?: string;
  initial_capital?: number;
  rebalancing_frequency?: string;
  evaluation_period?: string;
  transaction_costs?: number;
  max_weight?: number;
  min_weight?: number;
  risk_aversion?: number;
  benchmark_ticker?: string;
  use_equal_weight_benchmark?: boolean;
  min_lookback_days?: number;
  max_lookback_days?: number;
  signal_weights?: Record<string, number>;
  signal_combination_method?: string;
  forward_fill_signals?: boolean;
}

