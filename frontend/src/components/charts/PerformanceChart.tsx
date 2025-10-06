/**
 * Performance Chart Component
 * Displays portfolio performance over time using Recharts
 */

import React, { useState, useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { 
  Box, 
  Typography, 
  useTheme, 
  Switch, 
  FormControlLabel, 
  FormControl, 
  Select, 
  MenuItem, 
  InputLabel,
  CircularProgress,
  Alert
} from '@mui/material';
import { format, parseISO } from 'date-fns';
import { useQuery } from 'react-query';

import { NavData } from '@/types';
import { marketApi } from '@/services/api';

interface PerformanceChartProps {
  data: NavData[];
  height?: number;
  showBenchmark?: boolean;
  showTrendLine?: boolean;
  backtestStartDate?: string;
  backtestEndDate?: string;
}

const PerformanceChart: React.FC<PerformanceChartProps> = ({
  data,
  height = 400,
  showBenchmark = true,
  showTrendLine: initialShowTrendLine = false,
  backtestStartDate,
  backtestEndDate,
}) => {
  const theme = useTheme();
  const [showTrendLine, setShowTrendLine] = useState(initialShowTrendLine);
  const [showMarketOverlay, setShowMarketOverlay] = useState(false);
  const [marketSymbol, setMarketSymbol] = useState('SPY');

  // Helper function to get display name for market symbol
  const getMarketDisplayName = (symbol: string) => {
    return symbol === '^GSPC' ? 'S&P 500' : symbol;
  };

  // Get the starting value for normalization
  const startingValue = data.length > 0 ? data[0].portfolio_nav : 100;

  // Fetch market overlay data
  const {
    data: marketOverlayData,
    isLoading: marketOverlayLoading,
    error: marketOverlayError,
  } = useQuery(
    ['market-overlay', marketSymbol, backtestStartDate, backtestEndDate, startingValue],
    () => marketApi.getNormalizedMarketData(
      marketSymbol,
      backtestStartDate || data[0]?.nav_date || '',
      backtestEndDate || data[data.length - 1]?.nav_date || '',
      startingValue
    ),
    {
      enabled: showMarketOverlay && !!backtestStartDate && !!backtestEndDate,
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
    }
  );

  // Calculate linear regression trend line
  const trendLineData = useMemo(() => {
    if (!showTrendLine || data.length < 2) return [];
    
    const n = data.length;
    const xValues = data.map((_, index) => index);
    const yValues = data.map(item => item.portfolio_nav);
    
    // Calculate means
    const xMean = xValues.reduce((sum, x) => sum + x, 0) / n;
    const yMean = yValues.reduce((sum, y) => sum + y, 0) / n;
    
    // Calculate slope and intercept
    let numerator = 0;
    let denominator = 0;
    
    for (let i = 0; i < n; i++) {
      const xDiff = xValues[i] - xMean;
      const yDiff = yValues[i] - yMean;
      numerator += xDiff * yDiff;
      denominator += xDiff * xDiff;
    }
    
    const slope = denominator === 0 ? 0 : numerator / denominator;
    const intercept = yMean - slope * xMean;
    
    // Generate trend line points
    return data.map((item, index) => ({
      date: item.nav_date,
      trend: slope * index + intercept,
    }));
  }, [data, showTrendLine]);

  // Transform data for chart
  const chartData = useMemo(() => {
    const baseData = data.map((item, index) => ({
      date: item.nav_date,
      portfolio: item.portfolio_nav,
      benchmark: item.benchmark_nav || null,
      pnl: item.pnl || 0,
      trend: showTrendLine && trendLineData.length > 0 ? trendLineData[index]?.trend : null,
    }));

    // Add market overlay data if available
    if (showMarketOverlay && marketOverlayData?.data) {
      const marketDataMap = new Map(
        marketOverlayData.data.map(point => [point.date, point.value])
      );
      
      return baseData.map(item => ({
        ...item,
        marketOverlay: marketDataMap.get(item.date) || null,
      }));
    }

    return baseData;
  }, [data, showTrendLine, trendLineData, showMarketOverlay, marketOverlayData]);

  // Calculate performance metrics
  const firstValue = chartData[0]?.portfolio || 0;
  const lastValue = chartData[chartData.length - 1]?.portfolio || 0;
  const totalReturn = firstValue > 0 ? ((lastValue - firstValue) / firstValue) * 100 : 0;

  const formatXAxisLabel = (tickItem: string) => {
    try {
      return format(parseISO(tickItem), 'MMM dd');
    } catch {
      return tickItem;
    }
  };

  const formatTooltipLabel = (label: string) => {
    try {
      return format(parseISO(label), 'MMM dd, yyyy');
    } catch {
      return label;
    }
  };

  const formatValue = (value: number, name: string) => {
    if (name === 'pnl') {
      return [`$${value.toFixed(2)}`, 'PnL'];
    }
    if (name === 'trend') {
      return [`$${value.toFixed(2)}`, 'Trend Line'];
    }
    if (name === 'marketOverlay') {
      return [`$${value.toFixed(2)}`, `${getMarketDisplayName(marketSymbol)} (overlay)`];
    }
    return [`$${value.toFixed(2)}`, name === 'portfolio' ? 'Portfolio' : 'Benchmark'];
  };

  if (!data || data.length === 0) {
    return (
      <Box
        sx={{
          height,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: 'background.default',
          borderRadius: 1,
          border: '1px dashed',
          borderColor: 'divider',
        }}
      >
        <Typography variant="body2" color="text.secondary">
          No performance data available
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%', height: height || 400 }}>
      {/* Chart Controls */}
      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={showMarketOverlay}
                onChange={(e) => setShowMarketOverlay(e.target.checked)}
                color="info"
              />
            }
            label="Show Market Overlay"
            sx={{ 
              '& .MuiFormControlLabel-label': {
                fontSize: '0.875rem',
                color: theme.palette.text.secondary,
              }
            }}
          />
          {showMarketOverlay && (
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Symbol</InputLabel>
              <Select
                value={marketSymbol}
                onChange={(e) => setMarketSymbol(e.target.value)}
                label="Symbol"
              >
                <MenuItem value="SPY">SPY</MenuItem>
                <MenuItem value="^GSPC">S&P 500</MenuItem>
              </Select>
            </FormControl>
          )}
        </Box>
        
        <FormControlLabel
          control={
            <Switch
              checked={showTrendLine}
              onChange={(e) => setShowTrendLine(e.target.checked)}
              color="warning"
            />
          }
          label="Show Trend Line"
          sx={{ 
            '& .MuiFormControlLabel-label': {
              fontSize: '0.875rem',
              color: theme.palette.text.secondary,
            }
          }}
        />
      </Box>

      {/* Loading and Error States */}
      {showMarketOverlay && marketOverlayLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 50 }}>
          <CircularProgress size={24} />
          <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
            Loading market overlay...
          </Typography>
        </Box>
      ) : null}
      
      {showMarketOverlay && marketOverlayError ? (
        <Alert severity="warning" sx={{ mb: 2 }}>
          Couldn't load market overlay.
        </Alert>
      ) : null}
      
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={chartData}
          margin={{
            top: 20,
            right: 30,
            left: 20,
            bottom: 20,
          }}
        >
          <CartesianGrid 
            strokeDasharray="3 3" 
            stroke={theme.palette.divider}
            opacity={0.3}
          />
          <XAxis
            dataKey="date"
            tickFormatter={formatXAxisLabel}
            stroke={theme.palette.text.secondary}
            fontSize={12}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            tickFormatter={(value) => `$${value.toLocaleString()}`}
            stroke={theme.palette.text.secondary}
            fontSize={12}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip
            labelFormatter={formatTooltipLabel}
            formatter={formatValue}
            contentStyle={{
              backgroundColor: theme.palette.background.paper,
              border: `1px solid ${theme.palette.divider}`,
              borderRadius: 8,
              boxShadow: theme.shadows[4],
            }}
            labelStyle={{
              color: theme.palette.text.primary,
              fontWeight: 600,
            }}
          />
          <Legend />
          
          {/* Reference line at starting value */}
          <ReferenceLine
            y={firstValue}
            stroke={theme.palette.text.secondary}
            strokeDasharray="2 2"
            opacity={0.5}
            label={{ value: "Starting Value", position: "top" }}
          />
          
          {/* Portfolio line */}
          <Line
            type="monotone"
            dataKey="portfolio"
            stroke={theme.palette.primary.main}
            strokeWidth={3}
            dot={false}
            activeDot={{
              r: 6,
              stroke: theme.palette.primary.main,
              strokeWidth: 2,
              fill: theme.palette.background.paper,
            }}
          />
          
          {/* Benchmark line */}
          {showBenchmark && (
            <Line
              type="monotone"
              dataKey="benchmark"
              stroke={theme.palette.secondary.main}
              strokeWidth={2}
              dot={false}
              strokeDasharray="5 5"
              activeDot={{
                r: 4,
                stroke: theme.palette.secondary.main,
                strokeWidth: 2,
                fill: theme.palette.background.paper,
              }}
            />
          )}
          
          {/* Market overlay line */}
          {showMarketOverlay && marketOverlayData && (
            <Line
              type="monotone"
              dataKey="marketOverlay"
              stroke={theme.palette.info.main}
              strokeWidth={2}
              dot={false}
              strokeDasharray="3 3"
              activeDot={{
                r: 4,
                stroke: theme.palette.info.main,
                strokeWidth: 2,
                fill: theme.palette.background.paper,
              }}
            />
          )}
          
          {/* Trend line */}
          {showTrendLine && (
            <Line
              type="monotone"
              dataKey="trend"
              stroke={theme.palette.warning.main}
              strokeWidth={2}
              dot={false}
              strokeDasharray="8 4"
              activeDot={{
                r: 4,
                stroke: theme.palette.warning.main,
                strokeWidth: 2,
                fill: theme.palette.background.paper,
              }}
            />
          )}
        </LineChart>
      </ResponsiveContainer>
      
      {/* Performance summary */}
      <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          Total Return: {totalReturn.toFixed(2)}%
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {data.length} data points
        </Typography>
      </Box>
    </Box>
  );
};

export default PerformanceChart;

