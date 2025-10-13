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
  Speed as SpeedIcon,
  Timeline as TimelineIcon,
  ShowChart as ShowChartIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import Logo from '@/components/common/Logo';
import { useTheme } from '@/contexts/ThemeContext';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const { isDarkMode } = useTheme();

  const navigationCards = [
    {
      title: 'Backtest Manager',
      description: 'View and analyze your quantitative trading strategies',
      icon: <AnalyticsIcon sx={{ fontSize: 48 }} />,
      path: '/backtest',
      color: 'primary' as const,
      features: ['Performance Metrics', 'Portfolio Analysis', 'Risk Assessment'],
      gradient: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)'
    },
    {
      title: 'Universe Manager',
      description: 'Manage universes and their ticker compositions',
      icon: <GroupIcon sx={{ fontSize: 48 }} />,
      path: '/universes',
      color: 'secondary' as const,
      features: ['Create Universes', 'Ticker Management', 'Validation Tools'],
      gradient: isDarkMode 
        ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
        : 'linear-gradient(135deg, #059669 0%, #047857 100%)'
    },
    {
      title: 'Run Backtest',
      description: 'Configure and execute new quantitative trading strategies',
      icon: <TrendingUpIcon sx={{ fontSize: 48 }} />,
      path: '/run-backtest',
      color: 'success' as const,
      features: ['Strategy Configuration', 'Preflight Validation', 'Real-time Execution'],
      gradient: 'linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)'
    },
    {
      title: 'Strategy Analysis',
      description: 'Deep dive into strategy performance and signals',
      icon: <AssessmentIcon sx={{ fontSize: 48 }} />,
      path: '/analysis',
      color: 'warning' as const,
      features: ['Signal Analysis', 'Risk Metrics', 'Performance Attribution'],
      gradient: 'linear-gradient(135deg, #ef4444 0%, #f87171 100%)'
    }
  ];

  const handleCardClick = (path: string) => {
    navigate(path);
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ py: 6 }}>
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <Box sx={{ textAlign: 'center', mb: 8 }}>
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <Logo size="xlarge" showText={true} clickable={false} />
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              <Typography 
                variant="h4" 
                sx={{ 
                  maxWidth: 800, 
                  mx: 'auto', 
                  mt: 4,
                  fontWeight: 500,
                  background: isDarkMode 
                    ? 'linear-gradient(135deg, #f8fafc 0%, #cbd5e1 100%)'
                    : 'linear-gradient(135deg, #0f172a 0%, #475569 100%)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
              >
                Advanced quantitative trading platform for strategy development, backtesting, and portfolio management
              </Typography>
            </motion.div>
          </Box>
        </motion.div>

        {/* Navigation Cards */}
        <Grid container spacing={4} sx={{ mb: 8 }}>
          {navigationCards.map((card, index) => (
            <Grid item xs={12} sm={6} lg={3} key={index}>
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.1 * index }}
                whileHover={{ y: -12 }}
              >
                <Card
                  sx={{
                    height: '100%',
                    background: isDarkMode 
                      ? 'linear-gradient(145deg, #1e293b 0%, #334155 100%)'
                      : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
                    backdropFilter: 'none',
                    border: '1px solid',
                    borderColor: isDarkMode 
                      ? 'rgba(148, 163, 184, 0.1)'
                      : 'rgba(148, 163, 184, 0.2)',
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    position: 'relative',
                    overflow: 'hidden',
                    '&::before': {
                      content: '""',
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      height: '4px',
                      background: card.gradient,
                      opacity: 0,
                      transition: 'opacity 0.3s ease',
                    },
                    '&:hover': {
                      boxShadow: isDarkMode 
                        ? '0 20px 40px 0 rgba(0, 0, 0, 0.4), 0 12px 24px 0 rgba(0, 0, 0, 0.3)'
                        : '0 20px 40px 0 rgba(0, 0, 0, 0.15), 0 12px 24px 0 rgba(0, 0, 0, 0.1)',
                      '&::before': {
                        opacity: 1,
                      },
                    },
                  }}
                >
                  <CardActionArea
                    onClick={() => handleCardClick(card.path)}
                    sx={{ height: '100%', p: 0 }}
                  >
                    <CardContent sx={{ p: 4, height: '100%', display: 'flex', flexDirection: 'column' }}>
                      {/* Icon */}
                      <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ duration: 0.4, delay: 0.2 + 0.1 * index }}
                        whileHover={{ scale: 1.1, rotate: 5 }}
                      >
                        <Box 
                          sx={{ 
                            textAlign: 'center', 
                            mb: 3,
                            display: 'flex',
                            justifyContent: 'center',
                            alignItems: 'center',
                            width: 80,
                            height: 80,
                            mx: 'auto',
                            borderRadius: 4,
                            background: card.gradient,
                            color: 'white',
                          }}
                        >
                          {card.icon}
                        </Box>
                      </motion.div>

                      {/* Title */}
                      <Typography 
                        variant="h5" 
                        component="h2" 
                        gutterBottom 
                        sx={{ 
                          fontWeight: 700, 
                          textAlign: 'center',
                          background: card.gradient,
                          backgroundClip: 'text',
                          WebkitBackgroundClip: 'text',
                          WebkitTextFillColor: 'transparent',
                        }}
                      >
                        {card.title}
                      </Typography>

                      {/* Description */}
                      <Typography 
                        variant="body1" 
                        color="text.secondary" 
                        sx={{ 
                          mb: 4, 
                          textAlign: 'center', 
                          flexGrow: 1,
                          fontWeight: 500,
                          lineHeight: 1.6,
                        }}
                      >
                        {card.description}
                      </Typography>

                      {/* Features */}
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, justifyContent: 'center' }}>
                        {card.features.map((feature, featureIndex) => (
                          <motion.div
                            key={featureIndex}
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ duration: 0.3, delay: 0.3 + 0.1 * index + 0.05 * featureIndex }}
                          >
                            <Chip
                              label={feature}
                              size="small"
                              sx={{ 
                                fontSize: '0.75rem',
                                fontWeight: 500,
                                background: card.gradient,
                                color: 'white',
                                '&:hover': {
                                  transform: 'scale(1.05)',
                                },
                              }}
                            />
                          </motion.div>
                        ))}
                      </Box>
                    </CardContent>
                  </CardActionArea>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>

        {/* Platform Features */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          <Box sx={{ textAlign: 'center' }}>
            <Typography 
              variant="h3" 
              gutterBottom 
              sx={{ 
                fontWeight: 800,
                mb: 6,
                background: isDarkMode 
                  ? 'linear-gradient(135deg, #f8fafc 0%, #cbd5e1 100%)'
                  : 'linear-gradient(135deg, #0f172a 0%, #475569 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              Platform Features
            </Typography>
            <Grid container spacing={6}>
              <Grid item xs={12} md={4}>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.8 }}
                  whileHover={{ y: -5 }}
                >
                  <Box sx={{ p: 3 }}>
                    <Box 
                      sx={{ 
                        display: 'flex',
                        justifyContent: 'center',
                        alignItems: 'center',
                        width: 60,
                        height: 60,
                        mx: 'auto',
                        mb: 3,
                        borderRadius: 3,
                        background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                        color: 'white',
                      }}
                    >
                      <SpeedIcon sx={{ fontSize: 32 }} />
                    </Box>
                    <Typography variant="h5" gutterBottom sx={{ fontWeight: 700, mb: 2 }}>
                      Real-time Data
                    </Typography>
                    <Typography variant="body1" color="text.secondary" sx={{ fontWeight: 500 }}>
                      Access to live market data and historical information for comprehensive analysis
                    </Typography>
                  </Box>
                </motion.div>
              </Grid>
              <Grid item xs={12} md={4}>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.9 }}
                  whileHover={{ y: -5 }}
                >
                  <Box sx={{ p: 3 }}>
                    <Box 
                      sx={{ 
                        display: 'flex',
                        justifyContent: 'center',
                        alignItems: 'center',
                        width: 60,
                        height: 60,
                        mx: 'auto',
                        mb: 3,
                        borderRadius: 3,
                        background: 'linear-gradient(135deg, #10b981 0%, #34d399 100%)',
                        color: 'white',
                      }}
                    >
                      <ShowChartIcon sx={{ fontSize: 32 }} />
                    </Box>
                    <Typography variant="h5" gutterBottom sx={{ fontWeight: 700, mb: 2 }}>
                      Advanced Analytics
                    </Typography>
                    <Typography variant="body1" color="text.secondary" sx={{ fontWeight: 500 }}>
                      Sophisticated quantitative models and risk management tools
                    </Typography>
                  </Box>
                </motion.div>
              </Grid>
              <Grid item xs={12} md={4}>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 1.0 }}
                  whileHover={{ y: -5 }}
                >
                  <Box sx={{ p: 3 }}>
                    <Box 
                      sx={{ 
                        display: 'flex',
                        justifyContent: 'center',
                        alignItems: 'center',
                        width: 60,
                        height: 60,
                        mx: 'auto',
                        mb: 3,
                        borderRadius: 3,
                        background: 'linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)',
                        color: 'white',
                      }}
                    >
                      <TimelineIcon sx={{ fontSize: 32 }} />
                    </Box>
                    <Typography variant="h5" gutterBottom sx={{ fontWeight: 700, mb: 2 }}>
                      Portfolio Optimization
                    </Typography>
                    <Typography variant="body1" color="text.secondary" sx={{ fontWeight: 500 }}>
                      State-of-the-art optimization algorithms for portfolio construction
                    </Typography>
                  </Box>
                </motion.div>
              </Grid>
            </Grid>
          </Box>
        </motion.div>
      </Box>
    </Container>
  );
};

export default Home;
