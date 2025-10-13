/**
 * Backtest Detail Page
 * Displays detailed information about a specific backtest
 */

import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  Divider,
  Alert,
  Skeleton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Snackbar,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Visibility as VisibilityIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon,
  Speed as SpeedIcon,
  ShowChart as ShowChartIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { useQuery, useMutation } from 'react-query';

import { backtestApi, navApi } from '@/services/api';
import { Portfolio } from '@/types';
import PerformanceChart from '@/components/charts/PerformanceChart';
import MetricCard from '@/components/cards/MetricCard';
import PortfolioDetail from '@/components/tables/PortfolioDetail';

const BacktestDetail: React.FC = () => {
  const { runId } = useParams<{ runId: string }>();
  const navigate = useNavigate();
  const [selectedPortfolio, setSelectedPortfolio] = useState<Portfolio | null>(null);
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error';
  }>({ open: false, message: '', severity: 'success' });

  // Fetch backtest details
  const {
    data: backtest,
    isLoading: backtestLoading,
    error: backtestError,
  } = useQuery(
    ['backtest', runId],
    () => backtestApi.getBacktest(runId!),
    {
      enabled: !!runId,
    }
  );

  // Fetch backtest metrics
  const {
    data: metrics,
    isLoading: metricsLoading,
    error: metricsError,
  } = useQuery(
    ['backtest-metrics', runId],
    () => backtestApi.getBacktestMetrics(runId!),
    {
      enabled: !!runId,
    }
  );

  // Fetch portfolios
  const {
    data: portfoliosData,
    isLoading: portfoliosLoading,
    error: portfoliosError,
  } = useQuery(
    ['backtest-portfolios', runId],
    () => backtestApi.getBacktestPortfolios(runId!),
    {
      enabled: !!runId,
    }
  );

  // Fetch NAV data
  const {
    data: navData,
    isLoading: navLoading,
  } = useQuery(
    ['backtest-nav', runId],
    () => navApi.getBacktestNav(runId!),
    {
      enabled: !!runId,
    }
  );

  const handlePortfolioClick = (portfolio: Portfolio) => {
    setSelectedPortfolio(portfolio);
  };

  const handleBack = () => {
    navigate('/');
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
        // Redirect to dashboard after successful deletion
        setTimeout(() => {
          navigate('/');
        }, 2000);
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

  const handleDeleteBacktest = () => {
    if (!backtest) return;
    
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

  if (backtestError || metricsError || portfoliosError) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        Failed to load backtest details. Please check your connection and try again.
      </Alert>
    );
  }

  if (backtestLoading) {
    return (
      <Box>
        <Skeleton variant="rectangular" height={60} sx={{ mb: 2 }} />
        <Grid container spacing={3}>
          {[...Array(4)].map((_, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Skeleton variant="rectangular" height={120} />
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  if (!backtest) {
    return (
      <Alert severity="warning" sx={{ mt: 2 }}>
        Backtest not found.
      </Alert>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={handleBack}
            sx={{ mr: 2 }}
          >
            Back to Dashboard
          </Button>
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box>
            <Typography variant="h4" component="h1" sx={{ fontWeight: 700 }}>
              {backtest.name || backtest.run_id}
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {backtest.start_date} to {backtest.end_date}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Universe: {backtest.universe_name || 'Unknown'}
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Chip 
              label={backtest.frequency} 
              color="primary" 
              variant="outlined"
              size="medium"
            />
            <Button
              variant="outlined"
              color="error"
              startIcon={<DeleteIcon />}
              onClick={handleDeleteBacktest}
              disabled={deleteBacktestMutation.isLoading}
              sx={{
                '&:hover': {
                  backgroundColor: 'error.light',
                  color: 'white'
                }
              }}
            >
              Delete Backtest
            </Button>
          </Box>
        </Box>
      </Box>

      {/* Performance Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Return"
            value={metrics?.total_return}
            unit="%"
            icon={<TrendingUpIcon />}
            color="success"
            loading={metricsLoading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Sharpe Ratio"
            value={metrics?.sharpe_ratio}
            icon={<AssessmentIcon />}
            color="primary"
            loading={metricsLoading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Max Drawdown"
            value={metrics?.max_drawdown}
            unit="%"
            icon={<ShowChartIcon />}
            color="error"
            loading={metricsLoading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Volatility"
            value={metrics?.volatility}
            unit="%"
            icon={<SpeedIcon />}
            color="warning"
            loading={metricsLoading}
          />
        </Grid>
      </Grid>

      {/* Performance Chart */}
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
              showBenchmark={true}
              showTrendLine={true}
              backtestStartDate={backtest.start_date}
              backtestEndDate={backtest.end_date}
            />
          )}
        </CardContent>
      </Card>

      {/* Portfolios Section */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Portfolio Rebalancing History
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            {portfoliosData?.total || 0} portfolio rebalances
          </Typography>

          {portfoliosLoading ? (
            <Box>
              {[...Array(5)].map((_, index) => (
                <Skeleton key={index} variant="rectangular" height={60} sx={{ mb: 1 }} />
              ))}
            </Box>
          ) : (
            <List>
              {portfoliosData?.portfolios.map((portfolio, index) => (
                <React.Fragment key={portfolio.id}>
                  <ListItem
                    sx={{
                      cursor: 'pointer',
                      borderRadius: 1,
                      mb: 1,
                      '&:hover': {
                        backgroundColor: 'action.hover',
                      },
                    }}
                    onClick={() => handlePortfolioClick(portfolio)}
                  >
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                          <Typography variant="body1" sx={{ fontWeight: 500 }}>
                            {portfolio.asof_date}
                          </Typography>
                          <Chip 
                            label={portfolio.method} 
                            size="small" 
                            color="secondary" 
                            variant="outlined"
                          />
                          <Typography variant="body2" color="text.secondary">
                            {portfolio.position_count || 0} positions
                          </Typography>
                        </Box>
                      }
                      secondary={
                        <Typography variant="body2" color="text.secondary">
                          Portfolio ID: {portfolio.id} • Portfolio Value: ${portfolio.total_value?.toFixed(2) || 'N/A'}
                        </Typography>
                      }
                    />
                    <ListItemSecondaryAction>
                      <IconButton edge="end" size="small">
                        <VisibilityIcon />
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>
                  {index < (portfoliosData?.portfolios.length || 0) - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          )}
        </CardContent>
      </Card>

      {/* Portfolio Detail Panel */}
      {selectedPortfolio && (
        <PortfolioDetail
          portfolio={selectedPortfolio}
          onClose={() => setSelectedPortfolio(null)}
        />
      )}

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

export default BacktestDetail;

