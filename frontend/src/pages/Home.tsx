/**
 * Home Page
 * Landing page for Alpha Crucible - A public-facing page showcasing backtests and value proposition
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Container,
  Button,
  TextField,
  IconButton,
  Chip,
  Divider,
  Paper,
  Link,
  Snackbar,
  Alert,
} from '@mui/material';
import {
  Analytics as AnalyticsIcon,
  TrendingUp as TrendingUpIcon,
  Insights as InsightsIcon,
  Speed as SpeedIcon,
  PlayArrow as PlayArrowIcon,
  Email as EmailIcon,
  Chat as ChatIcon,
  YouTube as YouTubeIcon,
  Launch as LaunchIcon,
  CheckCircle as CheckCircleIcon,
  ArrowForward as ArrowForwardIcon,
  Send as SendIcon,
  ContactMail as ContactMailIcon,
  AutoGraph as AutoGraphIcon,
  Calculate as CalculateIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import { motion, useScroll, useTransform } from 'framer-motion';
import Logo from '@/components/common/Logo';
import { useTheme } from '@/contexts/ThemeContext';

// Configuration
const CONFIG = {
  discordUrl: 'https://discord.gg/59cTAYAdsy',
  youtubeVideoId: 'g2YsTpxWtio',
  contactEmail: 'alphacrucible@gmail.com',
  newsletterEndpoint: '/api/newsletter/subscribe', // UI placeholder - backend integration pending
};

const Home: React.FC = () => {
  const navigate = useNavigate();
  const { isDarkMode } = useTheme();
  const [email, setEmail] = useState('');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });
  const { scrollYProgress } = useScroll();
  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);
  const scale = useTransform(scrollYProgress, [0, 0.5], [1, 0.8]);

  const handleNewsletterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement actual newsletter subscription
    setSnackbar({
      open: true,
      message: 'Thank you for subscribing! We\'ll keep you updated.',
      severity: 'success',
    });
    setEmail('');
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const upcomingFeatures = [
    {
      icon: <AutoGraphIcon sx={{ fontSize: 40 }} />,
      title: 'Advanced Signal Analytics',
      description: 'Deep dive into signal performance with detailed analytics and attribution',
      comingSoon: 'Q2 2025',
    },
    {
      icon: <CalculateIcon sx={{ fontSize: 40 }} />,
      title: 'Portfolio Builder',
      description: 'Build and optimize custom portfolios with our advanced optimization algorithms',
      comingSoon: 'Q2 2025',
    },
    {
      icon: <AssessmentIcon sx={{ fontSize: 40 }} />,
      title: 'Risk Analysis Dashboard',
      description: 'Comprehensive risk metrics and scenario analysis tools',
      comingSoon: 'Q3 2025',
    },
  ];

  const valueProps = [
    {
      icon: <AnalyticsIcon sx={{ fontSize: 48 }} />,
      title: 'AI-Enhanced Signals',
      description: 'Signals generated from alternative data processed by advanced AI tools, capturing factors traditional analysis misses',
      gradient: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)',
    },
    {
      icon: <TrendingUpIcon sx={{ fontSize: 48 }} />,
      title: 'Sector-Focused Analysis',
      description: 'Sector-specific signals tailored to unique industry dynamics and drivers, not generic market-wide approaches',
      gradient: 'linear-gradient(135deg, #10b981 0%, #34d399 100%)',
    },
    {
      icon: <InsightsIcon sx={{ fontSize: 48 }} />,
      title: 'Rigorously Backtested',
      description: 'Every signal undergoes comprehensive historical backtesting with full performance metrics and risk analysis',
      gradient: 'linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%)',
    },
    {
      icon: <SpeedIcon sx={{ fontSize: 48 }} />,
      title: 'Alternative Data Edge',
      description: 'Access insights from non-traditional data sources—social sentiment, news flow, and more—before they appear in traditional metrics',
      gradient: 'linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)',
    },
  ];

  return (
    <Box>
      {/* Hero Section */}
      <Box
        sx={{
          minHeight: '90vh',
          display: 'flex',
          alignItems: 'center',
          position: 'relative',
          overflow: 'hidden',
          background: isDarkMode
            ? 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)'
            : 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #cbd5e1 100%)',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: isDarkMode
              ? 'radial-gradient(circle at 20% 50%, rgba(37, 99, 235, 0.15) 0%, transparent 50%), radial-gradient(circle at 80% 80%, rgba(139, 92, 246, 0.15) 0%, transparent 50%)'
              : 'radial-gradient(circle at 20% 50%, rgba(37, 99, 235, 0.1) 0%, transparent 50%), radial-gradient(circle at 80% 80%, rgba(139, 92, 246, 0.1) 0%, transparent 50%)',
            pointerEvents: 'none',
          },
        }}
      >
        <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1 }}>
          <Grid container spacing={6} alignItems="center">
            <Grid item xs={12} md={6}>
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
              >
                <Box sx={{ mb: 4 }}>
                  <Logo size="xlarge" showText={true} clickable={false} />
                </Box>
                <Typography
                  variant="h1"
                  sx={{
                    fontSize: { xs: '2.5rem', md: '3.5rem', lg: '4.5rem' },
                    fontWeight: 800,
                    mb: 3,
                    lineHeight: 1.1,
                    background: isDarkMode
                      ? 'linear-gradient(135deg, #ffffff 0%, #cbd5e1 50%, #94a3b8 100%)'
                      : 'linear-gradient(135deg, #0f172a 0%, #334155 50%, #64748b 100%)',
                    backgroundClip: 'text',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                  }}
                >
                  Quantitative Trading Signals
                  <br />
                  <Box component="span" sx={{ background: 'linear-gradient(135deg, #2563eb 0%, #8b5cf6 100%)', backgroundClip: 'text', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                    Validated by Backtesting
                  </Box>
                </Typography>
                <Typography
                  variant="h5"
                  sx={{
                    mb: 4,
                    color: 'text.secondary',
                    fontWeight: 400,
                    lineHeight: 1.7,
                    maxWidth: '90%',
                  }}
                >
                  Alpha Crucible leverages <strong>AI-powered analysis of alternative data</strong> to generate 
                  sector-specific trading signals. We capture insights traditional financial analysis misses, 
                  providing you with rigorously backtested quantitative strategies validated through comprehensive testing.
                </Typography>
                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                  <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                    <Button
                      variant="contained"
                      size="large"
                      endIcon={<ArrowForwardIcon />}
                      onClick={() => navigate('/backtest')}
                      sx={{
                        px: 4,
                        py: 1.5,
                        fontSize: '1.1rem',
                        fontWeight: 600,
                        background: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)',
                        boxShadow: '0 10px 30px rgba(37, 99, 235, 0.4)',
                        '&:hover': {
                          background: 'linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%)',
                          boxShadow: '0 15px 40px rgba(37, 99, 235, 0.5)',
                          transform: 'translateY(-2px)',
                        },
                      }}
                    >
                      View Backtests
                    </Button>
                  </motion.div>
                  <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                    <Button
                      variant="outlined"
                      size="large"
                      endIcon={<LaunchIcon />}
                      href={CONFIG.discordUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      sx={{
                        px: 4,
                        py: 1.5,
                        fontSize: '1.1rem',
                        fontWeight: 600,
                        borderWidth: 2,
                        '&:hover': {
                          borderWidth: 2,
                          transform: 'translateY(-2px)',
                        },
                      }}
                    >
                      Join Discord
                    </Button>
                  </motion.div>
                </Box>
              </motion.div>
            </Grid>
            <Grid item xs={12} md={6}>
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.8, delay: 0.2 }}
                style={{ opacity, scale }}
              >
                <Card
                  sx={{
                    background: isDarkMode
                      ? 'linear-gradient(145deg, rgba(30, 41, 59, 0.9) 0%, rgba(51, 65, 85, 0.7) 100%)'
                      : 'linear-gradient(145deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.9) 100%)',
                    backdropFilter: 'blur(20px)',
                    border: '1px solid',
                    borderColor: 'divider',
                    boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
                  }}
                >
                  <CardContent sx={{ p: 4 }}>
                    <Typography variant="h6" gutterBottom sx={{ fontWeight: 700, mb: 3 }}>
                      What You Get Access To:
                    </Typography>
                    {[
                      'AI-processed alternative data signals',
                      'Sector-specific trading insights',
                      'Historical backtest performance',
                      'Portfolio composition analysis',
                      'Risk-adjusted return metrics',
                      'Signal performance attribution',
                    ].map((feature, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.5, delay: 0.4 + index * 0.1 }}
                      >
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                          <CheckCircleIcon sx={{ color: 'success.main', mr: 2 }} />
                          <Typography variant="body1" sx={{ fontWeight: 500 }}>
                            {feature}
                          </Typography>
                        </Box>
                      </motion.div>
                    ))}
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Project Description Section */}
      <Box
        sx={{
          py: { xs: 8, md: 12 },
          background: isDarkMode
            ? 'linear-gradient(180deg, #1e293b 0%, #0f172a 100%)'
            : 'linear-gradient(180deg, #ffffff 0%, #f8fafc 100%)',
        }}
      >
        <Container maxWidth="lg">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <Typography
              variant="h2"
              align="center"
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
              About Alpha Crucible
            </Typography>
          </motion.div>

          <Grid container spacing={6}>
            <Grid item xs={12} md={6}>
              <motion.div
                initial={{ opacity: 0, x: -30 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.8 }}
              >
                <Card
                  sx={{
                    height: '100%',
                    background: isDarkMode
                      ? 'linear-gradient(145deg, #1e293b 0%, #334155 100%)'
                      : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
                    border: '1px solid',
                    borderColor: 'divider',
                    boxShadow: '0 10px 40px rgba(0, 0, 0, 0.1)',
                  }}
                >
                  <CardContent sx={{ p: 4 }}>
                    <Typography variant="h4" gutterBottom sx={{ fontWeight: 700, mb: 3 }}>
                      Our Mission
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 3, lineHeight: 1.8, fontSize: '1.1rem' }}>
                      Alpha Crucible is built on three core principles that set us apart from traditional 
                      financial analysis: <strong>Sector-Specific Focus</strong>, <strong>Alternative Data Integration</strong>, 
                      and <strong>AI-Powered Processing</strong>.
                    </Typography>
                    <Typography variant="body1" sx={{ lineHeight: 1.8, fontSize: '1.1rem' }}>
                      Traditional financial analysis relies on price and volume data that everyone sees. We go beyond this 
                      by processing alternative data sources—social media sentiment, news flow, web traffic patterns, 
                      and more—using advanced AI tools to extract meaningful signals. Our sector-specific approach ensures 
                      these insights are relevant and actionable for specific industries.
                    </Typography>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
            <Grid item xs={12} md={6}>
              <motion.div
                initial={{ opacity: 0, x: 30 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.8 }}
              >
                <Card
                  sx={{
                    height: '100%',
                    background: isDarkMode
                      ? 'linear-gradient(145deg, #1e293b 0%, #334155 100%)'
                      : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
                    border: '1px solid',
                    borderColor: 'divider',
                    boxShadow: '0 10px 40px rgba(0, 0, 0, 0.1)',
                  }}
                >
                  <CardContent sx={{ p: 4 }}>
                    <Typography variant="h4" gutterBottom sx={{ fontWeight: 700, mb: 3 }}>
                      How We Create Value
                    </Typography>
                    <Box sx={{ mb: 3 }}>
                      <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                        🎯 Sector-Specific Signals
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2, lineHeight: 1.7 }}>
                        Instead of generic market-wide signals, we focus on sector-specific analysis. 
                        Each signal is tailored to the unique dynamics, drivers, and patterns of specific 
                        sectors, providing more relevant and actionable insights.
                      </Typography>
                    </Box>
                    <Box sx={{ mb: 3 }}>
                      <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                        📡 Alternative Data Sources
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2, lineHeight: 1.7 }}>
                        We go beyond traditional financial data—analyzing social media sentiment, news flow, 
                        satellite imagery, web traffic, and other alternative data sources. These signals often 
                        reveal insights before they appear in traditional metrics.
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                        🤖 AI-Powered Processing
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.7 }}>
                        Modern AI tools process vast amounts of alternative data to identify patterns, 
                        correlations, and factors invisible to traditional analysis. This creates a competitive 
                        edge by discovering opportunities others can't see.
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Value Propositions */}
      <Box sx={{ py: { xs: 8, md: 12 }, background: isDarkMode ? '#0f172a' : '#ffffff' }}>
        <Container maxWidth="lg">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <Typography
              variant="h2"
              align="center"
              sx={{
                fontWeight: 800,
                mb: 8,
                background: isDarkMode
                  ? 'linear-gradient(135deg, #f8fafc 0%, #cbd5e1 100%)'
                  : 'linear-gradient(135deg, #0f172a 0%, #475569 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              Why Alpha Crucible?
            </Typography>
          </motion.div>

          <Grid container spacing={4}>
            {valueProps.map((prop, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <motion.div
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  whileHover={{ y: -10 }}
                >
                  <Card
                    sx={{
                      height: '100%',
                      background: isDarkMode
                        ? 'linear-gradient(145deg, #1e293b 0%, #334155 100%)'
                        : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
                      border: '1px solid',
                      borderColor: 'divider',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        boxShadow: '0 20px 60px rgba(0, 0, 0, 0.2)',
                        transform: 'translateY(-5px)',
                      },
                    }}
                  >
                    <CardContent sx={{ p: 4, textAlign: 'center' }}>
                      <Box
                        sx={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          width: 100,
                          height: 100,
                          borderRadius: 4,
                          background: prop.gradient,
                          color: 'white',
                          mb: 3,
                        }}
                      >
                        {prop.icon}
                      </Box>
                      <Typography variant="h5" gutterBottom sx={{ fontWeight: 700, mb: 2 }}>
                        {prop.title}
                      </Typography>
                      <Typography variant="body1" color="text.secondary" sx={{ lineHeight: 1.7, fontSize: '0.95rem' }}>
                        {prop.description}
                      </Typography>
                    </CardContent>
                  </Card>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* YouTube Video Section */}
      <Box
        sx={{
          py: { xs: 8, md: 12 },
          background: isDarkMode
            ? 'linear-gradient(180deg, #1e293b 0%, #0f172a 100%)'
            : 'linear-gradient(180deg, #f8fafc 0%, #ffffff 100%)',
        }}
      >
        <Container maxWidth="lg">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <Box sx={{ textAlign: 'center', mb: 6 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 3 }}>
                <YouTubeIcon sx={{ fontSize: 48, color: 'error.main', mr: 2 }} />
                <Typography
                  variant="h2"
                  sx={{
                    fontWeight: 800,
                    background: isDarkMode
                      ? 'linear-gradient(135deg, #f8fafc 0%, #cbd5e1 100%)'
                      : 'linear-gradient(135deg, #0f172a 0%, #475569 100%)',
                    backgroundClip: 'text',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                  }}
                >
                  Learn More
                </Typography>
              </Box>
              <Typography variant="h6" color="text.secondary" sx={{ maxWidth: 600, mx: 'auto' }}>
                Watch our introduction video to understand how Alpha Crucible works
              </Typography>
            </Box>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <Box
              sx={{
                position: 'relative',
                paddingBottom: '56.25%', // 16:9 aspect ratio
                height: 0,
                overflow: 'hidden',
                borderRadius: 4,
                boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
                background: '#000',
              }}
            >
              <iframe
                width="100%"
                height="100%"
                src={`https://www.youtube.com/embed/${CONFIG.youtubeVideoId}`}
                title="Alpha Crucible Introduction"
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  height: '100%',
                }}
              />
            </Box>
          </motion.div>
        </Container>
      </Box>

      {/* What's Coming Section */}
      <Box sx={{ py: { xs: 8, md: 12 }, background: isDarkMode ? '#0f172a' : '#ffffff' }}>
        <Container maxWidth="lg">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <Typography
              variant="h2"
              align="center"
              sx={{
                fontWeight: 800,
                mb: 2,
                background: isDarkMode
                  ? 'linear-gradient(135deg, #f8fafc 0%, #cbd5e1 100%)'
                  : 'linear-gradient(135deg, #0f172a 0%, #475569 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              What's Coming Next
            </Typography>
            <Typography variant="h6" align="center" color="text.secondary" sx={{ mb: 8, maxWidth: 700, mx: 'auto' }}>
              We're continuously expanding our platform with new features and capabilities
            </Typography>
          </motion.div>

          <Grid container spacing={4}>
            {upcomingFeatures.map((feature, index) => (
              <Grid item xs={12} md={4} key={index}>
                <motion.div
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  whileHover={{ y: -5 }}
                >
                  <Card
                    sx={{
                      height: '100%',
                      background: isDarkMode
                        ? 'linear-gradient(145deg, #1e293b 0%, #334155 100%)'
                        : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
                      border: '1px solid',
                      borderColor: 'divider',
                      position: 'relative',
                      overflow: 'hidden',
                      '&::before': {
                        content: '""',
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        height: '4px',
                        background: 'linear-gradient(135deg, #2563eb 0%, #8b5cf6 100%)',
                      },
                    }}
                  >
                    <CardContent sx={{ p: 4 }}>
                      <Box sx={{ mb: 3 }}>
                        <Box
                          sx={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            width: 80,
                            height: 80,
                            borderRadius: 3,
                            background: 'linear-gradient(135deg, #2563eb 0%, #8b5cf6 100%)',
                            color: 'white',
                          }}
                        >
                          {feature.icon}
                        </Box>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'start', justifyContent: 'space-between', mb: 2 }}>
                        <Typography variant="h5" sx={{ fontWeight: 700, flex: 1 }}>
                          {feature.title}
                        </Typography>
                        <Chip
                          label={feature.comingSoon}
                          size="small"
                          sx={{
                            background: 'linear-gradient(135deg, #2563eb 0%, #8b5cf6 100%)',
                            color: 'white',
                            fontWeight: 600,
                          }}
                        />
                      </Box>
                      <Typography variant="body1" color="text.secondary" sx={{ lineHeight: 1.7 }}>
                        {feature.description}
                      </Typography>
                    </CardContent>
                  </Card>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* Newsletter & Contact Section */}
      <Box
        sx={{
          py: { xs: 8, md: 12 },
          background: isDarkMode
            ? 'linear-gradient(180deg, #1e293b 0%, #0f172a 100%)'
            : 'linear-gradient(180deg, #f8fafc 0%, #ffffff 100%)',
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={6}>
            {/* Newsletter */}
            <Grid item xs={12} md={6}>
              <motion.div
                initial={{ opacity: 0, x: -30 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.8 }}
              >
                <Card
                  sx={{
                    height: '100%',
                    background: isDarkMode
                      ? 'linear-gradient(145deg, #1e293b 0%, #334155 100%)'
                      : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
                    border: '1px solid',
                    borderColor: 'divider',
                  }}
                >
                  <CardContent sx={{ p: 4 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                      <EmailIcon sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
                      <Typography variant="h4" sx={{ fontWeight: 700 }}>
                        Stay Updated
                      </Typography>
                    </Box>
                    <Typography variant="body1" color="text.secondary" sx={{ mb: 4, lineHeight: 1.7 }}>
                      Subscribe to our newsletter to receive updates on new backtests, feature releases, 
                      and quantitative trading insights.
                    </Typography>
                    <form onSubmit={handleNewsletterSubmit}>
                      <Box sx={{ display: 'flex', gap: 2 }}>
                        <TextField
                          fullWidth
                          type="email"
                          placeholder="Enter your email"
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          required
                          sx={{
                            '& .MuiOutlinedInput-root': {
                              background: isDarkMode ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.02)',
                            },
                          }}
                        />
                        <Button
                          type="submit"
                          variant="contained"
                          startIcon={<SendIcon />}
                          sx={{
                            px: 4,
                            background: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)',
                            '&:hover': {
                              background: 'linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%)',
                            },
                          }}
                        >
                          Subscribe
                        </Button>
                      </Box>
                    </form>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>

            {/* Contact & Discord */}
            <Grid item xs={12} md={6}>
              <motion.div
                initial={{ opacity: 0, x: 30 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.8 }}
              >
                <Card
                  sx={{
                    height: '100%',
                    background: isDarkMode
                      ? 'linear-gradient(145deg, #1e293b 0%, #334155 100%)'
                      : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
                    border: '1px solid',
                    borderColor: 'divider',
                  }}
                >
                  <CardContent sx={{ p: 4 }}>
                    <Typography variant="h4" sx={{ fontWeight: 700, mb: 4 }}>
                      Get In Touch
                    </Typography>

                    {/* Discord */}
                    <Box sx={{ mb: 4 }}>
                      <Button
                        fullWidth
                        variant="contained"
                        startIcon={<ChatIcon />}
                        endIcon={<LaunchIcon />}
                        href={CONFIG.discordUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        sx={{
                          py: 1.5,
                          mb: 2,
                          background: 'linear-gradient(135deg, #5865F2 0%, #7289da 100%)',
                          '&:hover': {
                            background: 'linear-gradient(135deg, #4752C4 0%, #5865F2 100%)',
                          },
                        }}
                      >
                        Join Our Discord Community
                      </Button>
                      <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center' }}>
                        Connect with the community, ask questions, and stay updated
                      </Typography>
                    </Box>

                    <Divider sx={{ my: 3 }} />

                    {/* Contact Email */}
                    <Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        <ContactMailIcon sx={{ color: 'primary.main', mr: 2 }} />
                        <Typography variant="h6" sx={{ fontWeight: 600 }}>
                          Contact Us
                        </Typography>
                      </Box>
                      <Link
                        href={`mailto:${CONFIG.contactEmail}`}
                        sx={{
                          color: 'primary.main',
                          textDecoration: 'none',
                          fontSize: '1.1rem',
                          fontWeight: 500,
                          '&:hover': {
                            textDecoration: 'underline',
                          },
                        }}
                      >
                        {CONFIG.contactEmail}
                      </Link>
                    </Box>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Final CTA Section */}
      <Box
        sx={{
          py: { xs: 8, md: 12 },
          background: isDarkMode
            ? 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)'
            : 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
        }}
      >
        <Container maxWidth="md">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <Paper
              elevation={0}
              sx={{
                p: { xs: 4, md: 6 },
                textAlign: 'center',
                background: isDarkMode
                  ? 'linear-gradient(145deg, #1e293b 0%, #334155 100%)'
                  : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 4,
              }}
            >
              <Typography
                variant="h3"
                sx={{
                  fontWeight: 800,
                  mb: 3,
                  background: isDarkMode
                    ? 'linear-gradient(135deg, #f8fafc 0%, #cbd5e1 100%)'
                    : 'linear-gradient(135deg, #0f172a 0%, #475569 100%)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
              >
                Ready to Explore?
              </Typography>
              <Typography variant="h6" color="text.secondary" sx={{ mb: 4, lineHeight: 1.7 }}>
                Start exploring our backtest results and discover the power of quantitative trading signals
              </Typography>
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Button
                  variant="contained"
                  size="large"
                  endIcon={<PlayArrowIcon />}
                  onClick={() => navigate('/backtest')}
                  sx={{
                    px: 6,
                    py: 2,
                    fontSize: '1.2rem',
                    fontWeight: 600,
                    background: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)',
                    boxShadow: '0 15px 40px rgba(37, 99, 235, 0.4)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%)',
                      boxShadow: '0 20px 50px rgba(37, 99, 235, 0.5)',
                    },
                  }}
                >
                  View Backtests Now
                </Button>
              </motion.div>
            </Paper>
          </motion.div>
        </Container>
      </Box>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Home;
