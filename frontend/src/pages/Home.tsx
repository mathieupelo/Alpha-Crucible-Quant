/**
 * Home Page - Premium Animated Version
 * Ultra-polished landing page with Netflix/Apple/Spotify-level animations
 */

import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from 'react-query';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Container,
  Button,
  TextField,
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
  ShowChart as ShowChartIcon,
  Security as SecurityIcon,
  Bolt as BoltIcon,
  AutoAwesome as AutoAwesomeIcon,
  CalendarToday as CalendarTodayIcon,
  Timeline as TimelineIcon,
  Article as ArticleIcon,
} from '@mui/icons-material';
import { motion, useScroll, useTransform, useInView } from 'framer-motion';
import { format, parseISO } from 'date-fns';
import Logo from '@/components/common/Logo';
import AnimatedBackground from '@/components/common/AnimatedBackground';
import GradientMesh from '@/components/common/GradientMesh';
import { useTheme } from '@/contexts/ThemeContext';
import { backtestApi } from '@/services/api';
import SectorsSection from '@/components/sectors/SectorsSection';
import NewsFeed from '@/components/news/NewsFeed';

// Configuration
const CONFIG = {
  discordUrl: 'https://discord.gg/59cTAYAdsy',
  youtubeVideoId: 'g2YsTpxWtio',
  contactEmail: 'alphacrucible@gmail.com',
  newsletterEndpoint: '/api/newsletter/subscribe',
};

// Animation variants
const fadeInUp = {
  hidden: { opacity: 0, y: 60 },
  visible: { 
    opacity: 1, 
    y: 0,
    transition: { duration: 0.8, ease: [0.6, -0.05, 0.01, 0.99] }
  },
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15,
      delayChildren: 0.2,
    },
  },
};

const scaleIn = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: { 
    opacity: 1, 
    scale: 1,
    transition: { duration: 0.6, ease: [0.6, -0.05, 0.01, 0.99] }
  },
};

// Latest Backtest Showcase Component
const LatestBacktestShowcase: React.FC = () => {
  const navigate = useNavigate();
  const { isDarkMode } = useTheme();

  // Fetch most recent backtest
  const { data: backtestsData, isLoading: backtestsLoading } = useQuery(
    'latest-backtest',
    () => backtestApi.getBacktests(1, 1),
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
      refetchOnWindowFocus: false,
    }
  );

  const latestBacktest = backtestsData?.backtests?.[0];
  const runId = latestBacktest?.run_id;

  // Fetch metrics for the latest backtest
  const { data: metricsData, isLoading: metricsLoading } = useQuery(
    ['backtest-metrics', runId],
    () => backtestApi.getBacktestMetrics(runId!),
    {
      enabled: !!runId,
      staleTime: 5 * 60 * 1000,
      refetchOnWindowFocus: false,
    }
  );

  if (backtestsLoading || metricsLoading || !latestBacktest || !metricsData) {
    return null; // Don't show anything if loading or no data
  }

  const metrics = metricsData;
  const formatDate = (dateStr: string) => format(parseISO(dateStr), 'MMM dd, yyyy');
  const formatPercent = (val: number) => `${val >= 0 ? '+' : ''}${val.toFixed(2)}%`;

  return (
    <Box
      sx={{
        py: { xs: 8, md: 12 },
        background: 'transparent',
        position: 'relative',
        zIndex: 1,
      }}
    >
      <Container maxWidth="lg">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          variants={staggerContainer}
        >
          <motion.div variants={fadeInUp}>
            <Box sx={{ textAlign: 'center', mb: 6 }}>
              <motion.div
                animate={{
                  scale: [1, 1.1, 1],
                }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                  ease: 'easeInOut',
                }}
              >
                <AutoAwesomeIcon
                  sx={{
                    fontSize: 56,
                    color: 'primary.main',
                    mb: 2,
                    background: 'linear-gradient(135deg, #2563eb 0%, #8b5cf6 100%)',
                    backgroundClip: 'text',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                  }}
                />
              </motion.div>
              <Typography
                variant="h2"
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
                Latest Backtest Results
              </Typography>
              <Typography variant="h6" color="text.secondary" sx={{ maxWidth: 700, mx: 'auto' }}>
                Explore our most recent quantitative trading strategy performance
              </Typography>
            </Box>
          </motion.div>

          <motion.div variants={scaleIn} whileHover={{ y: -10, transition: { duration: 0.3 } }}>
            <Card
              sx={{
                background: isDarkMode
                  ? 'linear-gradient(145deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.85) 100%)'
                  : 'linear-gradient(145deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.95) 100%)',
                backdropFilter: 'blur(20px)',
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 4,
                overflow: 'hidden',
                position: 'relative',
                boxShadow: '0 30px 80px rgba(0, 0, 0, 0.3)',
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  height: '4px',
                  background: 'linear-gradient(135deg, #2563eb 0%, #8b5cf6 50%, #ec4899 100%)',
                  backgroundSize: '200% 100%',
                  animation: 'gradientFlow 3s linear infinite',
                  '@keyframes gradientFlow': {
                    '0%': { backgroundPosition: '0% 0%' },
                    '100%': { backgroundPosition: '200% 0%' },
                  },
                },
                transition: 'all 0.3s ease',
                '&:hover': {
                  boxShadow: '0 40px 100px rgba(37, 99, 235, 0.4)',
                  transform: 'translateY(-5px)',
                },
              }}
            >
              <CardContent sx={{ p: { xs: 4, md: 6 } }}>
                {/* Header */}
                <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, justifyContent: 'space-between', alignItems: { xs: 'flex-start', md: 'center' }, mb: 4 }}>
                  <Box>
                    <Typography
                      variant="h4"
                      sx={{
                        fontWeight: 700,
                        mb: 1,
                        background: 'linear-gradient(135deg, #2563eb 0%, #8b5cf6 100%)',
                        backgroundClip: 'text',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                      }}
                    >
                      {latestBacktest.name || `Backtest ${latestBacktest.run_id}`}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap', mt: 1 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <CalendarTodayIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
                        <Typography variant="body2" color="text.secondary">
                          {formatDate(latestBacktest.start_date)} - {formatDate(latestBacktest.end_date)}
                        </Typography>
                      </Box>
                      {latestBacktest.universe_name && (
                        <Chip
                          label={latestBacktest.universe_name}
                          size="small"
                          sx={{
                            background: 'linear-gradient(135deg, rgba(37, 99, 235, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%)',
                            border: '1px solid',
                            borderColor: 'primary.main',
                          }}
                        />
                      )}
                    </Box>
                  </Box>
                  <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                    <Button
                      variant="contained"
                      endIcon={<ArrowForwardIcon />}
                      onClick={() => navigate(`/backtest?runId=${latestBacktest.run_id}`)}
                      sx={{
                        mt: { xs: 2, md: 0 },
                        px: 4,
                        py: 1.5,
                        background: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)',
                        boxShadow: '0 10px 30px rgba(37, 99, 235, 0.4)',
                        '&:hover': {
                          background: 'linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%)',
                          boxShadow: '0 15px 40px rgba(37, 99, 235, 0.5)',
                        },
                      }}
                    >
                      View Details
                    </Button>
                  </motion.div>
                </Box>

                {/* Key Metrics Grid */}
                <Grid container spacing={3} sx={{ mb: 4 }}>
                  <Grid item xs={6} sm={4} md={3}>
                    <motion.div whileHover={{ scale: 1.05 }}>
                      <Card
                        sx={{
                          background: isDarkMode
                            ? 'rgba(37, 99, 235, 0.1)'
                            : 'rgba(37, 99, 235, 0.05)',
                          border: '1px solid',
                          borderColor: isDarkMode ? 'rgba(37, 99, 235, 0.3)' : 'rgba(37, 99, 235, 0.2)',
                          borderRadius: 3,
                          p: 2,
                          textAlign: 'center',
                        }}
                      >
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 1, fontWeight: 500 }}>
                          Total Return
                        </Typography>
                        <Typography
                          variant="h5"
                          sx={{
                            fontWeight: 800,
                            color: metrics.total_return >= 0 ? 'success.main' : 'error.main',
                          }}
                        >
                          {formatPercent(metrics.total_return)}
                        </Typography>
                      </Card>
                    </motion.div>
                  </Grid>
                  <Grid item xs={6} sm={4} md={3}>
                    <motion.div whileHover={{ scale: 1.05 }}>
                      <Card
                        sx={{
                          background: isDarkMode
                            ? 'rgba(16, 185, 129, 0.1)'
                            : 'rgba(16, 185, 129, 0.05)',
                          border: '1px solid',
                          borderColor: isDarkMode ? 'rgba(16, 185, 129, 0.3)' : 'rgba(16, 185, 129, 0.2)',
                          borderRadius: 3,
                          p: 2,
                          textAlign: 'center',
                        }}
                      >
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 1, fontWeight: 500 }}>
                          Sharpe Ratio
                        </Typography>
                        <Typography variant="h5" sx={{ fontWeight: 800, color: 'success.main' }}>
                          {metrics.sharpe_ratio.toFixed(2)}
                        </Typography>
                      </Card>
                    </motion.div>
                  </Grid>
                  <Grid item xs={6} sm={4} md={3}>
                    <motion.div whileHover={{ scale: 1.05 }}>
                      <Card
                        sx={{
                          background: isDarkMode
                            ? 'rgba(139, 92, 246, 0.1)'
                            : 'rgba(139, 92, 246, 0.05)',
                          border: '1px solid',
                          borderColor: isDarkMode ? 'rgba(139, 92, 246, 0.3)' : 'rgba(139, 92, 246, 0.2)',
                          borderRadius: 3,
                          p: 2,
                          textAlign: 'center',
                        }}
                      >
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 1, fontWeight: 500 }}>
                          Alpha
                        </Typography>
                        <Typography
                          variant="h5"
                          sx={{
                            fontWeight: 800,
                            color: metrics.alpha >= 0 ? 'success.main' : 'error.main',
                          }}
                        >
                          {formatPercent(metrics.alpha)}
                        </Typography>
                      </Card>
                    </motion.div>
                  </Grid>
                  <Grid item xs={6} sm={4} md={3}>
                    <motion.div whileHover={{ scale: 1.05 }}>
                      <Card
                        sx={{
                          background: isDarkMode
                            ? 'rgba(245, 158, 11, 0.1)'
                            : 'rgba(245, 158, 11, 0.05)',
                          border: '1px solid',
                          borderColor: isDarkMode ? 'rgba(245, 158, 11, 0.3)' : 'rgba(245, 158, 11, 0.2)',
                          borderRadius: 3,
                          p: 2,
                          textAlign: 'center',
                        }}
                      >
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 1, fontWeight: 500 }}>
                          Max Drawdown
                        </Typography>
                        <Typography variant="h5" sx={{ fontWeight: 800, color: 'warning.main' }}>
                          {formatPercent(metrics.max_drawdown)}
                        </Typography>
                      </Card>
                    </motion.div>
                  </Grid>
                </Grid>

                {/* Additional Metrics */}
                <Grid container spacing={2}>
                  <Grid item xs={6} sm={4}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <TimelineIcon sx={{ fontSize: 20, color: 'primary.main' }} />
                      <Typography variant="body2" color="text.secondary">
                        <strong>Volatility:</strong> {formatPercent(metrics.volatility)}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={4}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <TrendingUpIcon sx={{ fontSize: 20, color: 'success.main' }} />
                      <Typography variant="body2" color="text.secondary">
                        <strong>Win Rate:</strong> {formatPercent(metrics.win_rate)}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={4}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <ShowChartIcon sx={{ fontSize: 20, color: 'info.main' }} />
                      <Typography variant="body2" color="text.secondary">
                        <strong>Annualized Return:</strong> {formatPercent(metrics.annualized_return)}
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </motion.div>
        </motion.div>
      </Container>
    </Box>
  );
};

const Home: React.FC = () => {
  const navigate = useNavigate();
  const { isDarkMode } = useTheme();
  const [email, setEmail] = useState('');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });
  const heroRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll();
  
  // Parallax effects
  const heroY = useTransform(scrollYProgress, [0, 1], ['0%', '50%']);
  const heroOpacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);
  const heroScale = useTransform(scrollYProgress, [0, 0.5], [1, 0.95]);

  const handleNewsletterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
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

  // Animated Counter Component
  const AnimatedCounter: React.FC<{ end: number; duration?: number; suffix?: string }> = ({ end, duration = 2, suffix = '' }) => {
    const [count, setCount] = useState(0);
    const ref = React.useRef<HTMLSpanElement>(null);
    const isInView = useInView(ref, { once: true, amount: 0.5 });

    React.useEffect(() => {
      if (!isInView) return;
      
      let startTime: number | null = null;
      const animate = (timestamp: number) => {
        if (!startTime) startTime = timestamp;
        const progress = Math.min((timestamp - startTime) / (duration * 1000), 1);
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        setCount(Math.floor(easeOutQuart * end));
        if (progress < 1) {
          requestAnimationFrame(animate);
        }
      };
      requestAnimationFrame(animate);
    }, [end, duration, isInView]);

    return <span ref={ref}>{count}{suffix}</span>;
  };

  const stats = [
    { icon: <ShowChartIcon sx={{ fontSize: 40 }} />, value: 150, suffix: '+', label: 'Signals Analyzed', color: '#2563eb' },
    { icon: <TrendingUpIcon sx={{ fontSize: 40 }} />, value: 25, suffix: '%', label: 'Avg Alpha', color: '#10b981' },
    { icon: <SecurityIcon sx={{ fontSize: 40 }} />, value: 95, suffix: '%', label: 'Backtest Accuracy', color: '#8b5cf6' },
    { icon: <BoltIcon sx={{ fontSize: 40 }} />, value: 10, suffix: 'ms', label: 'Signal Latency', color: '#f59e0b' },
  ];

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
    <Box sx={{ position: 'relative', overflow: 'hidden' }}>
      {/* Animated Backgrounds */}
      <GradientMesh />
      <AnimatedBackground />

      {/* Hero Section with Parallax */}
      <Box
        ref={heroRef}
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          position: 'relative',
          overflow: 'hidden',
          background: 'transparent',
          zIndex: 1,
        }}
      >
        <motion.div
          style={{
            y: heroY,
            opacity: heroOpacity,
            scale: heroScale,
          }}
        >
          <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 2 }}>
            <Grid container spacing={6} alignItems="center">
              <Grid item xs={12} md={6}>
                <motion.div
                  initial="hidden"
                  animate="visible"
                  variants={staggerContainer}
                >
                  <motion.div variants={fadeInUp}>
                    <Box sx={{ mb: 4 }}>
                      <motion.div
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        <Logo size="xlarge" showText={true} clickable={false} />
                      </motion.div>
                    </Box>
                  </motion.div>
                  
                  <motion.div variants={fadeInUp}>
                    <Typography
                      variant="h1"
                      sx={{
                        fontSize: { xs: '2.5rem', md: '3.5rem', lg: '5rem' },
                        fontWeight: 900,
                        mb: 3,
                        lineHeight: 1.1,
                        letterSpacing: '-0.03em',
                        background: isDarkMode
                          ? 'linear-gradient(135deg, #ffffff 0%, #cbd5e1 50%, #94a3b8 100%)'
                          : 'linear-gradient(135deg, #0f172a 0%, #334155 50%, #64748b 100%)',
                        backgroundClip: 'text',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        position: 'relative',
                      }}
                    >
                      <motion.span
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, delay: 0.2 }}
                      >
                        Quantitative Trading Signals
                      </motion.span>
                      <br />
                      <motion.span
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, delay: 0.4 }}
                      >
                        <Box 
                          component="span" 
                          sx={{ 
                            background: 'linear-gradient(135deg, #2563eb 0%, #8b5cf6 50%, #ec4899 100%)',
                            backgroundClip: 'text', 
                            WebkitBackgroundClip: 'text', 
                            WebkitTextFillColor: 'transparent',
                            backgroundSize: '200% 200%',
                            animation: 'gradientShift 3s ease infinite',
                            '@keyframes gradientShift': {
                              '0%, 100%': { backgroundPosition: '0% 50%' },
                              '50%': { backgroundPosition: '100% 50%' },
                            },
                          }}
                        >
                          Validated by Backtesting
                        </Box>
                      </motion.span>
                    </Typography>
                  </motion.div>

                  <motion.div variants={fadeInUp}>
                    <Typography
                      variant="h5"
                      sx={{
                        mb: 4,
                        color: 'text.secondary',
                        fontWeight: 400,
                        lineHeight: 1.8,
                        maxWidth: '90%',
                        fontSize: { xs: '1rem', md: '1.25rem' },
                      }}
                    >
                      Alpha Crucible leverages <strong>AI-powered analysis of alternative data</strong> to generate 
                      sector-specific trading signals. We capture insights traditional financial analysis misses, 
                      providing you with rigorously backtested quantitative strategies validated through comprehensive testing.
                    </Typography>
                  </motion.div>

                  <motion.div variants={fadeInUp}>
                    <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mb: 4 }}>
                      <motion.div 
                        whileHover={{ scale: 1.05, y: -2 }} 
                        whileTap={{ scale: 0.95 }}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.6, delay: 0.6 }}
                      >
                        <Button
                          variant="contained"
                          size="large"
                          endIcon={<ArrowForwardIcon />}
                          onClick={() => navigate('/backtest')}
                          sx={{
                            px: 5,
                            py: 2,
                            fontSize: '1.1rem',
                            fontWeight: 600,
                            background: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)',
                            boxShadow: '0 20px 40px rgba(37, 99, 235, 0.4)',
                            position: 'relative',
                            overflow: 'hidden',
                            '&::before': {
                              content: '""',
                              position: 'absolute',
                              top: 0,
                              left: '-100%',
                              width: '100%',
                              height: '100%',
                              background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)',
                              transition: 'left 0.5s',
                            },
                            '&:hover': {
                              background: 'linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%)',
                              boxShadow: '0 25px 50px rgba(37, 99, 235, 0.6)',
                              transform: 'translateY(-2px)',
                              '&::before': {
                                left: '100%',
                              },
                            },
                          }}
                        >
                          View Backtests
                        </Button>
                      </motion.div>
                      <motion.div 
                        whileHover={{ scale: 1.05, y: -2 }} 
                        whileTap={{ scale: 0.95 }}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.6, delay: 0.7 }}
                      >
                        <Button
                          variant="outlined"
                          size="large"
                          endIcon={<LaunchIcon />}
                          href={CONFIG.discordUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          sx={{
                            px: 5,
                            py: 2,
                            fontSize: '1.1rem',
                            fontWeight: 600,
                            borderWidth: 2,
                            backdropFilter: 'blur(10px)',
                            background: isDarkMode ? 'rgba(30, 41, 59, 0.3)' : 'rgba(255, 255, 255, 0.3)',
                            '&:hover': {
                              borderWidth: 2,
                              transform: 'translateY(-2px)',
                              background: isDarkMode ? 'rgba(30, 41, 59, 0.5)' : 'rgba(255, 255, 255, 0.5)',
                              boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)',
                            },
                          }}
                        >
                          Join Discord
                        </Button>
                      </motion.div>
                    </Box>
                  </motion.div>
                </motion.div>
              </Grid>

              <Grid item xs={12} md={6}>
                <motion.div
                  initial={{ opacity: 0, scale: 0.8, rotateY: 15 }}
                  animate={{ opacity: 1, scale: 1, rotateY: 0 }}
                  transition={{ duration: 1, delay: 0.3, ease: [0.6, -0.05, 0.01, 0.99] }}
                >
                  <motion.div
                    whileHover={{ 
                      scale: 1.02,
                      rotateY: -5,
                      transition: { duration: 0.3 }
                    }}
                    style={{ perspective: 1000 }}
                  >
                    <Card
                      sx={{
                        background: isDarkMode
                          ? 'linear-gradient(145deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.85) 100%)'
                          : 'linear-gradient(145deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.95) 100%)',
                        backdropFilter: 'blur(30px)',
                        border: '1px solid',
                        borderColor: isDarkMode ? 'rgba(148, 163, 184, 0.2)' : 'rgba(148, 163, 184, 0.3)',
                        boxShadow: '0 30px 80px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.05) inset',
                        borderRadius: 4,
                        position: 'relative',
                        overflow: 'hidden',
                        '&::before': {
                          content: '""',
                          position: 'absolute',
                          top: 0,
                          left: 0,
                          right: 0,
                          height: '2px',
                          background: 'linear-gradient(90deg, #2563eb, #8b5cf6, #ec4899, #2563eb)',
                          backgroundSize: '200% 100%',
                          animation: 'gradientFlow 3s linear infinite',
                          '@keyframes gradientFlow': {
                            '0%': { backgroundPosition: '0% 0%' },
                            '100%': { backgroundPosition: '200% 0%' },
                          },
                        },
                      }}
                    >
                      <CardContent sx={{ p: 5 }}>
                        <Typography variant="h5" gutterBottom sx={{ fontWeight: 700, mb: 4, fontSize: '1.5rem' }}>
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
                            initial={{ opacity: 0, x: -30 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.5, delay: 0.8 + index * 0.1 }}
                            whileHover={{ x: 5 }}
                          >
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2.5 }}>
                              <motion.div
                                animate={{ 
                                  scale: [1, 1.2, 1],
                                  rotate: [0, 10, 0]
                                }}
                                transition={{ 
                                  duration: 0.5, 
                                  delay: 0.9 + index * 0.1,
                                  ease: 'easeInOut'
                                }}
                              >
                                <CheckCircleIcon sx={{ color: 'success.main', mr: 2, fontSize: 28 }} />
                              </motion.div>
                              <Typography variant="body1" sx={{ fontWeight: 500, fontSize: '1.05rem' }}>
                                {feature}
                              </Typography>
                            </Box>
                          </motion.div>
                        ))}
                      </CardContent>
                    </Card>
                  </motion.div>
                </motion.div>
              </Grid>
            </Grid>
          </Container>
        </motion.div>

        {/* Scroll Indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 1.5 }}
          style={{
            position: 'absolute',
            bottom: 40,
            left: '50%',
            transform: 'translateX(-50%)',
            zIndex: 10,
          }}
        >
          <motion.div
            animate={{ y: [0, 10, 0] }}
            transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
          >
            <Box
              sx={{
                width: 30,
                height: 50,
                border: `2px solid ${isDarkMode ? 'rgba(255,255,255,0.3)' : 'rgba(0,0,0,0.3)'}`,
                borderRadius: 25,
                position: 'relative',
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  top: 10,
                  left: '50%',
                  transform: 'translateX(-50%)',
                  width: 6,
                  height: 6,
                  borderRadius: '50%',
                  background: isDarkMode ? 'rgba(255,255,255,0.5)' : 'rgba(0,0,0,0.5)',
                },
              }}
            />
          </motion.div>
        </motion.div>
      </Box>

      {/* Main Content Area */}
      <Box
        sx={{
          width: { xs: '100%', lg: 'calc(100% - 600px)' },
          transition: 'width 0.3s ease',
        }}
      >
        {/* Sectors Section */}
        <SectorsSection />

      {/* Animated Stats Section */}
      <Box
        sx={{
          py: { xs: 8, md: 12 },
          background: 'transparent',
          position: 'relative',
          zIndex: 1,
        }}
      >
        <Container maxWidth="lg">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.3 }}
            variants={staggerContainer}
          >
            <motion.div variants={fadeInUp}>
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
                By The Numbers
              </Typography>
            </motion.div>

            <Grid container spacing={4}>
              {stats.map((stat, index) => (
                <Grid item xs={6} md={3} key={index}>
                  <motion.div
                    variants={scaleIn}
                    whileHover={{ 
                      scale: 1.1,
                      y: -10,
                      transition: { duration: 0.3 }
                    }}
                  >
                    <Card
                      sx={{
                        height: '100%',
                        background: isDarkMode
                          ? `linear-gradient(145deg, rgba(30, 41, 59, 0.9) 0%, rgba(51, 65, 85, 0.7) 100%)`
                          : `linear-gradient(145deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.9) 100%)`,
                        border: '1px solid',
                        borderColor: 'divider',
                        borderRadius: 4,
                        p: 4,
                        textAlign: 'center',
                        position: 'relative',
                        overflow: 'hidden',
                        '&::before': {
                          content: '""',
                          position: 'absolute',
                          top: 0,
                          left: 0,
                          right: 0,
                          height: '4px',
                          background: `linear-gradient(135deg, ${stat.color} 0%, ${stat.color}dd 100%)`,
                        },
                        '&:hover': {
                          boxShadow: `0 20px 60px ${stat.color}40`,
                        },
                      }}
                    >
                      <motion.div
                        animate={{ 
                          rotate: [0, 360],
                        }}
                        transition={{ 
                          duration: 20,
                          repeat: Infinity,
                          ease: 'linear'
                        }}
                      >
                        <Box sx={{ color: stat.color, mb: 2, display: 'flex', justifyContent: 'center' }}>
                          {stat.icon}
                        </Box>
                      </motion.div>
                      <Typography
                        variant="h3"
                        sx={{
                          fontWeight: 800,
                          mb: 1,
                          background: `linear-gradient(135deg, ${stat.color} 0%, ${stat.color}dd 100%)`,
                          backgroundClip: 'text',
                          WebkitBackgroundClip: 'text',
                          WebkitTextFillColor: 'transparent',
                        }}
                      >
                        <AnimatedCounter end={stat.value} suffix={stat.suffix} />
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
                        {stat.label}
                      </Typography>
                    </Card>
                  </motion.div>
                </Grid>
              ))}
            </Grid>
          </motion.div>
        </Container>
      </Box>

      {/* Latest Backtest Showcase */}
      <LatestBacktestShowcase />
      </Box>

      {/* News Feed Sidebar - Fixed on Right Side */}
      <Box
        sx={{
          position: 'fixed',
          top: { xs: 0, lg: 64 },
          right: 0,
          width: { xs: '100%', lg: '580px' },
          height: { xs: '100vh', lg: 'calc(100vh - 64px)' },
          overflowY: 'auto',
          zIndex: 50,
          background: 'transparent',
          backdropFilter: 'blur(40px)',
          borderLeft: { xs: 'none', lg: 'none' },
          boxShadow: { xs: 'none', lg: 'none' },
          px: { xs: 2, lg: 4 },
          py: { xs: 4, lg: 5 },
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: isDarkMode
              ? 'linear-gradient(90deg, transparent 0%, rgba(15, 23, 42, 0.3) 50%, rgba(30, 41, 59, 0.4) 100%)'
              : 'linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.3) 50%, rgba(248, 250, 252, 0.4) 100%)',
            pointerEvents: 'none',
            zIndex: 0,
          },
          '&::after': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            width: '1px',
            height: '100%',
            background: isDarkMode
              ? 'linear-gradient(180deg, transparent 0%, rgba(148, 163, 184, 0.08) 20%, rgba(148, 163, 184, 0.12) 50%, rgba(148, 163, 184, 0.08) 80%, transparent 100%)'
              : 'linear-gradient(180deg, transparent 0%, rgba(148, 163, 184, 0.12) 20%, rgba(148, 163, 184, 0.18) 50%, rgba(148, 163, 184, 0.12) 80%, transparent 100%)',
            pointerEvents: 'none',
            zIndex: 1,
          },
          '& > *': {
            position: 'relative',
            zIndex: 2,
          },
          '&::-webkit-scrollbar': {
            width: '4px',
          },
          '&::-webkit-scrollbar-track': {
            background: 'transparent',
          },
          '&::-webkit-scrollbar-thumb': {
            background: isDarkMode 
              ? 'linear-gradient(180deg, rgba(148, 163, 184, 0.2) 0%, rgba(148, 163, 184, 0.15) 100%)'
              : 'linear-gradient(180deg, rgba(148, 163, 184, 0.15) 0%, rgba(148, 163, 184, 0.1) 100%)',
            borderRadius: '2px',
            border: 'none',
            '&:hover': {
              background: isDarkMode 
                ? 'linear-gradient(180deg, rgba(148, 163, 184, 0.3) 0%, rgba(148, 163, 184, 0.25) 100%)'
                : 'linear-gradient(180deg, rgba(148, 163, 184, 0.25) 0%, rgba(148, 163, 184, 0.2) 100%)',
            },
          },
        }}
      >
        <motion.div
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
        >
          <Box sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
              <ArticleIcon sx={{ fontSize: 28, color: 'primary.main' }} />
              <Typography variant="h5" sx={{ fontWeight: 700 }}>
                Real-Time News
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Live feed from GameCore-12 universe with AI sentiment analysis
            </Typography>
          </Box>
          <NewsFeed
            universeName="GameCore-12 (GC-12)"
            pollingInterval={30000} // 30 seconds
            maxItems={10}
          />
        </motion.div>
      </Box>

      {/* Project Description Section */}
      <Box
        sx={{
          py: { xs: 8, md: 12 },
          background: 'transparent',
          position: 'relative',
          zIndex: 1,
        }}
      >
        <Container maxWidth="lg">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.2 }}
            variants={staggerContainer}
          >
            <motion.div variants={fadeInUp}>
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
                  variants={scaleIn}
                  whileHover={{ y: -10, transition: { duration: 0.3 } }}
                >
                  <Card
                    sx={{
                      height: '100%',
                      background: isDarkMode
                        ? 'linear-gradient(145deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.85) 100%)'
                        : 'linear-gradient(145deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.95) 100%)',
                      backdropFilter: 'blur(20px)',
                      border: '1px solid',
                      borderColor: 'divider',
                      boxShadow: '0 20px 60px rgba(0, 0, 0, 0.2)',
                      borderRadius: 4,
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        boxShadow: '0 30px 80px rgba(37, 99, 235, 0.3)',
                      },
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
                  variants={scaleIn}
                  whileHover={{ y: -10, transition: { duration: 0.3 } }}
                >
                  <Card
                    sx={{
                      height: '100%',
                      background: isDarkMode
                        ? 'linear-gradient(145deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.85) 100%)'
                        : 'linear-gradient(145deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.95) 100%)',
                      backdropFilter: 'blur(20px)',
                      border: '1px solid',
                      borderColor: 'divider',
                      boxShadow: '0 20px 60px rgba(0, 0, 0, 0.2)',
                      borderRadius: 4,
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        boxShadow: '0 30px 80px rgba(139, 92, 246, 0.3)',
                      },
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
          </motion.div>
        </Container>
      </Box>

      {/* Value Propositions with Floating Cards */}
      <Box sx={{ py: { xs: 8, md: 12 }, background: 'transparent', position: 'relative', zIndex: 1 }}>
        <Container maxWidth="lg">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.2 }}
            variants={staggerContainer}
          >
            <motion.div variants={fadeInUp}>
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
                    variants={scaleIn}
                    whileHover={{ 
                      y: -15,
                      scale: 1.05,
                      transition: { duration: 0.3 }
                    }}
                    style={{ height: '100%' }}
                  >
                    <Card
                      sx={{
                        height: '100%',
                        background: isDarkMode
                          ? 'linear-gradient(145deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.85) 100%)'
                          : 'linear-gradient(145deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.95) 100%)',
                        backdropFilter: 'blur(20px)',
                        border: '1px solid',
                        borderColor: 'divider',
                        borderRadius: 4,
                        transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                        position: 'relative',
                        overflow: 'hidden',
                        '&::before': {
                          content: '""',
                          position: 'absolute',
                          top: 0,
                          left: 0,
                          right: 0,
                          bottom: 0,
                          background: prop.gradient,
                          opacity: 0,
                          transition: 'opacity 0.4s ease',
                          zIndex: 0,
                        },
                        '&:hover': {
                          boxShadow: `0 30px 80px ${prop.gradient.replace('gradient', 'rgba').split(' ')[0]}40`,
                          transform: 'translateY(-10px)',
                          '&::before': {
                            opacity: 0.1,
                          },
                        },
                      }}
                    >
                      <CardContent sx={{ p: 4, textAlign: 'center', position: 'relative', zIndex: 1 }}>
                        <motion.div
                          animate={{ 
                            y: [0, -10, 0],
                          }}
                          transition={{ 
                            duration: 2 + index * 0.3,
                            repeat: Infinity,
                            ease: 'easeInOut',
                            delay: index * 0.2,
                          }}
                        >
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
                              boxShadow: `0 10px 30px ${prop.gradient.split(' ')[0]}40`,
                            }}
                          >
                            {prop.icon}
                          </Box>
                        </motion.div>
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
          </motion.div>
        </Container>
      </Box>

      {/* YouTube Video Section */}
      <Box
        sx={{
          py: { xs: 8, md: 12 },
          background: 'transparent',
          position: 'relative',
          zIndex: 1,
        }}
      >
        <Container maxWidth="lg">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.3 }}
            variants={staggerContainer}
          >
            <motion.div variants={fadeInUp}>
              <Box sx={{ textAlign: 'center', mb: 6 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 3 }}>
                  <motion.div
                    animate={{ 
                      scale: [1, 1.2, 1],
                    }}
                    transition={{ 
                      duration: 2,
                      repeat: Infinity,
                      ease: 'easeInOut'
                    }}
                  >
                    <YouTubeIcon sx={{ fontSize: 48, color: 'error.main', mr: 2 }} />
                  </motion.div>
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
              variants={scaleIn}
              whileHover={{ scale: 1.02 }}
            >
              <Box
                sx={{
                  position: 'relative',
                  paddingBottom: '56.25%',
                  height: 0,
                  overflow: 'hidden',
                  borderRadius: 4,
                  boxShadow: '0 30px 80px rgba(0, 0, 0, 0.4)',
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
          </motion.div>
        </Container>
      </Box>

      {/* What's Coming Section */}
      <Box sx={{ py: { xs: 8, md: 12 }, background: 'transparent', position: 'relative', zIndex: 1 }}>
        <Container maxWidth="lg">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.2 }}
            variants={staggerContainer}
          >
            <motion.div variants={fadeInUp}>
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
                    variants={scaleIn}
                    whileHover={{ 
                      y: -10,
                      scale: 1.03,
                      transition: { duration: 0.3 }
                    }}
                  >
                    <Card
                      sx={{
                        height: '100%',
                        background: isDarkMode
                          ? 'linear-gradient(145deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.85) 100%)'
                          : 'linear-gradient(145deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.95) 100%)',
                        backdropFilter: 'blur(20px)',
                        border: '1px solid',
                        borderColor: 'divider',
                        position: 'relative',
                        overflow: 'hidden',
                        borderRadius: 4,
                        '&::before': {
                          content: '""',
                          position: 'absolute',
                          top: 0,
                          left: 0,
                          right: 0,
                          height: '4px',
                          background: 'linear-gradient(135deg, #2563eb 0%, #8b5cf6 100%)',
                        },
                        transition: 'all 0.3s ease',
                        '&:hover': {
                          boxShadow: '0 30px 80px rgba(37, 99, 235, 0.3)',
                        },
                      }}
                    >
                      <CardContent sx={{ p: 4 }}>
                        <Box sx={{ mb: 3 }}>
                          <motion.div
                            whileHover={{ rotate: 360 }}
                            transition={{ duration: 0.6 }}
                          >
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
                          </motion.div>
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
          </motion.div>
        </Container>
      </Box>

      {/* Newsletter & Contact Section */}
      <Box
        sx={{
          py: { xs: 8, md: 12 },
          background: 'transparent',
          position: 'relative',
          zIndex: 1,
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={6}>
            <Grid item xs={12} md={6}>
              <motion.div
                initial={{ opacity: 0, x: -50 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.8 }}
                whileHover={{ y: -5 }}
              >
                <Card
                  sx={{
                    height: '100%',
                    background: isDarkMode
                      ? 'linear-gradient(145deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.85) 100%)'
                      : 'linear-gradient(145deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.95) 100%)',
                    backdropFilter: 'blur(20px)',
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 4,
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

            <Grid item xs={12} md={6}>
              <motion.div
                initial={{ opacity: 0, x: 50 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.8 }}
                whileHover={{ y: -5 }}
              >
                <Card
                  sx={{
                    height: '100%',
                    background: isDarkMode
                      ? 'linear-gradient(145deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.85) 100%)'
                      : 'linear-gradient(145deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.95) 100%)',
                    backdropFilter: 'blur(20px)',
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 4,
                  }}
                >
                  <CardContent sx={{ p: 4 }}>
                    <Typography variant="h4" sx={{ fontWeight: 700, mb: 4 }}>
                      Get In Touch
                    </Typography>

                    <Box sx={{ mb: 4 }}>
                      <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
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
                      </motion.div>
                      <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center' }}>
                        Connect with the community, ask questions, and stay updated
                      </Typography>
                    </Box>

                    <Divider sx={{ my: 3 }} />

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
          background: 'transparent',
          position: 'relative',
          zIndex: 1,
        }}
      >
        <Container maxWidth="md">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <Paper
              elevation={0}
              sx={{
                p: { xs: 4, md: 6 },
                textAlign: 'center',
                background: isDarkMode
                  ? 'linear-gradient(145deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.85) 100%)'
                  : 'linear-gradient(145deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.95) 100%)',
                backdropFilter: 'blur(20px)',
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 4,
                position: 'relative',
                overflow: 'hidden',
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  background: 'linear-gradient(135deg, rgba(37, 99, 235, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%)',
                  opacity: 0,
                  transition: 'opacity 0.3s ease',
                },
                '&:hover::before': {
                  opacity: 1,
                },
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
              <motion.div 
                whileHover={{ scale: 1.05, y: -2 }} 
                whileTap={{ scale: 0.95 }}
              >
                <Button
                  variant="contained"
                  size="large"
                  endIcon={<PlayArrowIcon />}
                  onClick={() => navigate('/backtest')}
                  sx={{
                    px: 6,
                    py: 2.5,
                    fontSize: '1.2rem',
                    fontWeight: 600,
                    background: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)',
                    boxShadow: '0 20px 40px rgba(37, 99, 235, 0.4)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%)',
                      boxShadow: '0 25px 50px rgba(37, 99, 235, 0.6)',
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
