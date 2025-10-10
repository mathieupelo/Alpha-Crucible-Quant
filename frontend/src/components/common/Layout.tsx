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
} from '@mui/material';
import {
  Home as HomeIcon,
  Dashboard as DashboardIcon,
  Group as GroupIcon,
  PlayArrow as PlayArrowIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import Logo from './Logo';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const navigationItems = [
    { path: '/', label: 'Home', icon: <HomeIcon /> },
    { path: '/dashboard', label: 'Dashboard', icon: <DashboardIcon /> },
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
          backgroundColor: 'background.paper',
          borderBottom: '1px solid',
          borderColor: 'divider',
        }}
      >
        <Toolbar>
          <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
            <Logo size="medium" showText={true} />
            <Typography
              variant="body2"
              sx={{ 
                ml: 3,
                color: 'text.secondary',
                fontSize: '0.875rem',
              }}
            >
              Quantitative Trading Dashboard
            </Typography>
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {navigationItems.map((item) => (
              <Tooltip key={item.path} title={item.label}>
                <Button
                  color="inherit"
                  startIcon={item.icon}
                  onClick={() => navigate(item.path)}
                  sx={{
                    color: isActive(item.path) ? 'primary.main' : 'text.secondary',
                    fontWeight: isActive(item.path) ? 600 : 400,
                    '&:hover': {
                      backgroundColor: 'action.hover',
                    },
                  }}
                >
                  {item.label}
                </Button>
              </Tooltip>
            ))}
            <Tooltip title="Settings">
              <IconButton color="inherit" size="small">
                <SettingsIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Box component="main" sx={{ flexGrow: 1, py: 3 }}>
        <Container maxWidth="xl">
          {children}
        </Container>
      </Box>

      {/* Footer */}
      <Box
        component="footer"
        sx={{
          py: 3,
          px: 2,
          mt: 'auto',
          backgroundColor: 'background.paper',
          borderTop: '1px solid',
          borderColor: 'divider',
        }}
      >
        <Container maxWidth="xl">
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
            <Logo size="small" showText={true} variant="minimal" clickable={true} />
            <Typography
              variant="body2"
              color="text.secondary"
              align="center"
              sx={{ fontSize: '0.875rem' }}
            >
              © 2025 Alpha Crucible Quant. Built with React, FastAPI, and Material-UI.
            </Typography>
          </Box>
        </Container>
      </Box>
    </Box>
  );
};

export default Layout;

