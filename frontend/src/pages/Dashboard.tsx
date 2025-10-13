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
  IconButton,
  Snackbar,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  ShowChart as ShowChartIcon,
  Assessment as AssessmentIcon,
  Speed as SpeedIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';

import { backtestApi, navApi } from '@/services/api';
import { Backtest } from '@/types';
import PerformanceChart from '@/components/charts/PerformanceChart';
import MetricCard from '@/components/cards/MetricCard';
import Logo from '@/components/common/Logo';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [selectedBacktest, setSelectedBacktest] = useState<string>('');
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error';
  }>({ open: false, message: '', severity: 'success' });

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

  // Delete backtest mutation
  const deleteBacktestMutation = useMutation(
    (runId: string) => backtestApi.deleteBacktest(runId),
    {
      onSuccess: (data) => {
        setSnackbar({
          open: true,
          message: data.message,
          severity: 'success'
        });
        // Refresh the backtests list
        queryClient.invalidateQueries('backtests');
        // Clear selected backtest if it was deleted
        if (selectedBacktest === data.run_id) {
          setSelectedBacktest('');
        }
      },
      onError: (error: any) => {
        setSnackbar({
          open: true,
          message: error.response?.data?.detail || error.message || 'Failed to delete backtest',
          severity: 'error'
        });
      },
    }
  );

  const handleDeleteBacktest = (backtest: Backtest, event: React.MouseEvent) => {
    event.stopPropagation(); // Prevent card click
    const confirmed = window.confirm(
      `Are you sure you want to delete the backtest "${backtest.name || backtest.run_id}"?\n\nThis will permanently delete:\n- The backtest configuration\n- All portfolio data\n- All NAV data\n- All associated positions\n\nThis action cannot be undone.`
    );
    
    if (confirmed) {
      deleteBacktestMutation.mutate(backtest.run_id);
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
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
            <InputLabel shrink={!!selectedBacktest}>Choose a backtest to analyze</InputLabel>
            <Select
              value={selectedBacktest}
              onChange={(e) => handleBacktestChange(e.target.value)}
              disabled={backtestsLoading}
              label="Choose a backtest to analyze"
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
              <Skeleton variant="rectangular" height={400} />
            ) : (
              <PerformanceChart
                data={navData?.nav_data || []}
                height={400}
                showTrendLine={true}
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
                      '&:hover': {
                        transform: 'translateY(-2px)',
                        boxShadow: 4,
                      },
                    }}
                    onClick={() => handleBacktestClick(backtest)}
                  >
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                        <Typography variant="h6" component="div" sx={{ fontWeight: 600 }}>
                          {backtest.name || backtest.run_id}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Chip 
                            label={backtest.frequency} 
                            size="small" 
                            color="primary" 
                            variant="outlined"
                          />
                          <IconButton
                            size="small"
                            color="error"
                            onClick={(e) => handleDeleteBacktest(backtest, e)}
                            disabled={deleteBacktestMutation.isLoading}
                            sx={{
                              opacity: 0.7,
                              '&:hover': {
                                opacity: 1,
                                backgroundColor: 'error.light',
                                color: 'white'
                              }
                            }}
                          >
                            <DeleteIcon fontSize="small" />
                          </IconButton>
                        </Box>
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

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={snackbar.severity} 
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Dashboard;

