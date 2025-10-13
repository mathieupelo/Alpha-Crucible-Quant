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
  AreaChart,
  Area,
} from 'recharts';
import { 
  Box, 
  Typography, 
  Chip,
  FormControl,
  FormControlLabel,
  Switch, 
  Select, 
  MenuItem, 
  InputLabel,
  Button,
  ButtonGroup,
  Stack,
} from '@mui/material';
import { format, parseISO } from 'date-fns';
import { useQuery } from 'react-query';
import { motion } from 'framer-motion';

import { NavData } from '@/types';
import { marketApi } from '@/services/api';
import { useTheme as useCustomTheme } from '@/contexts/ThemeContext';

interface PerformanceChartProps {
  data: NavData[];
  height?: number;
  showBenchmark?: boolean;
  backtestStartDate?: string;
  backtestEndDate?: string;
}

const PerformanceChart: React.FC<PerformanceChartProps> = ({
  data,
  height = 400,
  showBenchmark = true,
  backtestStartDate,
  backtestEndDate,
}) => {
  const { isDarkMode } = useCustomTheme();
  const [showTrendLine, setShowTrendLine] = useState(true); // Enable by default
  const [showMarketOverlay, setShowMarketOverlay] = useState(true); // Enable by default
  const [marketSymbol, setMarketSymbol] = useState('SPY');
  const [showAreaFill, setShowAreaFill] = useState(true); // Enable area chart by default


  // Get the starting value for normalization
  const startingValue = data.length > 0 ? data[0].portfolio_nav : 100;

  // Fetch market overlay data
  const {
    data: marketOverlayData,
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


  // Debug logging
  console.log('PerformanceChart - Data received:', data);
  console.log('PerformanceChart - Data length:', data?.length);
  console.log('PerformanceChart - Chart data:', chartData);

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
          No performance data available (Data length: {data?.length || 0})
        </Typography>
      </Box>
    );
  }

  // Simple test chart first

  return (
    <Box sx={{ width: '100%', height: height || 400 }}>
      {/* Interactive Controls */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <Box sx={{ 
          mb: 3, 
          p: 2,
          background: isDarkMode
            ? 'linear-gradient(145deg, #1e293b 0%, #334155 100%)'
            : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
          backdropFilter: 'none',
          borderRadius: 2,
          border: '1px solid',
          borderColor: isDarkMode
            ? 'rgba(148, 163, 184, 0.1)'
            : 'rgba(148, 163, 184, 0.2)',
        }}>
          <Stack direction="row" spacing={3} alignItems="center" flexWrap="wrap" useFlexGap>
            {/* Chart Type Toggle */}
            <ButtonGroup size="small" variant="outlined">
              <Button 
                variant={!showAreaFill ? "contained" : "outlined"}
                onClick={() => setShowAreaFill(false)}
                sx={{ 
                  background: !showAreaFill ? (isDarkMode ? '#2563eb' : '#1d4ed8') : 'transparent',
                  color: !showAreaFill ? 'white' : (isDarkMode ? '#94a3b8' : '#64748b'),
                  '&:hover': {
                    background: !showAreaFill ? (isDarkMode ? '#1d4ed8' : '#1e40af') : (isDarkMode ? 'rgba(37, 99, 235, 0.1)' : 'rgba(29, 78, 216, 0.1)'),
                  }
                }}
              >
                Line Chart
              </Button>
              <Button 
                variant={showAreaFill ? "contained" : "outlined"}
                onClick={() => setShowAreaFill(true)}
                sx={{ 
                  background: showAreaFill ? (isDarkMode ? '#2563eb' : '#1d4ed8') : 'transparent',
                  color: showAreaFill ? 'white' : (isDarkMode ? '#94a3b8' : '#64748b'),
                  '&:hover': {
                    background: showAreaFill ? (isDarkMode ? '#1d4ed8' : '#1e40af') : (isDarkMode ? 'rgba(37, 99, 235, 0.1)' : 'rgba(29, 78, 216, 0.1)'),
                  }
                }}
              >
                Area Chart
              </Button>
            </ButtonGroup>

            {/* Trend Line Toggle */}
            <FormControlLabel
              control={
                <Switch
                  checked={showTrendLine}
                  onChange={(e) => setShowTrendLine(e.target.checked)}
                  sx={{
                    '& .MuiSwitch-switchBase.Mui-checked': {
                      color: isDarkMode ? '#2563eb' : '#1d4ed8',
                    },
                    '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                      backgroundColor: isDarkMode ? '#2563eb' : '#1d4ed8',
                    },
                  }}
                />
              }
              label="Trend Line"
              sx={{ 
                color: isDarkMode ? '#e2e8f0' : '#334155',
                '& .MuiFormControlLabel-label': {
                  fontSize: '0.875rem',
                  fontWeight: 500,
                }
              }}
            />

            {/* Market Overlay Toggle */}
          <FormControlLabel
            control={
              <Switch
                checked={showMarketOverlay}
                onChange={(e) => setShowMarketOverlay(e.target.checked)}
                  sx={{
                    '& .MuiSwitch-switchBase.Mui-checked': {
                      color: isDarkMode ? '#2563eb' : '#1d4ed8',
                    },
                    '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                      backgroundColor: isDarkMode ? '#2563eb' : '#1d4ed8',
                    },
                  }}
                />
              }
              label="Market Overlay"
            sx={{ 
                color: isDarkMode ? '#e2e8f0' : '#334155',
              '& .MuiFormControlLabel-label': {
                fontSize: '0.875rem',
                  fontWeight: 500,
              }
            }}
          />

            {/* Market Symbol Selector */}
          {showMarketOverlay && (
            <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel sx={{ 
                  color: isDarkMode ? '#94a3b8' : '#64748b',
                  '&.Mui-focused': {
                    color: isDarkMode ? '#2563eb' : '#1d4ed8',
                  }
                }}>
                  Market
                </InputLabel>
              <Select
                value={marketSymbol}
                onChange={(e) => setMarketSymbol(e.target.value)}
                  label="Market"
                  sx={{
                    color: isDarkMode ? '#e2e8f0' : '#334155',
                    background: isDarkMode
                      ? 'linear-gradient(145deg, #1e293b 0%, #334155 100%)'
                      : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
                    '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: isDarkMode ? 'rgba(148, 163, 184, 0.3)' : 'rgba(100, 116, 139, 0.3)',
                    },
                    '&:hover .MuiOutlinedInput-notchedOutline': {
                      borderColor: isDarkMode ? '#2563eb' : '#1d4ed8',
                    },
                    '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                      borderColor: isDarkMode ? '#2563eb' : '#1d4ed8',
                    },
                  }}
                  MenuProps={{
                    PaperProps: {
                      sx: {
                        background: isDarkMode
                          ? 'linear-gradient(145deg, #1e293b 0%, #334155 100%)'
                          : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
                        border: isDarkMode
                          ? '1px solid rgba(148, 163, 184, 0.3)'
                          : '1px solid rgba(148, 163, 184, 0.4)',
                        boxShadow: isDarkMode
                          ? '0 8px 32px 0 rgba(0, 0, 0, 0.5), 0 4px 16px 0 rgba(0, 0, 0, 0.4)'
                          : '0 8px 32px 0 rgba(0, 0, 0, 0.2), 0 4px 16px 0 rgba(0, 0, 0, 0.15)',
                        '& .MuiMenuItem-root': {
                          color: isDarkMode ? '#e2e8f0' : '#1e293b',
                          '&:hover': {
                            backgroundColor: isDarkMode ? 'rgba(37, 99, 235, 0.1)' : 'rgba(37, 99, 235, 0.05)',
                          },
                          '&.Mui-selected': {
                            backgroundColor: isDarkMode ? 'rgba(37, 99, 235, 0.2)' : 'rgba(37, 99, 235, 0.1)',
                            '&:hover': {
                              backgroundColor: isDarkMode ? 'rgba(37, 99, 235, 0.3)' : 'rgba(37, 99, 235, 0.15)',
                            },
                          },
                        },
                      },
                    },
                  }}
                >
                  <MenuItem value="SPY">SPY (S&P 500)</MenuItem>
                  <MenuItem value="QQQ">QQQ (NASDAQ)</MenuItem>
                  <MenuItem value="IWM">IWM (Russell 2000)</MenuItem>
                  <MenuItem value="DIA">DIA (Dow Jones)</MenuItem>
              </Select>
            </FormControl>
          )}
          </Stack>
        </Box>
      </motion.div>

      {/* Performance Chart */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
      >
        <Box sx={{ 
          width: '100%', 
          height: height || 400,
          p: 2,
          background: isDarkMode
            ? 'linear-gradient(145deg, #1e293b 0%, #334155 100%)'
            : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
          backdropFilter: 'none',
          borderRadius: 3,
          border: '1px solid',
          borderColor: isDarkMode
            ? 'rgba(148, 163, 184, 0.1)'
            : 'rgba(148, 163, 184, 0.2)',
          boxShadow: isDarkMode
            ? '0 8px 32px rgba(0, 0, 0, 0.3)'
            : '0 8px 32px rgba(0, 0, 0, 0.1)',
        }}>
          <ResponsiveContainer width="100%" height={height ? height - 40 : 360}>
            {showAreaFill ? (
              <AreaChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                <defs>
                  <linearGradient id="portfolioGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2563eb" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#2563eb" stopOpacity={0.05}/>
                  </linearGradient>
                  <linearGradient id="benchmarkGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0.05}/>
                  </linearGradient>
                </defs>
                <CartesianGrid 
                  strokeDasharray="3 3" 
                  stroke={isDarkMode ? 'rgba(148, 163, 184, 0.1)' : 'rgba(148, 163, 184, 0.2)'}
                />
                <XAxis 
                  dataKey="date" 
                  tickFormatter={(value) => {
                    try {
                      return format(parseISO(value), 'MMM dd');
                    } catch {
                      return value;
                    }
                  }}
                  stroke={isDarkMode ? '#94a3b8' : '#64748b'}
                  fontSize={12}
                  fontWeight={500}
                />
                <YAxis 
                  tickFormatter={(value) => `$${value.toLocaleString()}`}
                  stroke={isDarkMode ? '#94a3b8' : '#64748b'}
                  fontSize={12}
                  fontWeight={500}
                />
                <Tooltip
                  contentStyle={{
                    background: isDarkMode ? 'rgba(30, 41, 59, 0.95)' : 'rgba(255, 255, 255, 0.95)',
                    border: 'none',
                    borderRadius: 12,
                    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
                    backdropFilter: 'blur(10px)',
                  }}
                  labelFormatter={(label) => {
                    try {
                      return format(parseISO(label), 'MMM dd, yyyy');
                    } catch {
                      return label;
                    }
                  }}
                  formatter={(value, name) => [
                    `$${Number(value).toFixed(2)}`, 
                    name === 'portfolio' ? 'Portfolio' : name === 'benchmark' ? 'Benchmark' : name === 'trend' ? 'Trend Line' : name === 'marketOverlay' ? `${marketSymbol} Overlay` : name
                  ]}
                />
                <Legend 
                  wrapperStyle={{
                    paddingTop: '20px',
                    fontSize: '14px',
                    fontWeight: 600,
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="portfolio"
                  stroke="#2563eb"
                  fill="url(#portfolioGradient)"
                  strokeWidth={3}
                  name="Portfolio"
                />
                {showBenchmark && (
                  <Area
                    type="monotone"
                    dataKey="benchmark"
                    stroke="#10b981"
                    fill="url(#benchmarkGradient)"
                    strokeWidth={2}
                    strokeDasharray="5 5"
                    name="Benchmark"
                  />
                )}
                {showTrendLine && (
                  <Line
                    type="monotone"
                    dataKey="trend"
                    stroke="#f59e0b"
                    strokeWidth={3}
                    dot={false}
                    strokeDasharray="8 4"
                    name="Trend Line"
                  />
                )}
                {showMarketOverlay && (
                  <Line
                    type="monotone"
                    dataKey="marketOverlay"
                    stroke="#ef4444"
                    strokeWidth={3}
                    dot={false}
                    strokeDasharray="2 2"
                    name={`${marketSymbol} Overlay`}
                  />
                )}
              </AreaChart>
            ) : (
              <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                <defs>
                  <linearGradient id="portfolioGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2563eb" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#2563eb" stopOpacity={0.05}/>
                  </linearGradient>
                  <linearGradient id="benchmarkGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0.05}/>
                  </linearGradient>
                </defs>
          <CartesianGrid 
            strokeDasharray="3 3" 
                  stroke={isDarkMode ? 'rgba(148, 163, 184, 0.1)' : 'rgba(148, 163, 184, 0.2)'}
          />
          <XAxis
            dataKey="date"
                  tickFormatter={(value) => {
                    try {
                      return format(parseISO(value), 'MMM dd');
                    } catch {
                      return value;
                    }
                  }}
                  stroke={isDarkMode ? '#94a3b8' : '#64748b'}
            fontSize={12}
                  fontWeight={500}
          />
          <YAxis
            tickFormatter={(value) => `$${value.toLocaleString()}`}
                  stroke={isDarkMode ? '#94a3b8' : '#64748b'}
            fontSize={12}
                  fontWeight={500}
          />
          <Tooltip
            contentStyle={{
                    background: isDarkMode ? 'rgba(30, 41, 59, 0.95)' : 'rgba(255, 255, 255, 0.95)',
                    border: 'none',
                    borderRadius: 12,
                    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
                    backdropFilter: 'blur(10px)',
                  }}
                  labelFormatter={(label) => {
                    try {
                      return format(parseISO(label), 'MMM dd, yyyy');
                    } catch {
                      return label;
                    }
                  }}
                  formatter={(value, name) => [
                    `$${Number(value).toFixed(2)}`, 
                    name === 'portfolio' ? 'Portfolio' : name === 'benchmark' ? 'Benchmark' : name === 'trend' ? 'Trend Line' : name === 'marketOverlay' ? `${marketSymbol} Overlay` : name
                  ]}
                />
                <Legend 
                  wrapperStyle={{
                    paddingTop: '20px',
                    fontSize: '14px',
              fontWeight: 600,
            }}
          />
          <Line
            type="monotone"
            dataKey="portfolio"
                  stroke="#2563eb"
            strokeWidth={3}
            dot={false}
                  name="Portfolio"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
          {showBenchmark && (
            <Line
              type="monotone"
              dataKey="benchmark"
                    stroke="#10b981"
              strokeWidth={2}
              dot={false}
              strokeDasharray="5 5"
                    name="Benchmark"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                )}
          {showTrendLine && (
            <Line
              type="monotone"
              dataKey="trend"
                    stroke="#f59e0b"
              strokeWidth={3}
              dot={false}
              strokeDasharray="8 4"
                    name="Trend Line"
                  />
                )}
                {showMarketOverlay && (
                  <Line
                    type="monotone"
                    dataKey="marketOverlay"
                    stroke="#ef4444"
                    strokeWidth={3}
                    dot={false}
                    strokeDasharray="2 2"
                    name={`${marketSymbol} Overlay`}
            />
          )}
        </LineChart>
            )}
      </ResponsiveContainer>
        </Box>
      </motion.div>
      
      {/* Performance summary */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.4 }}
      >
        <Box sx={{ 
          mt: 3, 
          p: 2,
          background: isDarkMode 
            ? 'linear-gradient(145deg, #1e293b 0%, #334155 100%)'
            : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
          backdropFilter: 'none',
          borderRadius: 3,
          border: '1px solid',
          borderColor: isDarkMode 
            ? 'rgba(148, 163, 184, 0.1)'
            : 'rgba(148, 163, 184, 0.2)',
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 2
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Chip
              label={`Total Return: ${totalReturn.toFixed(2)}%`}
              color={totalReturn >= 0 ? "success" : "error"}
              variant="filled"
              sx={{ fontWeight: 600 }}
            />
            <Chip
              label={`${data.length} data points`}
              variant="outlined"
              sx={{ fontWeight: 500 }}
            />
          </Box>
          <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
            Performance from {format(parseISO(data[0]?.nav_date || ''), 'MMM dd, yyyy')} to {format(parseISO(data[data.length - 1]?.nav_date || ''), 'MMM dd, yyyy')}
        </Typography>
      </Box>
      </motion.div>
    </Box>
  );
};

export default PerformanceChart;

