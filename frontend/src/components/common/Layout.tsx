/**
 * Main Layout Component
 * Provides the overall layout structure for the application
 */

import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  Container,
  IconButton,
  Tooltip,
  Button,
  Fade,
} from '@mui/material';
import {
  Home as HomeIcon,
  Dashboard as DashboardIcon,
  Group as GroupIcon,
  PlayArrow as PlayArrowIcon,
  DarkMode as DarkModeIcon,
  LightMode as LightModeIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import Logo from './Logo';
import { useTheme } from '@/contexts/ThemeContext';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isDarkMode, toggleTheme } = useTheme();

  const navigationItems = [
    { path: '/', label: 'Home', icon: <HomeIcon /> },
    { path: '/backtest', label: 'Backtest Manager', icon: <DashboardIcon /> },
    { path: '/run-backtest', label: 'Run Backtest', icon: <PlayArrowIcon /> },
    { path: '/universes', label: 'Universes', icon: <GroupIcon /> },
  ];

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* Header */}
      <AppBar 
        position="static" 
        elevation={0}
        sx={{ 
          background: isDarkMode 
            ? 'rgba(30, 41, 59, 0.85)'
            : 'rgba(255, 255, 255, 0.85)',
          backdropFilter: 'blur(30px)',
          borderBottom: '1px solid',
          borderColor: isDarkMode ? 'rgba(148, 163, 184, 0.2)' : 'rgba(148, 163, 184, 0.3)',
          boxShadow: isDarkMode
            ? '0 4px 20px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(255, 255, 255, 0.05) inset'
            : '0 4px 20px rgba(0, 0, 0, 0.1), 0 0 0 1px rgba(0, 0, 0, 0.05) inset',
        }}
      >
        <Toolbar sx={{ py: 1.5, px: { xs: 2, sm: 3, md: 4 } }}>
          <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1, gap: 3 }}>
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Logo size="medium" showText={true} />
            </motion.div>
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              <Typography
                variant="body2"
                sx={{ 
                  color: 'text.secondary',
                  fontSize: '0.875rem',
                  fontWeight: 500,
                  display: { xs: 'none', md: 'block' },
                  background: isDarkMode
                    ? 'linear-gradient(135deg, #cbd5e1 0%, #94a3b8 100%)'
                    : 'linear-gradient(135deg, #475569 0%, #64748b 100%)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
              >
                Quantitative Trading Dashboard
              </Typography>
            </motion.div>
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            {navigationItems.map((item, index) => (
              <motion.div
                key={item.path}
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
              >
                <Tooltip title={item.label} arrow placement="bottom">
                  <Button
                    color="inherit"
                    startIcon={item.icon}
                    onClick={() => navigate(item.path)}
                    sx={{
                      color: isActive(item.path) ? 'primary.main' : 'text.secondary',
                      fontWeight: isActive(item.path) ? 600 : 500,
                      borderRadius: 2.5,
                      px: 2.5,
                      py: 1,
                      minHeight: 40,
                      position: 'relative',
                      overflow: 'hidden',
                      fontSize: '0.875rem',
                      textTransform: 'none',
                      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                      ...(isActive(item.path) && {
                        background: isDarkMode
                          ? 'linear-gradient(135deg, rgba(37, 99, 235, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%)'
                          : 'linear-gradient(135deg, rgba(37, 99, 235, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%)',
                        border: '1px solid',
                        borderColor: isDarkMode
                          ? 'rgba(37, 99, 235, 0.3)'
                          : 'rgba(37, 99, 235, 0.4)',
                        '&::before': {
                          content: '""',
                          position: 'absolute',
                          top: 0,
                          left: '-100%',
                          width: '100%',
                          height: '100%',
                          background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent)',
                          transition: 'left 0.5s',
                        },
                      }),
                      '&:hover': {
                        backgroundColor: isActive(item.path)
                          ? (isDarkMode
                              ? 'rgba(37, 99, 235, 0.25)'
                              : 'rgba(37, 99, 235, 0.15)')
                          : isDarkMode 
                            ? 'rgba(148, 163, 184, 0.15)' 
                            : 'rgba(148, 163, 184, 0.08)',
                        color: isActive(item.path) ? 'primary.main' : 'primary.main',
                        transform: 'translateY(-2px)',
                        boxShadow: isActive(item.path)
                          ? '0 8px 20px rgba(37, 99, 235, 0.3)'
                          : '0 4px 12px rgba(0, 0, 0, 0.1)',
                        '&::before': {
                          left: '100%',
                        },
                      },
                    }}
                  >
                    <Box sx={{ display: { xs: 'none', md: 'block' } }}>{item.label}</Box>
                    <Box sx={{ display: { xs: 'block', md: 'none' } }}>{item.icon}</Box>
                  </Button>
                </Tooltip>
              </motion.div>
            ))}
            
            {/* Theme Toggle */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3, delay: 0.4 }}
            >
              <Tooltip title={`Switch to ${isDarkMode ? 'light' : 'dark'} mode`} arrow placement="bottom">
                <IconButton
                  onClick={toggleTheme}
                  sx={{
                    color: 'text.secondary',
                    borderRadius: 2,
                    width: 40,
                    height: 40,
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    '&:hover': {
                      color: 'primary.main',
                      backgroundColor: isDarkMode 
                        ? 'rgba(148, 163, 184, 0.15)' 
                        : 'rgba(148, 163, 184, 0.08)',
                      transform: 'rotate(180deg) scale(1.1)',
                      boxShadow: '0 4px 12px rgba(37, 99, 235, 0.2)',
                    },
                  }}
                >
                  <Fade in={true} timeout={300}>
                    {isDarkMode ? <LightModeIcon /> : <DarkModeIcon />}
                  </Fade>
                </IconButton>
              </Tooltip>
            </motion.div>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <Box component="main" sx={{ flexGrow: 1, py: 4 }}>
          <Container maxWidth="xl">
            {children}
          </Container>
        </Box>
      </motion.div>

      {/* Footer */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.6 }}
      >
        <Box
          component="footer"
          sx={{
            py: 4,
            px: 2,
            mt: 'auto',
            background: isDarkMode 
              ? 'rgba(30, 41, 59, 0.85)'
              : 'rgba(255, 255, 255, 0.85)',
            backdropFilter: 'blur(30px)',
            borderTop: '1px solid',
            borderColor: isDarkMode ? 'rgba(148, 163, 184, 0.2)' : 'rgba(148, 163, 184, 0.3)',
            boxShadow: isDarkMode
              ? '0 -4px 20px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(255, 255, 255, 0.05) inset'
              : '0 -4px 20px rgba(0, 0, 0, 0.1), 0 0 0 1px rgba(0, 0, 0, 0.05) inset',
            position: 'relative',
          }}
        >
          <Container maxWidth="xl">
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2.5 }}>
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Logo size="small" showText={true} variant="minimal" clickable={true} />
              </motion.div>
              <Typography
                variant="body2"
                color="text.secondary"
                align="center"
                sx={{ 
                  fontSize: '0.875rem', 
                  fontWeight: 500,
                  background: isDarkMode
                    ? 'linear-gradient(135deg, #cbd5e1 0%, #94a3b8 100%)'
                    : 'linear-gradient(135deg, #475569 0%, #64748b 100%)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
              >
                © 2025 Alpha Crucible Quant. Built with React, FastAPI, and Material-UI.
              </Typography>
            </Box>
          </Container>
        </Box>
      </motion.div>
    </Box>
  );
};

export default Layout;

