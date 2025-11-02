/**
 * Main App Component for Alpha Crucible Quant Dashboard
 */

import React, { useMemo } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box } from '@mui/material';

import Home from '@/pages/Home';
import BacktestManager from '@/pages/BacktestManager';
import UniverseManager from '@/pages/UniverseManager';
import UniverseDetail from '@/pages/UniverseDetail';
import RunBacktest from '@/pages/RunBacktest';
import NewsDeepDive from '@/pages/NewsDeepDive';
import Layout from '@/components/common/Layout';
import { ThemeProvider as CustomThemeProvider, useTheme } from '@/contexts/ThemeContext';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

// Create sophisticated Material-UI theme with modern gradients
const createAppTheme = (isDarkMode: boolean) => createTheme({
  palette: {
    mode: isDarkMode ? 'dark' : 'light',
  primary: {
    main: isDarkMode ? '#2563eb' : '#1d4ed8',
    light: isDarkMode ? '#3b82f6' : '#2563eb',
    dark: isDarkMode ? '#1d4ed8' : '#1e40af',
    contrastText: '#ffffff',
  },
  secondary: {
    main: isDarkMode ? '#2563eb' : '#1d4ed8',
    light: isDarkMode ? '#3b82f6' : '#2563eb',
    dark: isDarkMode ? '#1d4ed8' : '#1e40af',
    contrastText: '#ffffff',
  },
    error: {
      main: isDarkMode ? '#ef4444' : '#dc2626',
      light: isDarkMode ? '#f87171' : '#ef4444',
      dark: isDarkMode ? '#dc2626' : '#b91c1c',
    },
    warning: {
      main: isDarkMode ? '#f59e0b' : '#d97706',
      light: isDarkMode ? '#fbbf24' : '#f59e0b',
      dark: isDarkMode ? '#d97706' : '#b45309',
    },
    info: {
      main: isDarkMode ? '#06b6d4' : '#0891b2',
      light: isDarkMode ? '#22d3ee' : '#06b6d4',
      dark: isDarkMode ? '#0891b2' : '#0e7490',
    },
    success: {
      main: isDarkMode ? '#10b981' : '#059669',
      light: isDarkMode ? '#34d399' : '#10b981',
      dark: isDarkMode ? '#059669' : '#047857',
    },
    background: {
      default: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)',
      paper: isDarkMode 
        ? 'linear-gradient(145deg, #1e293b 0%, #334155 100%)'
        : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
    },
    text: {
      primary: isDarkMode ? '#f8fafc' : '#0f172a',
      secondary: isDarkMode ? '#cbd5e1' : '#475569',
    },
    divider: isDarkMode ? 'rgba(148, 163, 184, 0.1)' : 'rgba(148, 163, 184, 0.2)',
  },
  typography: {
    fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    h1: {
      fontWeight: 800,
      fontSize: '3rem',
      lineHeight: 1.1,
      letterSpacing: '-0.02em',
    },
    h2: {
      fontWeight: 700,
      fontSize: '2.25rem',
      lineHeight: 1.2,
      letterSpacing: '-0.01em',
    },
    h3: {
      fontWeight: 600,
      fontSize: '1.875rem',
      lineHeight: 1.3,
    },
    h4: {
      fontWeight: 600,
      fontSize: '1.5rem',
      lineHeight: 1.4,
    },
    h5: {
      fontWeight: 600,
      fontSize: '1.25rem',
      lineHeight: 1.4,
    },
    h6: {
      fontWeight: 600,
      fontSize: '1.125rem',
      lineHeight: 1.4,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.6,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
    },
    button: {
      fontWeight: 600,
      textTransform: 'none',
    },
  },
  shape: {
    borderRadius: 1, // Minimal border radius - barely visible except for buttons and icons
  },
  shadows: [
    'none',
    isDarkMode 
      ? '0 1px 3px 0 rgba(0, 0, 0, 0.3), 0 1px 2px 0 rgba(0, 0, 0, 0.2)'
      : '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    isDarkMode 
      ? '0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2)'
      : '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    isDarkMode 
      ? '0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.2)'
      : '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    isDarkMode 
      ? '0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2)'
      : '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    isDarkMode 
      ? '0 25px 50px -12px rgba(0, 0, 0, 0.4)'
      : '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    isDarkMode 
      ? '0 25px 50px -12px rgba(0, 0, 0, 0.4)'
      : '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    isDarkMode 
      ? '0 25px 50px -12px rgba(0, 0, 0, 0.4)'
      : '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    isDarkMode 
      ? '0 25px 50px -12px rgba(0, 0, 0, 0.4)'
      : '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    isDarkMode 
      ? '0 25px 50px -12px rgba(0, 0, 0, 0.4)'
      : '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    isDarkMode 
      ? '0 25px 50px -12px rgba(0, 0, 0, 0.4)'
      : '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    isDarkMode 
      ? '0 25px 50px -12px rgba(0, 0, 0, 0.4)'
      : '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    isDarkMode 
      ? '0 25px 50px -12px rgba(0, 0, 0, 0.4)'
      : '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    isDarkMode 
      ? '0 25px 50px -12px rgba(0, 0, 0, 0.4)'
      : '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    isDarkMode 
      ? '0 25px 50px -12px rgba(0, 0, 0, 0.4)'
      : '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    isDarkMode 
      ? '0 25px 50px -12px rgba(0, 0, 0, 0.4)'
      : '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    isDarkMode 
      ? '0 25px 50px -12px rgba(0, 0, 0, 0.4)'
      : '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    isDarkMode 
      ? '0 25px 50px -12px rgba(0, 0, 0, 0.4)'
      : '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    isDarkMode 
      ? '0 25px 50px -12px rgba(0, 0, 0, 0.4)'
      : '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    isDarkMode 
      ? '0 25px 50px -12px rgba(0, 0, 0, 0.4)'
      : '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    isDarkMode 
      ? '0 25px 50px -12px rgba(0, 0, 0, 0.4)'
      : '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    isDarkMode 
      ? '0 25px 50px -12px rgba(0, 0, 0, 0.4)'
      : '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    isDarkMode 
      ? '0 25px 50px -12px rgba(0, 0, 0, 0.4)'
      : '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    isDarkMode 
      ? '0 25px 50px -12px rgba(0, 0, 0, 0.4)'
      : '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    isDarkMode 
      ? '0 25px 50px -12px rgba(0, 0, 0, 0.4)'
      : '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    isDarkMode 
      ? '0 25px 50px -12px rgba(0, 0, 0, 0.4)'
      : '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    isDarkMode 
      ? '0 25px 50px -12px rgba(0, 0, 0, 0.4)'
      : '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
  ] as any,
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)',
          backgroundAttachment: 'fixed',
          minHeight: '100vh',
        },
        '*': {
          '&::-webkit-scrollbar': {
            width: '8px',
            height: '8px',
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
          // Firefox scrollbar styling
          scrollbarWidth: 'thin',
          scrollbarColor: isDarkMode 
            ? '#64748b #1e293b' 
            : '#94a3b8 #f1f5f9',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          background: isDarkMode 
            ? 'linear-gradient(145deg, #1e293b 0%, #334155 100%)'
            : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
          backdropFilter: 'none',
          border: isDarkMode 
            ? '1px solid rgba(148, 163, 184, 0.3)'
            : '1px solid rgba(148, 163, 184, 0.4)',
          boxShadow: isDarkMode 
            ? '0 8px 32px 0 rgba(0, 0, 0, 0.5), 0 4px 16px 0 rgba(0, 0, 0, 0.4)'
            : '0 8px 32px 0 rgba(0, 0, 0, 0.2), 0 4px 16px 0 rgba(0, 0, 0, 0.15)',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: isDarkMode 
              ? '0 12px 40px 0 rgba(0, 0, 0, 0.6), 0 8px 24px 0 rgba(0, 0, 0, 0.5)'
              : '0 12px 40px 0 rgba(0, 0, 0, 0.25), 0 8px 24px 0 rgba(0, 0, 0, 0.2)',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
          borderRadius: 8, // Keep rounded for clickable buttons
          padding: '10px 24px',
          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            transform: 'translateY(-1px)',
          },
        },
        contained: {
          background: isDarkMode
            ? 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)'
            : 'linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%)',
          boxShadow: isDarkMode
            ? '0 4px 14px 0 rgba(37, 99, 235, 0.4)'
            : '0 4px 14px 0 rgba(29, 78, 216, 0.3)',
          '&:hover': {
            background: isDarkMode
              ? 'linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%)'
              : 'linear-gradient(135deg, #1e40af 0%, #1d4ed8 100%)',
            boxShadow: isDarkMode
              ? '0 6px 20px 0 rgba(37, 99, 235, 0.5)'
              : '0 6px 20px 0 rgba(29, 78, 216, 0.4)',
          },
        },
        outlined: {
          borderColor: isDarkMode ? 'rgba(148, 163, 184, 0.3)' : 'rgba(148, 163, 184, 0.4)',
          '&:hover': {
            borderColor: isDarkMode ? 'rgba(148, 163, 184, 0.5)' : 'rgba(148, 163, 184, 0.6)',
            backgroundColor: isDarkMode ? 'rgba(148, 163, 184, 0.05)' : 'rgba(148, 163, 184, 0.05)',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 1, // Minimal border radius for input fields
            backgroundColor: isDarkMode 
              ? 'rgba(30, 41, 59, 0.5)'
              : 'rgba(255, 255, 255, 0.8)',
            backdropFilter: 'blur(10px)',
            transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
            '&:hover': {
              backgroundColor: isDarkMode 
                ? 'rgba(30, 41, 59, 0.7)'
                : 'rgba(255, 255, 255, 0.9)',
            },
            '&.Mui-focused': {
              backgroundColor: isDarkMode 
                ? 'rgba(30, 41, 59, 0.8)'
                : 'rgba(255, 255, 255, 1)',
            },
          },
        },
      },
    },
    MuiSelect: {
      styleOverrides: {
        root: {
          borderRadius: 1, // Minimal border radius for select fields
          backgroundColor: isDarkMode 
            ? 'rgba(30, 41, 59, 0.5)'
            : 'rgba(255, 255, 255, 0.8)',
          backdropFilter: 'blur(10px)',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 1, // Minimal border radius for chips
          fontWeight: 500,
        },
      },
    },
  },
});

const App: React.FC = () => {
  const { isDarkMode } = useTheme();
  const theme = useMemo(() => createAppTheme(isDarkMode), [isDarkMode]);

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Box sx={{ minHeight: '100vh' }}>
            <Layout>
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/backtest" element={<BacktestManager />} />
                <Route path="/run-backtest" element={<RunBacktest />} />
                <Route path="/universes" element={<UniverseManager />} />
                <Route path="/universes/:id" element={<UniverseDetail />} />
                <Route path="/news-deep-dive" element={<NewsDeepDive />} />
              </Routes>
            </Layout>
          </Box>
        </Router>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

const AppWithTheme: React.FC = () => {
  return (
    <CustomThemeProvider>
      <App />
    </CustomThemeProvider>
  );
};

export default AppWithTheme;

