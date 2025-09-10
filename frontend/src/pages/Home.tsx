/**
 * Home Page
 * Landing page with navigation to different sections of the application
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActionArea,
  Container,
  Chip,
} from '@mui/material';
import {
  Analytics as AnalyticsIcon,
  Group as GroupIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';

const Home: React.FC = () => {
  const navigate = useNavigate();

  const navigationCards = [
    {
      title: 'Dashboard',
      description: 'View and analyze your quantitative trading strategies',
      icon: <AnalyticsIcon sx={{ fontSize: 48, color: 'primary.main' }} />,
      path: '/dashboard',
      color: 'primary' as const,
      features: ['Performance Metrics', 'Portfolio Analysis', 'Risk Assessment']
    },
    {
      title: 'Universe Manager',
      description: 'Manage universes and their ticker compositions',
      icon: <GroupIcon sx={{ fontSize: 48, color: 'secondary.main' }} />,
      path: '/universes',
      color: 'secondary' as const,
      features: ['Create Universes', 'Ticker Management', 'Validation Tools']
    },
    {
      title: 'Backtest Explorer',
      description: 'Explore detailed backtest results and performance',
      icon: <TrendingUpIcon sx={{ fontSize: 48, color: 'success.main' }} />,
      path: '/backtest',
      color: 'success' as const,
      features: ['Historical Analysis', 'Signal Evaluation', 'Portfolio Optimization']
    },
    {
      title: 'Strategy Analysis',
      description: 'Deep dive into strategy performance and signals',
      icon: <AssessmentIcon sx={{ fontSize: 48, color: 'warning.main' }} />,
      path: '/analysis',
      color: 'warning' as const,
      features: ['Signal Analysis', 'Risk Metrics', 'Performance Attribution']
    }
  ];

  const handleCardClick = (path: string) => {
    navigate(path);
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ py: 4 }}>
        {/* Header */}
        <Box sx={{ textAlign: 'center', mb: 6 }}>
          <Typography variant="h2" component="h1" gutterBottom sx={{ fontWeight: 700, mb: 2 }}>
            Alpha Crucible Quant
          </Typography>
          <Typography variant="h5" color="text.secondary" sx={{ maxWidth: 600, mx: 'auto' }}>
            Advanced quantitative trading platform for strategy development, backtesting, and portfolio management
          </Typography>
        </Box>

        {/* Navigation Cards */}
        <Grid container spacing={4}>
          {navigationCards.map((card, index) => (
            <Grid item xs={12} sm={6} lg={3} key={index}>
              <Card
                sx={{
                  height: '100%',
                  transition: 'all 0.3s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-8px)',
                    boxShadow: 8,
                  },
                }}
              >
                <CardActionArea
                  onClick={() => handleCardClick(card.path)}
                  sx={{ height: '100%', p: 0 }}
                >
                  <CardContent sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
                    {/* Icon */}
                    <Box sx={{ textAlign: 'center', mb: 3 }}>
                      {card.icon}
                    </Box>

                    {/* Title */}
                    <Typography variant="h5" component="h2" gutterBottom sx={{ fontWeight: 600, textAlign: 'center' }}>
                      {card.title}
                    </Typography>

                    {/* Description */}
                    <Typography variant="body1" color="text.secondary" sx={{ mb: 3, textAlign: 'center', flexGrow: 1 }}>
                      {card.description}
                    </Typography>

                    {/* Features */}
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, justifyContent: 'center' }}>
                      {card.features.map((feature, featureIndex) => (
                        <Chip
                          key={featureIndex}
                          label={feature}
                          size="small"
                          color={card.color}
                          variant="outlined"
                          sx={{ fontSize: '0.75rem' }}
                        />
                      ))}
                    </Box>
                  </CardContent>
                </CardActionArea>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* Quick Stats or Additional Info */}
        <Box sx={{ mt: 8, textAlign: 'center' }}>
          <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
            Platform Features
          </Typography>
          <Grid container spacing={4} sx={{ mt: 2 }}>
            <Grid item xs={12} md={4}>
              <Box>
                <Typography variant="h6" gutterBottom color="primary.main">
                  Real-time Data
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Access to live market data and historical information for comprehensive analysis
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box>
                <Typography variant="h6" gutterBottom color="secondary.main">
                  Advanced Analytics
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Sophisticated quantitative models and risk management tools
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box>
                <Typography variant="h6" gutterBottom color="success.main">
                  Portfolio Optimization
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  State-of-the-art optimization algorithms for portfolio construction
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Box>
      </Box>
    </Container>
  );
};

export default Home;
