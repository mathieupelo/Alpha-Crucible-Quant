/**
 * Main Dashboard Page
 * Displays overview of all backtests with performance metrics
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Skeleton,
  Alert,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  ShowChart as ShowChartIcon,
  Assessment as AssessmentIcon,
  Speed as SpeedIcon,
} from '@mui/icons-material';
import { useQuery } from 'react-query';

import { backtestApi, navApi } from '@/services/api';
import { Backtest } from '@/types';
import PerformanceChart from '@/components/charts/PerformanceChart';
import MetricCard from '@/components/cards/MetricCard';
import Logo from '@/components/common/Logo';
import { useTheme } from '@/contexts/ThemeContext';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { isDarkMode } = useTheme();
  const [selectedBacktest, setSelectedBacktest] = useState<string>('');

  // Fetch backtests
  const {
    data: backtestsData,
    isLoading: backtestsLoading,
    error: backtestsError,
  } = useQuery('backtests', () => backtestApi.getBacktests(1, 100));

  // Fetch metrics for selected backtest
  const {
    data: metricsData,
    isLoading: metricsLoading,
  } = useQuery(
    ['backtest-metrics', selectedBacktest],
    () => backtestApi.getBacktestMetrics(selectedBacktest),
    {
      enabled: !!selectedBacktest,
    }
  );

  // Fetch NAV data for selected backtest
  const {
    data: navData,
    isLoading: navLoading,
  } = useQuery(
    ['backtest-nav', selectedBacktest],
    () => navApi.getBacktestNav(selectedBacktest),
    {
      enabled: !!selectedBacktest,
    }
  );

  const handleBacktestChange = (runId: string) => {
    setSelectedBacktest(runId);
  };

  const handleBacktestClick = (backtest: Backtest) => {
    navigate(`/backtest/${backtest.run_id}`);
  };

  if (backtestsError) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        Failed to load backtests. Please check your connection and try again.
      </Alert>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <Logo size="medium" showText={false} clickable={true} />
          <Typography variant="h4" component="h1" sx={{ fontWeight: 700 }}>
            Dashboard
          </Typography>
        </Box>
        <Typography variant="body1" color="text.secondary">
          Monitor and analyze your quantitative trading strategies
        </Typography>
      </Box>

      {/* Backtest Selector */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Select Backtest
          </Typography>
          <FormControl fullWidth>
            <InputLabel 
              shrink={!!selectedBacktest}
              sx={{
                color: isDarkMode ? '#94a3b8' : '#64748b',
                '&.Mui-focused': {
                  color: isDarkMode ? '#2563eb' : '#1d4ed8',
                }
              }}
            >
              Choose a backtest to analyze
            </InputLabel>
            <Select
              value={selectedBacktest}
              onChange={(e) => handleBacktestChange(e.target.value)}
              disabled={backtestsLoading}
              label="Choose a backtest to analyze"
              sx={{
                '& .MuiSelect-select': {
                  py: 2,
                },
                background: isDarkMode
                  ? 'linear-gradient(145deg, #1e293b 0%, #334155 100%)'
                  : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
                '& .MuiOutlinedInput-notchedOutline': {
                  borderColor: isDarkMode ? 'rgba(148, 163, 184, 0.3)' : 'rgba(148, 163, 184, 0.4)',
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
              {backtestsData?.backtests.map((backtest) => (
                <MenuItem key={backtest.run_id} value={backtest.run_id}>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
                    <Box>
                      <Typography variant="body1">{backtest.name || backtest.run_id}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        {backtest.start_date} to {backtest.end_date}
                      </Typography>
                    </Box>
                    <Chip 
                      label={backtest.frequency} 
                      size="small" 
                      color="primary" 
                      variant="outlined"
                    />
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </CardContent>
      </Card>

      {/* Metrics Cards */}
      {selectedBacktest && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="Total Return"
              value={metricsData?.total_return}
              unit="%"
              icon={<TrendingUpIcon />}
              color="success"
              loading={metricsLoading}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="Sharpe Ratio"
              value={metricsData?.sharpe_ratio}
              icon={<AssessmentIcon />}
              color="primary"
              loading={metricsLoading}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="Max Drawdown"
              value={metricsData?.max_drawdown}
              unit="%"
              icon={<ShowChartIcon />}
              color="error"
              loading={metricsLoading}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="Volatility"
              value={metricsData?.volatility}
              unit="%"
              icon={<SpeedIcon />}
              color="warning"
              loading={metricsLoading}
            />
          </Grid>
        </Grid>
      )}

      {/* Performance Chart */}
      {selectedBacktest && (
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Performance Overview
            </Typography>
            {navLoading ? (
              <Skeleton variant="rectangular" height={500} />
            ) : (
              <PerformanceChart
                data={navData?.nav_data || []}
                height={500}
                showBenchmark={true}
                backtestStartDate={backtestsData?.backtests.find(b => b.run_id === selectedBacktest)?.start_date}
                backtestEndDate={backtestsData?.backtests.find(b => b.run_id === selectedBacktest)?.end_date}
              />
            )}
          </CardContent>
        </Card>
      )}

      {/* Backtests List */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            All Backtests
          </Typography>
          {backtestsLoading ? (
            <Box>
              {[...Array(5)].map((_, index) => (
                <Skeleton key={index} variant="rectangular" height={80} sx={{ mb: 2 }} />
              ))}
            </Box>
          ) : (
            <Grid container spacing={2}>
              {backtestsData?.backtests.map((backtest) => (
                <Grid item xs={12} md={6} lg={4} key={backtest.run_id}>
                  <Card
                    sx={{
                      cursor: 'pointer',
                      transition: 'all 0.2s ease-in-out',
                      background: isDarkMode 
                        ? 'linear-gradient(145deg, #1e293b 0%, #334155 100%)'
                        : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
                      border: isDarkMode 
                        ? '1px solid rgba(148, 163, 184, 0.3)'
                        : '1px solid rgba(148, 163, 184, 0.4)',
                      boxShadow: isDarkMode 
                        ? '0 8px 32px 0 rgba(0, 0, 0, 0.5), 0 4px 16px 0 rgba(0, 0, 0, 0.4)'
                        : '0 8px 32px 0 rgba(0, 0, 0, 0.2), 0 4px 16px 0 rgba(0, 0, 0, 0.15)',
                      '&:hover': {
                        transform: 'translateY(-2px)',
                        boxShadow: isDarkMode 
                          ? '0 12px 40px 0 rgba(0, 0, 0, 0.6), 0 8px 24px 0 rgba(0, 0, 0, 0.5)'
                          : '0 12px 40px 0 rgba(0, 0, 0, 0.25), 0 8px 24px 0 rgba(0, 0, 0, 0.2)',
                      },
                    }}
                    onClick={() => handleBacktestClick(backtest)}
                  >
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                        <Typography variant="h6" component="div" sx={{ fontWeight: 600 }}>
                          {backtest.name || backtest.run_id}
                        </Typography>
                        <Chip 
                          label={backtest.frequency} 
                          size="small" 
                          color="primary" 
                          variant="outlined"
                        />
                      </Box>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        {backtest.start_date} to {backtest.end_date}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Universe: {backtest.universe_name || 'Unknown'}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Created: {new Date(backtest.created_at).toLocaleDateString()}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default Dashboard;

