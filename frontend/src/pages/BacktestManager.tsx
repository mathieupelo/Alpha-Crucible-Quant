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
  Alert,
  Skeleton,
  IconButton,
  Snackbar,
  Drawer,
  useMediaQuery,
  useTheme as useMuiTheme,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Accordion,
  AccordionSummary,
  AccordionDetails,
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
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  AccountBalanceWallet as AccountBalanceWalletIcon,
  BarChart as BarChartIcon,
  Insights as InsightsIcon,
  Timeline as TimelineIcon,
} from '@mui/icons-material';
import { Tooltip } from '@mui/material';
import { useQuery, useMutation } from 'react-query';

import { backtestApi, navApi, portfolioApi } from '@/services/api';
import { Backtest, Portfolio } from '@/types';
import PerformanceChart from '@/components/charts/PerformanceChart';
import MetricCard from '@/components/cards/MetricCard';
import PortfolioDetail from '@/components/tables/PortfolioDetail';
import Logo from '@/components/common/Logo';
import AnimatedBackground from '@/components/common/AnimatedBackground';
import GradientMesh from '@/components/common/GradientMesh';
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
  const [expandedSignals, setExpandedSignals] = useState<Set<string>>(new Set());
  const [expandedPortfolios, setExpandedPortfolios] = useState<Set<number>>(new Set());
  const [mainTab, setMainTab] = useState(0);
  const [portfolioScoreData, setPortfolioScoreData] = useState<Map<number, {
    signals?: any[];
    scores?: any[];
    positions?: any[];
    universeTickers?: string[];
  }>>(new Map());
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

  // Extract unique signals with descriptions (deduped by name)
  const uniqueSignals = React.useMemo(() => {
    if (!usedSignalsData?.signals) return [] as Array<{ name: string; description?: string }>;
    const nameToDescription = new Map<string, string | undefined>();
    usedSignalsData.signals.forEach(s => {
      if (!nameToDescription.has(s.name)) {
        nameToDescription.set(s.name, s.description);
      }
    });
    return Array.from(nameToDescription.entries())
      .map(([name, description]) => ({ name, description }))
      .sort((a, b) => a.name.localeCompare(b.name));
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

  const toggleSignalExpansion = (signalName: string) => {
    setExpandedSignals(prev => {
      const next = new Set(prev);
      if (next.has(signalName)) {
        next.delete(signalName);
      } else {
        next.add(signalName);
      }
      return next;
    });
  };

  const togglePortfolioExpansion = async (portfolioId: number) => {
    setExpandedPortfolios(prev => {
      const next = new Set(prev);
      if (next.has(portfolioId)) {
        next.delete(portfolioId);
      } else {
        next.add(portfolioId);
        // Fetch portfolio score data when expanding
        if (!portfolioScoreData.has(portfolioId)) {
          Promise.all([
            portfolioApi.getPortfolioSignals(portfolioId),
            portfolioApi.getPortfolioScores(portfolioId),
            portfolioApi.getPortfolioUniverseTickers(portfolioId),
            portfolioApi.getPortfolioPositions(portfolioId),
          ]).then(([signals, scores, universeTickers, positions]) => {
            setPortfolioScoreData(prev => new Map(prev).set(portfolioId, {
              signals: signals.signals,
              scores: scores.scores,
              positions: positions.positions,
              universeTickers: universeTickers.tickers,
            }));
          }).catch(err => {
            console.error('Error fetching portfolio score data:', err);
          });
        }
      }
      return next;
    });
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
            borderRadius: '1px', // Minimal border radius
          },
          '&::-webkit-scrollbar-thumb': {
            background: isDarkMode 
              ? 'linear-gradient(135deg, #475569 0%, #64748b 100%)'
              : 'linear-gradient(135deg, #cbd5e1 0%, #94a3b8 100%)',
            borderRadius: '1px', // Minimal border radius
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
                  sx={{ mb: 1, borderRadius: 1 }} // Minimal border radius 
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
      position: 'relative',
      '&::-webkit-scrollbar': {
        width: '8px',
      },
      '&::-webkit-scrollbar-track': {
        background: isDarkMode ? '#1e293b' : '#f1f5f9',
        borderRadius: '1px', // Minimal border radius
      },
      '&::-webkit-scrollbar-thumb': {
        background: isDarkMode 
          ? 'linear-gradient(135deg, #475569 0%, #64748b 100%)'
          : 'linear-gradient(135deg, #cbd5e1 0%, #94a3b8 100%)',
        borderRadius: '1px', // Minimal border radius
        border: isDarkMode ? '1px solid #334155' : '1px solid #e2e8f0',
        '&:hover': {
          background: isDarkMode 
            ? 'linear-gradient(135deg, #64748b 0%, #94a3b8 100%)'
            : 'linear-gradient(135deg, #94a3b8 0%, #64748b 100%)',
        },
      },
    }}>
      {/* Animated Backgrounds */}
      <GradientMesh />
      <AnimatedBackground />

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
                ? 'rgba(30, 41, 59, 0.95)'
                : 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(20px)',
              border: 'none',
              position: 'relative',
              zIndex: 2,
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
              ? 'rgba(30, 41, 59, 0.95)'
              : 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(20px)',
            borderRight: `1px solid ${isDarkMode ? 'rgba(148, 163, 184, 0.2)' : 'rgba(148, 163, 184, 0.3)'}`,
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            position: 'relative',
            zIndex: 2,
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
              ? 'rgba(30, 41, 59, 0.95)'
              : 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(20px)',
            border: `1px solid ${isDarkMode ? 'rgba(148, 163, 184, 0.3)' : 'rgba(148, 163, 184, 0.4)'}`,
            '&:hover': {
              background: isDarkMode 
                ? 'rgba(51, 65, 85, 0.95)'
                : 'rgba(248, 250, 252, 0.95)',
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
        pb: 10,
        position: 'relative',
        zIndex: 1,
        '&::-webkit-scrollbar': {
          width: '8px',
        },
        '&::-webkit-scrollbar-track': {
          background: isDarkMode ? '#1e293b' : '#f1f5f9',
          borderRadius: '1px', // Minimal border radius
        },
        '&::-webkit-scrollbar-thumb': {
          background: isDarkMode 
            ? 'linear-gradient(135deg, #475569 0%, #64748b 100%)'
            : 'linear-gradient(135deg, #cbd5e1 0%, #94a3b8 100%)',
          borderRadius: '1px', // Minimal border radius
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
            <Box sx={{ mb: 3 }}>
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
                <Card sx={{ mb: 3, background: isDarkMode ? 'rgba(30,41,59,0.85)' : 'rgba(255,255,255,0.95)', backdropFilter: 'blur(20px)' }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 2 }}>
                      <Box sx={{ flex: 1, minWidth: 300 }}>
                        <Typography variant="h4" component="h1" sx={{ fontWeight: 700, mb: 1 }}>
                          {backtest.name || backtest.run_id}
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, alignItems: 'center' }}>
                          <Typography variant="body2" color="text.secondary">
                            {backtest.start_date} to {backtest.end_date}
                          </Typography>
                          <Chip 
                            label={backtest.frequency} 
                            color="primary" 
                            variant="outlined"
                            size="small"
                          />
                          <Typography variant="body2" color="text.secondary">
                            Universe: {backtest.universe_name || 'Unknown'}
                          </Typography>
                        </Box>
                      </Box>
                      <Button
                        variant="outlined"
                        color="error"
                        startIcon={<DeleteIcon />}
                        onClick={handleDeleteBacktest}
                        disabled={deleteBacktestMutation.isLoading}
                        size="small"
                      >
                        Delete
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              ) : (
                <Alert severity="warning">
                  Backtest not found.
                </Alert>
              )}
            </Box>

            {/* Main Tabbed Content */}
            {backtest && (
              <Card sx={{ background: isDarkMode ? 'rgba(30,41,59,0.85)' : 'rgba(255,255,255,0.95)', backdropFilter: 'blur(20px)' }}>
                <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                  <Tabs 
                    value={mainTab} 
                    onChange={(_, newValue) => setMainTab(newValue)}
                    sx={{
                      '& .MuiTab-root': {
                        textTransform: 'none',
                        fontWeight: 500,
                        minHeight: 64,
                      },
                    }}
                  >
                    <Tab icon={<BarChartIcon />} iconPosition="start" label="Overview" />
                    <Tab icon={<AnalyticsIcon />} iconPosition="start" label="Signals" />
                    <Tab icon={<AccountBalanceWalletIcon />} iconPosition="start" label="Portfolios" />
                  </Tabs>
                </Box>

                {/* Overview Tab */}
                {mainTab === 0 && (
                  <CardContent>
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
                      <Grid item xs={12} sm={6} md={3}>
                        <MetricCard
                          title="Annualized Return"
                          value={metrics?.annualized_return}
                          unit="%"
                          icon={<TrendingUpIcon />}
                          color="success"
                          loading={metricsLoading}
                        />
                      </Grid>
                      <Grid item xs={12} sm={6} md={3}>
                        <MetricCard
                          title="Win Rate"
                          value={metrics?.win_rate}
                          unit="%"
                          icon={<AssessmentIcon />}
                          color="primary"
                          loading={metricsLoading}
                        />
                      </Grid>
                      <Grid item xs={12} sm={6} md={3}>
                        <MetricCard
                          title="Alpha"
                          value={metrics?.alpha}
                          icon={<InsightsIcon />}
                          color="primary"
                          loading={metricsLoading}
                        />
                      </Grid>
                      <Grid item xs={12} sm={6} md={3}>
                        <MetricCard
                          title="Beta"
                          value={metrics?.beta}
                          icon={<TimelineIcon />}
                          color="primary"
                          loading={metricsLoading}
                        />
                      </Grid>
                    </Grid>

                    {/* Performance Chart */}
                    <Box sx={{ mb: 8, pb: 8 }}>
                      <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
                        Performance Overview
                      </Typography>
                      {navLoading ? (
                        <Skeleton variant="rectangular" height={450} sx={{ borderRadius: 1 }} /> // Minimal border radius
                      ) : (
                        <Box sx={{ pb: 6 }}>
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
                  </CardContent>
                )}

                {/* Signals Tab */}
                {mainTab === 1 && (
                  <CardContent>
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                      Signals Used in This Backtest
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                      The following signals were used to create this backtest:
                    </Typography>
                    {usedSignalsLoading ? (
                      <Box>
                        {[...Array(3)].map((_, index) => (
                          <Skeleton key={index} variant="rectangular" height={100} sx={{ borderRadius: 1, mb: 2 }} /> // Minimal border radius
                        ))}
                      </Box>
                    ) : uniqueSignals.length > 0 ? (
                      <Box>
                        {uniqueSignals.map((signal) => {
                          const isExpanded = expandedSignals.has(signal.name);
                          const description = signal.description || 'No description provided';
                          const needsExpansion = description.length > 150;
                          
                          return (
                            <Card
                              key={signal.name}
                              variant="outlined"
                              sx={{
                                mb: 2,
                                background: isDarkMode ? 'rgba(30,41,59,0.85)' : 'rgba(255,255,255,0.95)',
                                backdropFilter: 'blur(20px)',
                                borderColor: isDarkMode ? 'rgba(148,163,184,0.25)' : 'rgba(148,163,184,0.30)',
                                '&:hover': {
                                  boxShadow: isDarkMode
                                    ? '0 8px 24px rgba(0,0,0,0.35)'
                                    : '0 8px 24px rgba(0,0,0,0.15)',
                                  borderColor: isDarkMode ? 'rgba(148,163,184,0.40)' : 'rgba(148,163,184,0.50)',
                                },
                                transition: 'all 0.2s ease-in-out',
                              }}
                            >
                              <CardContent sx={{ p: 2.5, '&:last-child': { pb: 2.5 } }}>
                                <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', mb: 1 }}>
                                  <Box sx={{ flex: 1 }}>
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
                                      <Chip 
                                        label={signal.name} 
                                        size="small" 
                                        variant="outlined" 
                                        sx={{ 
                                          fontWeight: 600, 
                                          height: 24,
                                          backgroundColor: isDarkMode ? 'rgba(96,165,250,0.15)' : 'rgba(147,197,253,0.35)',
                                          borderColor: isDarkMode ? '#60a5fa' : '#60a5fa',
                                          color: isDarkMode ? '#bfdbfe' : '#1e40af',
                                        }} 
                                      />
                                    </Box>
                                    <Typography
                                      variant="body2"
                                      color="text.secondary"
                                      sx={{
                                        lineHeight: 1.6,
                                        whiteSpace: isExpanded ? 'normal' : 'pre-wrap',
                                        ...(needsExpansion && !isExpanded && {
                                          display: '-webkit-box',
                                          WebkitLineClamp: 3,
                                          WebkitBoxOrient: 'vertical',
                                          overflow: 'hidden',
                                          textOverflow: 'ellipsis',
                                        }),
                                      }}
                                    >
                                      {description}
                                    </Typography>
                                  </Box>
                                  {needsExpansion && (
                                    <IconButton
                                      size="small"
                                      onClick={() => toggleSignalExpansion(signal.name)}
                                      sx={{
                                        ml: 1.5,
                                        color: isDarkMode ? '#94a3b8' : '#64748b',
                                        '&:hover': {
                                          backgroundColor: isDarkMode ? 'rgba(148,163,184,0.1)' : 'rgba(148,163,184,0.08)',
                                        },
                                      }}
                                    >
                                      {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                                    </IconButton>
                                  )}
                                </Box>
                              </CardContent>
                            </Card>
                          );
                        })}
                      </Box>
                    ) : (
                      <Alert severity="info" sx={{ mt: 1 }}>
                        No signals found for this backtest.
                      </Alert>
                    )}
                  </CardContent>
                )}

                {/* Portfolios Tab */}
                {mainTab === 2 && (
                  <CardContent>
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                      Portfolio Rebalancing History
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                      {portfoliosData?.total || 0} portfolio rebalances. Click to expand and view signal scores and combined scores.
                    </Typography>

                    {portfoliosLoading ? (
                      <Box>
                        {[...Array(5)].map((_, index) => (
                          <Skeleton key={index} variant="rectangular" height={80} sx={{ borderRadius: 1, mb: 2 }} /> // Minimal border radius
                        ))}
                      </Box>
                    ) : portfoliosData && portfoliosData.portfolios.length > 0 ? (
                      <Box>
                        {portfoliosData.portfolios.map((portfolio) => {
                          const isExpanded = expandedPortfolios.has(portfolio.id);
                          const scoreData = portfolioScoreData.get(portfolio.id);
                          const universeTickers = scoreData?.universeTickers || [];
                          const signalData = scoreData?.signals || [];
                          const combinedScores = scoreData?.scores || [];
                          const positions = scoreData?.positions || [];
                          
                          // Create a map of ticker to weight for quick lookup
                          const tickerToWeight = new Map<string, number>();
                          positions.forEach((pos: any) => {
                            tickerToWeight.set(pos.ticker, pos.weight);
                          });
                          
                          // Get available signals from signal data
                          const availableSignals = signalData.length > 0 && signalData[0]?.available_signals
                            ? [...new Set(signalData[0].available_signals as string[])].sort()
                            : [];

                          return (
                            <Accordion
                              key={portfolio.id}
                              expanded={isExpanded}
                              onChange={() => togglePortfolioExpansion(portfolio.id)}
                              sx={{
                                mb: 2,
                                background: isDarkMode ? 'rgba(30,41,59,0.85)' : 'rgba(255,255,255,0.95)',
                                backdropFilter: 'blur(20px)',
                                '&:before': { display: 'none' },
                                border: `1px solid ${isDarkMode ? 'rgba(148,163,184,0.25)' : 'rgba(148,163,184,0.30)'}`,
                                boxShadow: isExpanded 
                                  ? (isDarkMode ? '0 8px 24px rgba(0,0,0,0.35)' : '0 8px 24px rgba(0,0,0,0.15)')
                                  : 'none',
                              }}
                            >
                              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%', pr: 2 }}>
                                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flex: 1 }}>
                                    <Typography variant="body1" sx={{ fontWeight: 600, minWidth: 120 }}>
                                      {portfolio.asof_date}
                                    </Typography>
                                    <Chip 
                                      label={portfolio.method} 
                                      size="small" 
                                      variant="outlined"
                                      sx={{
                                        backgroundColor: isDarkMode ? 'rgba(96,165,250,0.15)' : 'rgba(147,197,253,0.35)',
                                        borderColor: isDarkMode ? '#60a5fa' : '#60a5fa',
                                        color: isDarkMode ? '#bfdbfe' : '#1e40af',
                                      }}
                                    />
                                    <Typography variant="body2" color="text.secondary">
                                      {portfolio.position_count || 0} positions
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                      ${portfolio.total_value?.toFixed(2) || 'N/A'}
                                    </Typography>
                                  </Box>
                                  <IconButton
                                    size="small"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      handlePortfolioClick(portfolio);
                                    }}
                                    sx={{ mr: 1 }}
                                  >
                                    <VisibilityIcon />
                                  </IconButton>
                                </Box>
                              </AccordionSummary>
                              <AccordionDetails>
                                {scoreData ? (
                                  <Box>
                                    {/* Signal Scores Table */}
                                    {availableSignals.length > 0 && (
                                      <Box sx={{ mb: 3 }}>
                                        <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
                                          Signal Scores & Allocated Weights
                                        </Typography>
                                        <TableContainer component={Paper} variant="outlined" sx={{ maxHeight: 400, overflow: 'auto' }}>
                                          <Table size="small" stickyHeader>
                                            <TableHead>
                                              <TableRow>
                                                <TableCell sx={{ fontWeight: 600, position: 'sticky', left: 0, zIndex: 2, backgroundColor: isDarkMode ? '#1e293b' : '#ffffff' }}>
                                                  Ticker
                                                </TableCell>
                                                <TableCell align="right" sx={{ fontWeight: 600, position: 'sticky', left: 80, zIndex: 2, backgroundColor: isDarkMode ? '#1e293b' : '#ffffff' }}>
                                                  Weight
                                                </TableCell>
                                                {availableSignals.map((signalName) => (
                                                  <TableCell key={signalName} align="right" sx={{ fontWeight: 600 }}>
                                                    {signalName}
                                                  </TableCell>
                                                ))}
                                              </TableRow>
                                            </TableHead>
                                            <TableBody>
                                              {universeTickers.map((ticker) => {
                                                const tickerSignalData = signalData.find((s: any) => s.ticker === ticker);
                                                const weight = tickerToWeight.get(ticker) || 0;
                                                return (
                                                  <TableRow key={ticker} hover>
                                                    <TableCell sx={{ fontWeight: 500, position: 'sticky', left: 0, backgroundColor: isDarkMode ? '#1e293b' : '#ffffff', zIndex: 1 }}>
                                                      {ticker}
                                                    </TableCell>
                                                    <TableCell 
                                                      align="right" 
                                                      sx={{ 
                                                        fontWeight: 500, 
                                                        position: 'sticky', 
                                                        left: 80, 
                                                        backgroundColor: isDarkMode ? '#1e293b' : '#ffffff', 
                                                        zIndex: 1,
                                                        color: weight > 0 ? (isDarkMode ? '#10b981' : '#059669') : 'text.secondary'
                                                      }}
                                                    >
                                                      {weight > 0 ? `${(weight * 100).toFixed(2)}%` : '0.00%'}
                                                    </TableCell>
                                                    {availableSignals.map((signalName) => (
                                                      <TableCell key={signalName} align="right">
                                                        {tickerSignalData && (tickerSignalData as any)[signalName] !== null && (tickerSignalData as any)[signalName] !== undefined
                                                          ? Number((tickerSignalData as any)[signalName]).toFixed(4)
                                                          : '—'
                                                        }
                                                      </TableCell>
                                                    ))}
                                                  </TableRow>
                                                );
                                              })}
                                            </TableBody>
                                          </Table>
                                        </TableContainer>
                                      </Box>
                                    )}

                                    {/* Combined Scores Table */}
                                    <Box>
                                      <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
                                        Combined Scores & Allocated Weights
                                      </Typography>
                                      <TableContainer component={Paper} variant="outlined" sx={{ maxHeight: 400, overflow: 'auto' }}>
                                        <Table size="small" stickyHeader>
                                          <TableHead>
                                            <TableRow>
                                              <TableCell sx={{ fontWeight: 600 }}>Ticker</TableCell>
                                              <TableCell align="right" sx={{ fontWeight: 600 }}>Weight</TableCell>
                                              <TableCell align="right" sx={{ fontWeight: 600 }}>Combined Score</TableCell>
                                              <TableCell align="right" sx={{ fontWeight: 600 }}>Method</TableCell>
                                            </TableRow>
                                          </TableHead>
                                          <TableBody>
                                            {universeTickers.map((ticker) => {
                                              const tickerScoreData = combinedScores.find((s: any) => s.ticker === ticker);
                                              const weight = tickerToWeight.get(ticker) || 0;
                                              return (
                                                <TableRow key={ticker} hover>
                                                  <TableCell sx={{ fontWeight: 500 }}>{ticker}</TableCell>
                                                  <TableCell 
                                                    align="right"
                                                    sx={{
                                                      fontWeight: 500,
                                                      color: weight > 0 ? (isDarkMode ? '#10b981' : '#059669') : 'text.secondary'
                                                    }}
                                                  >
                                                    {weight > 0 ? `${(weight * 100).toFixed(2)}%` : '0.00%'}
                                                  </TableCell>
                                                  <TableCell align="right">
                                                    {tickerScoreData && tickerScoreData.combined_score !== null && tickerScoreData.combined_score !== undefined
                                                      ? Number(tickerScoreData.combined_score).toFixed(4)
                                                      : '—'
                                                    }
                                                  </TableCell>
                                                  <TableCell align="right">
                                                    <Chip 
                                                      label={tickerScoreData?.method || '—'} 
                                                      size="small" 
                                                      variant="outlined"
                                                    />
                                                  </TableCell>
                                                </TableRow>
                                              );
                                            })}
                                          </TableBody>
                                        </Table>
                                      </TableContainer>
                                    </Box>
                                  </Box>
                                ) : (
                                  <Box sx={{ textAlign: 'center', py: 2 }}>
                                    <Skeleton variant="rectangular" height={200} />
                                  </Box>
                                )}
                              </AccordionDetails>
                            </Accordion>
                          );
                        })}
                      </Box>
                    ) : (
                      <Alert severity="info">No portfolios found for this backtest.</Alert>
                    )}
                  </CardContent>
                )}
              </Card>
            )}

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
