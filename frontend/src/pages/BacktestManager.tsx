/**
 * Backtest Manager Page
 * Combined Dashboard and BacktestDetail with collapsible sidebar
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
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
  Drawer,
  useMediaQuery,
  useTheme as useMuiTheme,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Visibility as VisibilityIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon,
  Speed as SpeedIcon,
  ShowChart as ShowChartIcon,
  Delete as DeleteIcon,
  Menu as MenuIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  Analytics as AnalyticsIcon,
} from '@mui/icons-material';
import { Tooltip } from '@mui/material';
import { useQuery, useMutation } from 'react-query';

import { backtestApi, navApi } from '@/services/api';
import { Backtest, Portfolio } from '@/types';
import PerformanceChart from '@/components/charts/PerformanceChart';
import MetricCard from '@/components/cards/MetricCard';
import PortfolioDetail from '@/components/tables/PortfolioDetail';
import Logo from '@/components/common/Logo';
import { useTheme } from '@/contexts/ThemeContext';

const SIDEBAR_WIDTH = 320;
const COLLAPSED_WIDTH = 60;

const BacktestManager: React.FC = () => {
  const { runId } = useParams<{ runId: string }>();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const { isDarkMode } = useTheme();
  const muiTheme = useMuiTheme();
  const isMobile = useMediaQuery(muiTheme.breakpoints.down('md'));

  // State management
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
    const saved = localStorage.getItem('backtest-sidebar-collapsed');
    return saved ? JSON.parse(saved) : false;
  });
  const [selectedBacktestId, setSelectedBacktestId] = useState<string>(() => {
    return runId || localStorage.getItem('selected-backtest-id') || '';
  });
  const [selectedPortfolio, setSelectedPortfolio] = useState<Portfolio | null>(null);
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

  // Fetch selected backtest details
  const {
    data: backtest,
    isLoading: backtestLoading,
  } = useQuery(
    ['backtest', selectedBacktestId],
    () => backtestApi.getBacktest(selectedBacktestId),
    {
      enabled: !!selectedBacktestId,
    }
  );

  // Fetch backtest metrics
  const {
    data: metrics,
    isLoading: metricsLoading,
  } = useQuery(
    ['backtest-metrics', selectedBacktestId],
    () => backtestApi.getBacktestMetrics(selectedBacktestId),
    {
      enabled: !!selectedBacktestId,
    }
  );

  // Fetch portfolios
  const {
    data: portfoliosData,
    isLoading: portfoliosLoading,
  } = useQuery(
    ['backtest-portfolios', selectedBacktestId],
    () => backtestApi.getBacktestPortfolios(selectedBacktestId),
    {
      enabled: !!selectedBacktestId,
    }
  );

  // Fetch NAV data
  const {
    data: navData,
    isLoading: navLoading,
  } = useQuery(
    ['backtest-nav', selectedBacktestId],
    () => navApi.getBacktestNav(selectedBacktestId),
    {
      enabled: !!selectedBacktestId,
    }
  );

  // Fetch ONLY used signal definitions for the selected backtest
  const {
    data: usedSignalsData,
    isLoading: usedSignalsLoading,
  } = useQuery(
    ['backtest-used-signals', selectedBacktestId],
    () => backtestApi.getBacktestUsedSignals(selectedBacktestId),
    {
      enabled: !!selectedBacktestId,
      staleTime: 0,
      cacheTime: 0,
    }
  );

  // Extract unique signal names from signals data
  const uniqueSignalNames = React.useMemo(() => {
    if (!usedSignalsData?.signals) return [];
    return usedSignalsData.signals.map(s => s.name).sort();
  }, [usedSignalsData]);

  // Initialize selected backtest from URL or auto-select most recent
  useEffect(() => {
    const urlId = searchParams.get('id');
    
    if (urlId && backtestsData?.backtests) {
      // Check if URL backtest exists in the data
      const backtestExists = backtestsData.backtests.some(b => b.run_id === urlId);
      if (backtestExists && urlId !== selectedBacktestId) {
        setSelectedBacktestId(urlId);
        localStorage.setItem('selected-backtest-id', urlId);
      } else if (!backtestExists) {
        // URL backtest doesn't exist, auto-select most recent
        const mostRecent = backtestsData.backtests
          .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())[0];
        if (mostRecent && mostRecent.run_id !== selectedBacktestId) {
          setSelectedBacktestId(mostRecent.run_id);
          localStorage.setItem('selected-backtest-id', mostRecent.run_id);
          setSearchParams({ id: mostRecent.run_id });
        }
      }
    } else if (!urlId && backtestsData?.backtests && !selectedBacktestId) {
      // No URL ID and no selected backtest, auto-select most recent
      const mostRecent = backtestsData.backtests
        .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())[0];
      if (mostRecent) {
        setSelectedBacktestId(mostRecent.run_id);
        localStorage.setItem('selected-backtest-id', mostRecent.run_id);
        setSearchParams({ id: mostRecent.run_id });
      }
    }
  }, [backtestsData, searchParams, selectedBacktestId, setSearchParams]);

  // Persist sidebar state
  useEffect(() => {
    localStorage.setItem('backtest-sidebar-collapsed', JSON.stringify(sidebarCollapsed));
  }, [sidebarCollapsed]);

  const handleBacktestSelect = (backtest: Backtest) => {
    setSelectedBacktestId(backtest.run_id);
    localStorage.setItem('selected-backtest-id', backtest.run_id);
    setSearchParams({ id: backtest.run_id });
  };

  const handlePortfolioClick = (portfolio: Portfolio) => {
    setSelectedPortfolio(portfolio);
  };

  const handleBack = () => {
    navigate('/');
  };

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
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
        // Select next available backtest or redirect to home
        if (backtestsData?.backtests) {
          const remainingBacktests = backtestsData.backtests.filter(b => b.run_id !== runId);
          if (remainingBacktests.length > 0) {
            const nextBacktest = remainingBacktests[0];
            setSelectedBacktestId(nextBacktest.run_id);
          } else {
            navigate('/');
          }
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

  if (backtestsError) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        Failed to load backtests. Please check your connection and try again.
      </Alert>
    );
  }

  // Sort backtests by creation date (most recent first)
  const sortedBacktests = backtestsData?.backtests
    ?.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()) || [];

  const sidebarContent = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Sidebar Header */}
      {!sidebarCollapsed && (
        <Box sx={{ 
          p: 2, 
          borderBottom: `1px solid ${isDarkMode ? 'rgba(148, 163, 184, 0.1)' : 'rgba(148, 163, 184, 0.2)'}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          minHeight: 64
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Logo size="small" showText={false} clickable={true} />
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Backtests
            </Typography>
          </Box>
          <IconButton onClick={toggleSidebar} size="small">
            <ChevronLeftIcon />
          </IconButton>
        </Box>
      )}

      {/* Backtests List or Expand Button */}
      {sidebarCollapsed ? (
        // Collapsed view - show only expand button
        <Box sx={{ 
          flex: 1, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          p: 2
        }}>
          <Tooltip title="Expand sidebar to view backtests" placement="right" arrow>
            <IconButton
              onClick={toggleSidebar}
              sx={{
                width: 40,
                height: 40,
                background: isDarkMode 
                  ? 'linear-gradient(145deg, #1e40af 0%, #2563eb 100%)'
                  : 'linear-gradient(145deg, #dbeafe 0%, #bfdbfe 100%)',
                color: isDarkMode ? '#ffffff' : '#1e40af',
                border: isDarkMode 
                  ? '1px solid #3b82f6'
                  : '1px solid #60a5fa',
                boxShadow: isDarkMode 
                  ? '0 8px 32px 0 rgba(59, 130, 246, 0.3)'
                  : '0 8px 32px 0 rgba(59, 130, 246, 0.2)',
                '&:hover': {
                  background: isDarkMode 
                    ? 'linear-gradient(145deg, #1d4ed8 0%, #1e40af 100%)'
                    : 'linear-gradient(145deg, #bfdbfe 0%, #93c5fd 100%)',
                  transform: 'scale(1.05)',
                  boxShadow: isDarkMode 
                    ? '0 12px 40px 0 rgba(59, 130, 246, 0.4)'
                    : '0 12px 40px 0 rgba(59, 130, 246, 0.3)',
                },
                transition: 'all 0.2s ease-in-out',
              }}
            >
              <ChevronRightIcon />
            </IconButton>
          </Tooltip>
        </Box>
      ) : (
        // Expanded view - show backtests list
        <Box sx={{ 
          flex: 1, 
          overflow: 'auto', 
          p: 1,
          '&::-webkit-scrollbar': {
            width: '6px',
          },
          '&::-webkit-scrollbar-track': {
            background: isDarkMode ? '#1e293b' : '#f1f5f9',
            borderRadius: '3px',
          },
          '&::-webkit-scrollbar-thumb': {
            background: isDarkMode 
              ? 'linear-gradient(135deg, #475569 0%, #64748b 100%)'
              : 'linear-gradient(135deg, #cbd5e1 0%, #94a3b8 100%)',
            borderRadius: '3px',
            '&:hover': {
              background: isDarkMode 
                ? 'linear-gradient(135deg, #64748b 0%, #94a3b8 100%)'
                : 'linear-gradient(135deg, #94a3b8 0%, #64748b 100%)',
            },
          },
        }}>
          {backtestsLoading ? (
            <Box>
              {[...Array(5)].map((_, index) => (
                <Skeleton 
                  key={index} 
                  variant="rectangular" 
                  height={80} 
                  sx={{ mb: 1, borderRadius: 2 }} 
                />
              ))}
            </Box>
          ) : (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              {sortedBacktests.map((backtest) => (
                <Card
                  key={backtest.run_id}
                  sx={{
                    cursor: 'pointer',
                    transition: 'all 0.2s ease-in-out',
                    background: selectedBacktestId === backtest.run_id
                      ? isDarkMode 
                        ? 'linear-gradient(145deg, #1e40af 0%, #2563eb 100%)'
                        : 'linear-gradient(145deg, #dbeafe 0%, #bfdbfe 100%)'
                      : isDarkMode 
                        ? 'linear-gradient(145deg, #1e293b 0%, #334155 100%)'
                        : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
                    border: selectedBacktestId === backtest.run_id
                      ? isDarkMode 
                        ? '1px solid #3b82f6'
                        : '1px solid #60a5fa'
                      : isDarkMode 
                        ? '1px solid rgba(148, 163, 184, 0.3)'
                        : '1px solid rgba(148, 163, 184, 0.4)',
                    boxShadow: selectedBacktestId === backtest.run_id
                      ? isDarkMode 
                        ? '0 8px 32px 0 rgba(59, 130, 246, 0.3)'
                        : '0 8px 32px 0 rgba(59, 130, 246, 0.2)'
                      : isDarkMode 
                        ? '0 4px 16px 0 rgba(0, 0, 0, 0.3)'
                        : '0 4px 16px 0 rgba(0, 0, 0, 0.1)',
                    '&:hover': {
                      transform: 'translateY(-1px)',
                      boxShadow: selectedBacktestId === backtest.run_id
                        ? isDarkMode 
                          ? '0 12px 40px 0 rgba(59, 130, 246, 0.4)'
                          : '0 12px 40px 0 rgba(59, 130, 246, 0.3)'
                        : isDarkMode 
                          ? '0 8px 24px 0 rgba(0, 0, 0, 0.4)'
                          : '0 8px 24px 0 rgba(0, 0, 0, 0.15)',
                    },
                  }}
                  onClick={() => handleBacktestSelect(backtest)}
                >
                  <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                      <Typography 
                        variant="body1" 
                        component="div" 
                        sx={{ 
                          fontWeight: 600,
                          color: selectedBacktestId === backtest.run_id 
                            ? isDarkMode ? '#ffffff' : '#1e40af'
                            : 'inherit',
                          fontSize: '0.875rem',
                          lineHeight: 1.3
                        }}
                      >
                        {backtest.name || backtest.run_id}
                      </Typography>
                      <Chip 
                        label={backtest.frequency} 
                        size="small" 
                        color="primary" 
                        variant="outlined"
                        sx={{ fontSize: '0.75rem', height: 20 }}
                      />
                    </Box>
                    <Typography 
                      variant="body2" 
                      color={selectedBacktestId === backtest.run_id 
                        ? isDarkMode ? 'rgba(255, 255, 255, 0.8)' : 'rgba(30, 64, 175, 0.8)'
                        : 'text.secondary'
                      }
                      sx={{ fontSize: '0.75rem', mb: 0.5 }}
                    >
                      {backtest.start_date} to {backtest.end_date}
                    </Typography>
                    <Typography 
                      variant="body2" 
                      color={selectedBacktestId === backtest.run_id 
                        ? isDarkMode ? 'rgba(255, 255, 255, 0.7)' : 'rgba(30, 64, 175, 0.7)'
                        : 'text.secondary'
                      }
                      sx={{ fontSize: '0.75rem', mb: 0.5 }}
                    >
                      Universe: {backtest.universe_name || 'Unknown'}
                    </Typography>
                    <Typography 
                      variant="body2" 
                      color={selectedBacktestId === backtest.run_id 
                        ? isDarkMode ? 'rgba(255, 255, 255, 0.6)' : 'rgba(30, 64, 175, 0.6)'
                        : 'text.secondary'
                      }
                      sx={{ fontSize: '0.75rem' }}
                    >
                      Created: {new Date(backtest.created_at).toLocaleDateString()}
                    </Typography>
                  </CardContent>
                </Card>
              ))}
            </Box>
          )}
        </Box>
      )}
    </Box>
  );

  return (
    <Box sx={{ 
      display: 'flex', 
      height: '100vh', 
      overflow: 'hidden',
      '&::-webkit-scrollbar': {
        width: '8px',
      },
      '&::-webkit-scrollbar-track': {
        background: isDarkMode ? '#1e293b' : '#f1f5f9',
        borderRadius: '4px',
      },
      '&::-webkit-scrollbar-thumb': {
        background: isDarkMode 
          ? 'linear-gradient(135deg, #475569 0%, #64748b 100%)'
          : 'linear-gradient(135deg, #cbd5e1 0%, #94a3b8 100%)',
        borderRadius: '4px',
        border: isDarkMode ? '1px solid #334155' : '1px solid #e2e8f0',
        '&:hover': {
          background: isDarkMode 
            ? 'linear-gradient(135deg, #64748b 0%, #94a3b8 100%)'
            : 'linear-gradient(135deg, #94a3b8 0%, #64748b 100%)',
        },
      },
    }}>
      {/* Sidebar */}
      {isMobile ? (
        <Drawer
          variant="temporary"
          open={!sidebarCollapsed}
          onClose={() => setSidebarCollapsed(true)}
          sx={{
            '& .MuiDrawer-paper': {
              width: SIDEBAR_WIDTH,
              background: isDarkMode 
                ? 'linear-gradient(145deg, #1e293b 0%, #334155 100%)'
                : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
              border: 'none',
            },
          }}
        >
          {sidebarContent}
        </Drawer>
      ) : (
        <Box
          sx={{
            width: sidebarCollapsed ? COLLAPSED_WIDTH : SIDEBAR_WIDTH,
            transition: 'width 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            background: isDarkMode 
              ? 'linear-gradient(145deg, #1e293b 0%, #334155 100%)'
              : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
            borderRight: `1px solid ${isDarkMode ? 'rgba(148, 163, 184, 0.1)' : 'rgba(148, 163, 184, 0.2)'}`,
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
          }}
        >
          {sidebarContent}
        </Box>
      )}

      {/* Mobile sidebar toggle button */}
      {isMobile && (
        <IconButton
          onClick={toggleSidebar}
          sx={{
            position: 'fixed',
            top: 16,
            left: 16,
            zIndex: 1300,
            background: isDarkMode 
              ? 'linear-gradient(145deg, #1e293b 0%, #334155 100%)'
              : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
            border: `1px solid ${isDarkMode ? 'rgba(148, 163, 184, 0.3)' : 'rgba(148, 163, 184, 0.4)'}`,
            '&:hover': {
              background: isDarkMode 
                ? 'linear-gradient(145deg, #334155 0%, #475569 100%)'
                : 'linear-gradient(145deg, #f8fafc 0%, #e2e8f0 100%)',
            },
          }}
        >
          <MenuIcon />
        </IconButton>
      )}

      {/* Main Content */}
      <Box sx={{ 
        flex: 1, 
        overflow: 'auto', 
        p: 3,
        '&::-webkit-scrollbar': {
          width: '8px',
        },
        '&::-webkit-scrollbar-track': {
          background: isDarkMode ? '#1e293b' : '#f1f5f9',
          borderRadius: '4px',
        },
        '&::-webkit-scrollbar-thumb': {
          background: isDarkMode 
            ? 'linear-gradient(135deg, #475569 0%, #64748b 100%)'
            : 'linear-gradient(135deg, #cbd5e1 0%, #94a3b8 100%)',
          borderRadius: '4px',
          border: isDarkMode ? '1px solid #334155' : '1px solid #e2e8f0',
          '&:hover': {
            background: isDarkMode 
              ? 'linear-gradient(135deg, #64748b 0%, #94a3b8 100%)'
              : 'linear-gradient(135deg, #94a3b8 0%, #64748b 100%)',
          },
        },
        '&::-webkit-scrollbar-corner': {
          background: isDarkMode ? '#1e293b' : '#f1f5f9',
        },
      }}>
        {!selectedBacktestId ? (
          <Box sx={{ 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center', 
            justifyContent: 'center', 
            height: '100%',
            textAlign: 'center'
          }}>
            <Typography variant="h5" color="text.secondary" sx={{ mb: 2 }}>
              Select a backtest to view details
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Choose a backtest from the sidebar to see its performance metrics and portfolio details.
            </Typography>
          </Box>
        ) : (
          <Box>
            {/* Header */}
            <Box sx={{ mb: 4 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Button
                  startIcon={<ArrowBackIcon />}
                  onClick={handleBack}
                  sx={{ mr: 2 }}
                >
                  Back to Home
                </Button>
              </Box>
              
              {backtestLoading ? (
                <Skeleton variant="rectangular" height={60} />
              ) : backtest ? (
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
              ) : (
                <Alert severity="warning">
                  Backtest not found.
                </Alert>
              )}
            </Box>

            {/* Signals Section */}
            {backtest && (
              <Card sx={{ mb: 4 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <AnalyticsIcon sx={{ mr: 1, color: 'primary.main' }} />
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      Signals Used in This Backtest
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    The following signals were used to create this backtest:
                  </Typography>
                  {usedSignalsLoading ? (
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      {[...Array(3)].map((_, index) => (
                        <Skeleton key={index} variant="rectangular" width={80} height={32} sx={{ borderRadius: 1 }} />
                      ))}
                    </Box>
                  ) : uniqueSignalNames.length > 0 ? (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {uniqueSignalNames.map((signalName) => (
                        <Chip
                          key={signalName}
                          label={signalName}
                          color="secondary"
                          variant="filled"
                          sx={{
                            fontWeight: 500,
                            backgroundColor: isDarkMode 
                              ? 'rgba(156, 39, 176, 0.2)'
                              : 'rgba(156, 39, 176, 0.1)',
                            color: isDarkMode 
                              ? '#ce93d8'
                              : '#7b1fa2',
                            border: isDarkMode 
                              ? '1px solid rgba(156, 39, 176, 0.3)'
                              : '1px solid rgba(156, 39, 176, 0.2)',
                          }}
                        />
                      ))}
                    </Box>
                  ) : (
                    <Alert severity="info" sx={{ mt: 1 }}>
                      No signals found for this backtest.
                    </Alert>
                  )}
                </CardContent>
              </Card>
            )}

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
            <Box sx={{ mb: 20, pb: 5 }}>
              <Typography variant="h6" gutterBottom sx={{ mb: 3 }}>
                Performance Overview
              </Typography>
              {navLoading ? (
                <Skeleton variant="rectangular" height={450} />
              ) : (
                <Box sx={{ mb: 5 }}>
                  <PerformanceChart
                    data={navData?.nav_data || []}
                    height={450}
                    showBenchmark={true}
                    backtestStartDate={backtest?.start_date}
                    backtestEndDate={backtest?.end_date}
                  />
                </Box>
              )}
            </Box>

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
          </Box>
        )}
      </Box>

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

export default BacktestManager;
