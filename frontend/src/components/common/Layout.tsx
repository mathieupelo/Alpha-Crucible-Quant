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
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Analytics as AnalyticsIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
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
            <AnalyticsIcon sx={{ mr: 2, color: 'primary.main' }} />
            <Typography
              variant="h6"
              component="div"
              sx={{ 
                fontWeight: 700,
                color: 'text.primary',
                letterSpacing: '-0.025em',
              }}
            >
              Alpha Crucible Quant
            </Typography>
            <Typography
              variant="body2"
              sx={{ 
                ml: 2,
                color: 'text.secondary',
                fontSize: '0.875rem',
              }}
            >
              Quantitative Trading Dashboard
            </Typography>
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Tooltip title="Dashboard">
              <IconButton color="inherit" size="small">
                <DashboardIcon />
              </IconButton>
            </Tooltip>
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
          py: 2,
          px: 2,
          mt: 'auto',
          backgroundColor: 'background.paper',
          borderTop: '1px solid',
          borderColor: 'divider',
        }}
      >
        <Container maxWidth="xl">
          <Typography
            variant="body2"
            color="text.secondary"
            align="center"
            sx={{ fontSize: '0.875rem' }}
          >
            © 2025 Alpha Crucible Quant. Built with React, FastAPI, and Material-UI.
          </Typography>
        </Container>
      </Box>
    </Box>
  );
};

export default Layout;

