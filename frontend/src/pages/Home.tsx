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
  IconButton,
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
  ArrowForward as ArrowForwardIcon,
  Send as SendIcon,
  ContactMail as ContactMailIcon,
  AutoGraph as AutoGraphIcon,
  Calculate as CalculateIcon,
  Assessment as AssessmentIcon,
  ShowChart as ShowChartIcon,
  Security as SecurityIcon,
  Bolt as BoltIcon,
  CalendarToday as CalendarTodayIcon,
  Timeline as TimelineIcon,
} from '@mui/icons-material';
import { motion, useInView } from 'framer-motion';
import { format, parseISO } from 'date-fns';
import AnimatedBackground from '@/components/common/AnimatedBackground';
import GradientMesh from '@/components/common/GradientMesh';
import { useTheme } from '@/contexts/ThemeContext';
import { backtestApi, newsApi } from '@/services/api';
import SectorsSection from '@/components/sectors/SectorsSection';
import {
  TrendingDown as TrendingDownIcon,
  Remove as RemoveIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  RadioButtonChecked as RadioButtonCheckedIcon,
} from '@mui/icons-material';

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

// Live News Preview Component
const LiveNewsPreview: React.FC = () => {
  const navigate = useNavigate();
  const { isDarkMode } = useTheme();
  const [currentIndex, setCurrentIndex] = useState(0);

  // Fetch recent news for GameCore-12 universe
  const { data: newsData, isLoading: newsLoading } = useQuery(
    'home-news-preview',
    () => newsApi.getUniverseNews('GameCore-12 (GC-12)', 6),
    {
      staleTime: 2 * 60 * 1000, // 2 minutes
      refetchOnWindowFocus: false,
    }
  );

  const formatNewsDate = (dateStr: string) => {
    try {
      const date = parseISO(dateStr);
      const now = new Date();
      const diffMinutes = (now.getTime() - date.getTime()) / (1000 * 60);

      if (diffMinutes < 60) {
        return `${Math.floor(diffMinutes)}m ago`;
      } else if (diffMinutes < 1440) {
        return `${Math.floor(diffMinutes / 60)}h ago`;
      } else {
        return format(date, 'MMM dd');
      }
    } catch {
      return dateStr;
    }
  };

  const getSentimentStyle = (label: string) => {
    switch (label) {
      case 'positive':
        return {
          color: '#10b981',
          bgColor: isDarkMode ? 'rgba(16, 185, 129, 0.15)' : 'rgba(16, 185, 129, 0.1)',
          icon: <TrendingUpIcon sx={{ fontSize: 16 }} />,
        };
      case 'negative':
        return {
          color: '#ef4444',
          bgColor: isDarkMode ? 'rgba(239, 68, 68, 0.15)' : 'rgba(239, 68, 68, 0.1)',
          icon: <TrendingDownIcon sx={{ fontSize: 16 }} />,
        };
      default:
        return {
          color: '#6b7280',
          bgColor: isDarkMode ? 'rgba(107, 114, 128, 0.15)' : 'rgba(107, 114, 128, 0.1)',
          icon: <RemoveIcon sx={{ fontSize: 16 }} />,
        };
    }
  };

  const previewNews = newsData?.news || []; // Show all 6 items
  const visibleItems = 3; // Number of items visible at once (always show 3)
  // Ensure we have at least 3 items for display
  const displayNews = previewNews.length >= 3 ? previewNews : [];
  const maxIndex = Math.max(0, displayNews.length - visibleItems);
  const canGoPrevious = currentIndex > 0;
  const canGoNext = currentIndex < maxIndex && displayNews.length > visibleItems;
  const scrollContainerRef = React.useRef<HTMLDivElement>(null);

  const handlePrevious = () => {
    if (scrollContainerRef.current && currentIndex > 0) {
      const container = scrollContainerRef.current;
      const cards = container.querySelectorAll('[data-card-index]');
      if (cards.length > 0) {
        const firstCard = cards[0] as HTMLElement;
        const cardWidth = firstCard.offsetWidth;
        const gap = 24; // gap-3 = 24px
        
        const newIndex = Math.max(0, currentIndex - 1);
        setCurrentIndex(newIndex);
        
        // Scroll to show exactly visibleItems cards
        const targetScroll = newIndex * (cardWidth + gap);
        container.scrollTo({
          left: targetScroll,
          behavior: 'smooth',
        });
      }
    }
  };

  const handleNext = () => {
    if (scrollContainerRef.current && currentIndex < maxIndex) {
      const container = scrollContainerRef.current;
      const cards = container.querySelectorAll('[data-card-index]');
      if (cards.length > 0) {
        const firstCard = cards[0] as HTMLElement;
        const cardWidth = firstCard.offsetWidth;
        const gap = 24; // gap-3 = 24px
        
        const newIndex = Math.min(maxIndex, currentIndex + 1);
        setCurrentIndex(newIndex);
        
        // Scroll to show exactly visibleItems cards
        const targetScroll = newIndex * (cardWidth + gap);
        container.scrollTo({
          left: targetScroll,
          behavior: 'smooth',
        });
      }
    }
  };

  // Reset index when news data changes
  React.useEffect(() => {
    if (newsData?.news && newsData.news.length >= 3) {
      setCurrentIndex(0);
      if (scrollContainerRef.current) {
        scrollContainerRef.current.scrollTo({ left: 0, behavior: 'instant' });
      }
    }
  }, [newsData?.news?.length]);

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
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 2, mb: 2, flexWrap: 'wrap' }}>
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
                          Live News Data Analysis
                        </Typography>
                        {/* Breathing/Pulsing Real-time Indicator */}
                        <motion.div
                          animate={{
                            scale: [1, 1.3, 1],
                            opacity: [0.6, 1, 0.6],
                          }}
                          transition={{
                            duration: 2,
                            repeat: Infinity,
                            ease: 'easeInOut',
                          }}
                        >
                          <RadioButtonCheckedIcon
                            sx={{
                              fontSize: 16,
                              color: '#10b981',
                            }}
                          />
                        </motion.div>
                      </Box>
              <Typography variant="h6" color="text.secondary" sx={{ maxWidth: 700, mx: 'auto' }}>
                Real-time data analysis of market news with AI-powered sentiment insights
              </Typography>
            </Box>
          </motion.div>

          {/* News Preview Cards with Carousel */}
          <Box 
            sx={{ 
              position: 'relative', 
              mb: 4,
              // Fix shadow artifacts but don't clip arrows
              // Use padding instead of overflow hidden to allow arrows to show
              px: { xs: 2, md: 3 },
              // Ensure arrows are never clipped
              overflow: 'visible',
            }}
          >
            {/* Left Arrow */}
            {!newsLoading && displayNews.length > visibleItems && (
              <IconButton
                onClick={handlePrevious}
                disabled={!canGoPrevious}
                sx={{
                  position: 'absolute',
                  left: { xs: -8, md: -16 },
                  top: '50%',
                  transform: 'translateY(-50%)',
                  zIndex: 10,
                  background: isDarkMode
                    ? 'rgba(30, 41, 59, 0.9)'
                    : 'rgba(255, 255, 255, 0.9)',
                  backdropFilter: 'blur(10px)',
                  border: '1px solid',
                  borderColor: 'divider',
                  opacity: canGoPrevious ? 1 : 0.3,
                  cursor: canGoPrevious ? 'pointer' : 'not-allowed',
                  '&:hover': canGoPrevious ? {
                    background: isDarkMode
                      ? 'rgba(30, 41, 59, 1)'
                      : 'rgba(255, 255, 255, 1)',
                    transform: 'translateY(-50%) scale(1.1)',
                  } : {},
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
                }}
              >
                <ChevronLeftIcon />
              </IconButton>
            )}

            {/* Scrollable News Cards Container */}
            <Box
              ref={scrollContainerRef}
              sx={{
                display: 'flex',
                gap: 3,
                overflowX: 'auto',
                overflowY: 'visible',
                scrollBehavior: 'smooth',
                position: 'relative',
                scrollSnapType: 'x proximity',
                // Ensure container shows exactly 3 cards on desktop
                width: '100%',
                maxWidth: '100%',
                // Prevent shadow bleeding while allowing arrows
                '& > *': {
                  flexShrink: 0,
                },
                // Fix shadow artifacts by ensuring clean clipping
                isolation: 'isolate',
                transform: 'translateZ(0)', // Force hardware acceleration
                willChange: 'scroll-position',
                // Hide scrollbar
                '&::-webkit-scrollbar': {
                  display: 'none',
                },
                scrollbarWidth: 'none',
                msOverflowStyle: 'none',
              }}
            >
              {newsLoading || displayNews.length < 3 ? (
                // Loading Skeleton - show 3 skeleton cards (always show during loading or when data is insufficient)
                <>
                  {[1, 2, 3].map((idx) => (
                    <Card
                      key={`skeleton-${idx}`}
                      sx={{
                        width: { xs: 'calc(100% - 24px)', md: 'calc((100% - 48px) / 3)' },
                        minWidth: { xs: 'calc(100% - 24px)', md: 'calc((100% - 48px) / 3)' },
                        maxWidth: { xs: 'calc(100% - 24px)', md: 'calc((100% - 48px) / 3)' },
                        flexShrink: 0,
                        height: '100%',
                        background: isDarkMode
                          ? 'linear-gradient(145deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.85) 100%)'
                          : 'linear-gradient(145deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.95) 100%)',
                        backdropFilter: 'blur(20px)',
                        border: '1px solid',
                        borderColor: 'divider',
                        borderRadius: 1, // Minimal border radius
                        boxShadow: 'none',
                      }}
                    >
                      <CardContent sx={{ p: 3 }}>
                        <Box sx={{ mb: 2, borderRadius: 1, overflow: 'hidden', width: '100%', height: '120px', bgcolor: isDarkMode ? 'rgba(148, 163, 184, 0.1)' : 'rgba(148, 163, 184, 0.05)' }}>
                          <Box sx={{ width: '100%', height: '100%', bgcolor: isDarkMode ? 'rgba(148, 163, 184, 0.1)' : 'rgba(148, 163, 184, 0.05)' }} />
                        </Box>
                        <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                          <Box sx={{ width: 60, height: 24, borderRadius: 1, bgcolor: isDarkMode ? 'rgba(148, 163, 184, 0.1)' : 'rgba(148, 163, 184, 0.05)' }} />
                          <Box sx={{ width: 80, height: 24, borderRadius: 1, bgcolor: isDarkMode ? 'rgba(148, 163, 184, 0.1)' : 'rgba(148, 163, 184, 0.05)' }} />
                        </Box>
                        <Box sx={{ mb: 1.5 }}>
                          <Box sx={{ width: '90%', height: 20, borderRadius: 1, bgcolor: isDarkMode ? 'rgba(148, 163, 184, 0.1)' : 'rgba(148, 163, 184, 0.05)', mb: 1 }} />
                          <Box sx={{ width: '70%', height: 20, borderRadius: 1, bgcolor: isDarkMode ? 'rgba(148, 163, 184, 0.1)' : 'rgba(148, 163, 184, 0.05)' }} />
                        </Box>
                        <Box sx={{ mb: 2 }}>
                          <Box sx={{ width: '100%', height: 16, borderRadius: 1, bgcolor: isDarkMode ? 'rgba(148, 163, 184, 0.1)' : 'rgba(148, 163, 184, 0.05)', mb: 0.5 }} />
                          <Box sx={{ width: '85%', height: 16, borderRadius: 1, bgcolor: isDarkMode ? 'rgba(148, 163, 184, 0.1)' : 'rgba(148, 163, 184, 0.05)' }} />
                        </Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
                          <Box sx={{ width: 60, height: 12, borderRadius: 1, bgcolor: isDarkMode ? 'rgba(148, 163, 184, 0.1)' : 'rgba(148, 163, 184, 0.05)' }} />
                          <Box sx={{ width: 80, height: 12, borderRadius: 1, bgcolor: isDarkMode ? 'rgba(148, 163, 184, 0.1)' : 'rgba(148, 163, 184, 0.05)' }} />
                        </Box>
                      </CardContent>
                    </Card>
                  ))}
                </>
              ) : displayNews.length >= 3 ? (
                // Actual News Cards - show all pre-loaded (at least 3)
                displayNews.map((item: any, index: number) => {
                  const sentimentStyle = getSentimentStyle(item.sentiment.label);
                  return (
                    <Card
                      key={`${item.ticker}-${item.pub_date}-${index}`}
                      data-card-index={index}
                      component={motion.div}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.4, delay: index * 0.1 }}
                      sx={{
                        width: { xs: 'calc(100% - 24px)', md: 'calc((100% - 48px) / 3)' },
                        minWidth: { xs: 'calc(100% - 24px)', md: 'calc((100% - 48px) / 3)' },
                        maxWidth: { xs: 'calc(100% - 24px)', md: 'calc((100% - 48px) / 3)' },
                        flexShrink: 0,
                        height: '100%',
                        background: isDarkMode
                          ? 'linear-gradient(145deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.85) 100%)'
                          : 'linear-gradient(145deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.95) 100%)',
                        backdropFilter: 'blur(20px)',
                        border: '1px solid',
                        borderColor: 'divider',
                        borderRadius: 1, // Minimal border radius
                        overflow: 'hidden',
                        position: 'relative',
                        transition: 'all 0.3s ease',
                        '&::before': {
                          content: '""',
                          position: 'absolute',
                          left: 0,
                          top: 0,
                          bottom: 0,
                          width: '4px',
                          background: sentimentStyle.color,
                          opacity: 0.6,
                        },
                        '&:hover': {
                          boxShadow: `0 8px 24px ${sentimentStyle.color}20`,
                          transform: 'translateY(-5px)',
                        },
                      }}
                    >
                      <CardContent sx={{ p: 3 }}>
                        {/* Image */}
                        {item.image_url && (
                          <Box
                            sx={{
                              mb: 2,
                              borderRadius: 1, // Minimal border radius
                              overflow: 'hidden',
                              width: '100%',
                              height: '120px',
                              backgroundColor: isDarkMode ? 'rgba(30, 41, 59, 0.3)' : 'rgba(248, 250, 252, 0.5)',
                              position: 'relative',
                              '& img': {
                                width: '100%',
                                height: '100%',
                                objectFit: 'cover',
                              },
                            }}
                          >
                            <img
                              src={item.image_url}
                              alt={item.title}
                              onError={(e) => {
                                const target = e.target as HTMLImageElement;
                                target.style.display = 'none';
                              }}
                            />
                          </Box>
                        )}

                        {/* Header */}
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2, flexWrap: 'wrap', gap: 1 }}>
                          <Chip
                            label={item.ticker}
                            size="small"
                            sx={{
                              fontWeight: 600,
                              fontSize: '0.75rem',
                              background: isDarkMode
                                ? 'rgba(37, 99, 235, 0.2)'
                                : 'rgba(37, 99, 235, 0.1)',
                              border: '1px solid',
                              borderColor: 'primary.main',
                            }}
                          />
                          <Chip
                            icon={sentimentStyle.icon}
                            label={item.sentiment.label_display}
                            size="small"
                            sx={{
                              fontSize: '0.75rem',
                              color: sentimentStyle.color,
                              background: sentimentStyle.bgColor,
                              border: '1px solid',
                              borderColor: sentimentStyle.color + '40',
                              fontWeight: 500,
                            }}
                          />
                        </Box>

                        {/* Title */}
                        <Typography
                          variant="h6"
                          sx={{
                            fontWeight: 600,
                            mb: 1.5,
                            lineHeight: 1.4,
                            fontSize: '1rem',
                            display: '-webkit-box',
                            WebkitLineClamp: 2,
                            WebkitBoxOrient: 'vertical',
                            overflow: 'hidden',
                          }}
                        >
                          {item.title || item.summary?.substring(0, 100) || 'News Article'}
                        </Typography>

                        {/* Summary */}
                        {item.summary && (
                          <Typography
                            variant="body2"
                            color="text.secondary"
                            sx={{
                              mb: 2,
                              lineHeight: 1.6,
                              fontSize: '0.875rem',
                              display: '-webkit-box',
                              WebkitLineClamp: 2,
                              WebkitBoxOrient: 'vertical',
                              overflow: 'hidden',
                            }}
                          >
                            {item.summary}
                          </Typography>
                        )}

                        {/* Footer */}
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mt: 'auto', pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
                          <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                            {formatNewsDate(item.pub_date)}
                          </Typography>
                          <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                            {item.publisher || 'News Source'}
                          </Typography>
                        </Box>
                      </CardContent>
                    </Card>
                  );
                })
              ) : null}
            </Box>

            {/* Right Arrow */}
            {!newsLoading && displayNews.length > visibleItems && (
              <IconButton
                onClick={handleNext}
                disabled={!canGoNext}
                sx={{
                  position: 'absolute',
                  right: { xs: -8, md: -16 },
                  top: '50%',
                  transform: 'translateY(-50%)',
                  zIndex: 10,
                  background: isDarkMode
                    ? 'rgba(30, 41, 59, 0.9)'
                    : 'rgba(255, 255, 255, 0.9)',
                  backdropFilter: 'blur(10px)',
                  border: '1px solid',
                  borderColor: 'divider',
                  opacity: canGoNext ? 1 : 0.3,
                  cursor: canGoNext ? 'pointer' : 'not-allowed',
                  '&:hover': canGoNext ? {
                    background: isDarkMode
                      ? 'rgba(30, 41, 59, 1)'
                      : 'rgba(255, 255, 255, 1)',
                    transform: 'translateY(-50%) scale(1.1)',
                  } : {},
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
                }}
              >
                <ChevronRightIcon />
              </IconButton>
            )}
          </Box>

          {/* CTA Button */}
          {!newsLoading && displayNews.length >= 3 && (
            <motion.div variants={fadeInUp}>
              <Box sx={{ textAlign: 'center' }}>
                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <Button
                    variant="contained"
                    size="large"
                    endIcon={<ArrowForwardIcon />}
                    onClick={() => navigate('/news-deep-dive')}
                    sx={{
                      px: 5,
                      py: 2,
                      fontSize: '1.1rem',
                      fontWeight: 600,
                      background: 'linear-gradient(135deg, #2563eb 0%, #8b5cf6 100%)',
                      boxShadow: '0 20px 40px rgba(37, 99, 235, 0.4)',
                      '&:hover': {
                        background: 'linear-gradient(135deg, #1d4ed8 0%, #7c3aed 100%)',
                        boxShadow: '0 25px 50px rgba(37, 99, 235, 0.5)',
                        transform: 'translateY(-2px)',
                      },
                    }}
                  >
                    Explore Full News Analysis
                  </Button>
                </motion.div>
              </Box>
            </motion.div>
          )}
        </motion.div>
      </Container>
    </Box>
  );
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
  const { data: metricsData, isLoading: metricsLoading, isFetching: metricsFetching } = useQuery(
    ['backtest-metrics', runId],
    () => backtestApi.getBacktestMetrics(runId!),
    {
      enabled: !!runId,
      staleTime: 5 * 60 * 1000,
      refetchOnWindowFocus: false,
    }
  );

  // Show skeleton if:
  // 1. Backtests are loading, OR
  // 2. We have a runId but metrics are loading/fetching, OR
  // 3. We have a backtest but no metrics data yet (waiting for metrics to load)
  // Use isFetching as primary check since it's more reliable for detecting active queries
  const isLoading = backtestsLoading 
    || (!!runId && (metricsLoading || metricsFetching)) 
    || (!!latestBacktest && runId && !metricsData);
  
  // Show content only when we have both backtest and metrics data
  // Ensure metricsData exists and is a valid object
  const hasData = !!latestBacktest && !!metricsData;

  const metrics = metricsData || undefined;
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

          {isLoading ? (
            // Loading Skeleton for Backtest
            <Card
              sx={{
                background: isDarkMode
                  ? 'linear-gradient(145deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.85) 100%)'
                  : 'linear-gradient(145deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.95) 100%)',
                backdropFilter: 'blur(20px)',
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 1, // Minimal border radius
                overflow: 'hidden',
                position: 'relative',
              }}
            >
              <CardContent sx={{ p: { xs: 4, md: 6 } }}>
                {/* Header Skeleton */}
                <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, justifyContent: 'space-between', alignItems: { xs: 'flex-start', md: 'center' }, mb: 4 }}>
                  <Box sx={{ flex: 1 }}>
                    <Box sx={{ mb: 1, width: '60%', height: 32, borderRadius: 1, bgcolor: isDarkMode ? 'rgba(148, 163, 184, 0.1)' : 'rgba(148, 163, 184, 0.05)' }} />
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap', mt: 1 }}>
                      <Box sx={{ width: 200, height: 20, borderRadius: 1, bgcolor: isDarkMode ? 'rgba(148, 163, 184, 0.1)' : 'rgba(148, 163, 184, 0.05)' }} />
                      <Box sx={{ width: 100, height: 24, borderRadius: 1, bgcolor: isDarkMode ? 'rgba(148, 163, 184, 0.1)' : 'rgba(148, 163, 184, 0.05)' }} />
                    </Box>
                  </Box>
                  <Box sx={{ mt: { xs: 2, md: 0 }, width: 140, height: 40, borderRadius: 1, bgcolor: isDarkMode ? 'rgba(148, 163, 184, 0.1)' : 'rgba(148, 163, 184, 0.05)' }} />
                </Box>

                {/* Metrics Grid Skeleton */}
                <Grid container spacing={3} sx={{ mb: 4 }} justifyContent="center">
                  {[1, 2, 3, 4].map((idx) => (
                    <Grid item xs={6} sm={4} md={3} key={idx}>
                      <Card
                        sx={{
                          background: isDarkMode
                            ? 'rgba(148, 163, 184, 0.05)'
                            : 'rgba(148, 163, 184, 0.02)',
                          border: '1px solid',
                          borderColor: 'divider',
                          borderRadius: 1, // Minimal border radius
                          p: 2,
                          textAlign: 'center',
                        }}
                      >
                        <Box sx={{ mb: 1, width: '70%', mx: 'auto', height: 16, borderRadius: 1, bgcolor: isDarkMode ? 'rgba(148, 163, 184, 0.1)' : 'rgba(148, 163, 184, 0.05)' }} />
                        <Box sx={{ width: '50%', mx: 'auto', height: 28, borderRadius: 1, bgcolor: isDarkMode ? 'rgba(148, 163, 184, 0.1)' : 'rgba(148, 163, 184, 0.05)' }} />
                      </Card>
                    </Grid>
                  ))}
                </Grid>

                {/* Additional Metrics Skeleton */}
                <Grid container spacing={2}>
                  {[1, 2, 3].map((idx) => (
                    <Grid item xs={6} sm={4} key={idx}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Box sx={{ width: 20, height: 20, borderRadius: 1, bgcolor: isDarkMode ? 'rgba(148, 163, 184, 0.1)' : 'rgba(148, 163, 184, 0.05)' }} />
                        <Box sx={{ width: '80%', height: 16, borderRadius: 1, bgcolor: isDarkMode ? 'rgba(148, 163, 184, 0.1)' : 'rgba(148, 163, 184, 0.05)' }} />
                      </Box>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          ) : hasData ? (
            <motion.div variants={scaleIn} whileHover={{ y: -10, transition: { duration: 0.3 } }}>
              <Card
              sx={{
                background: isDarkMode
                  ? 'linear-gradient(145deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.85) 100%)'
                  : 'linear-gradient(145deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.95) 100%)',
                backdropFilter: 'blur(20px)',
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 1, // Minimal border radius
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
                <Grid container spacing={3} sx={{ mb: 4 }} justifyContent="center">
                  <Grid item xs={6} sm={4} md={3}>
                    <motion.div whileHover={{ scale: 1.05 }}>
                      <Card
                        sx={{
                          background: isDarkMode
                            ? 'rgba(37, 99, 235, 0.1)'
                            : 'rgba(37, 99, 235, 0.05)',
                          border: '1px solid',
                          borderColor: isDarkMode ? 'rgba(37, 99, 235, 0.3)' : 'rgba(37, 99, 235, 0.2)',
                          borderRadius: 1, // Minimal border radius
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
                            color: metrics && metrics.total_return >= 0 ? 'success.main' : 'error.main',
                          }}
                        >
                          {formatPercent(metrics?.total_return || 0)}
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
                          borderRadius: 1, // Minimal border radius
                          p: 2,
                          textAlign: 'center',
                        }}
                      >
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 1, fontWeight: 500 }}>
                          Sharpe Ratio
                        </Typography>
                        <Typography variant="h5" sx={{ fontWeight: 800, color: 'success.main' }}>
                          {(metrics?.sharpe_ratio || 0).toFixed(2)}
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
                          borderRadius: 1, // Minimal border radius
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
                            color: metrics && metrics.alpha >= 0 ? 'success.main' : 'error.main',
                          }}
                        >
                          {formatPercent(metrics?.alpha || 0)}
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
                          borderRadius: 1, // Minimal border radius
                          p: 2,
                          textAlign: 'center',
                        }}
                      >
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 1, fontWeight: 500 }}>
                          Max Drawdown
                        </Typography>
                        <Typography variant="h5" sx={{ fontWeight: 800, color: 'warning.main' }}>
                          {formatPercent(metrics?.max_drawdown || 0)}
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
                        <strong>Volatility:</strong> {formatPercent(metrics?.volatility || 0)}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={4}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <TrendingUpIcon sx={{ fontSize: 20, color: 'success.main' }} />
                      <Typography variant="body2" color="text.secondary">
                        <strong>Win Rate:</strong> {formatPercent(metrics?.win_rate || 0)}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={4}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <ShowChartIcon sx={{ fontSize: 20, color: 'info.main' }} />
                      <Typography variant="body2" color="text.secondary">
                        <strong>Annualized Return:</strong> {formatPercent(metrics?.annualized_return || 0)}
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
            </motion.div>
          ) : null}
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
    <Box 
      sx={{ 
        position: 'relative', 
        overflow: 'hidden',
      }}
    >
      {/* Animated Backgrounds */}
      <GradientMesh />
      <AnimatedBackground />

      {/* Hero Section with Netflix-style Background */}
      <Box
        ref={heroRef}
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          position: 'relative',
          overflow: 'hidden',
          background: 'transparent',
          zIndex: 1,
        }}
      >
        {/* Centered Content */}
        <Container
          maxWidth="md"
          sx={{
            position: 'relative',
            zIndex: 3,
            textAlign: 'center',
            px: { xs: 3, md: 4 },
          }}
        >
          <motion.div
            initial="hidden"
            animate="visible"
            variants={staggerContainer}
          >
            <motion.div variants={fadeInUp}>
              <Typography
                variant="h1"
                sx={{
                  fontSize: { xs: '2.5rem', md: '4rem', lg: '5.5rem' },
                  fontWeight: 900,
                  mb: 3,
                  lineHeight: 1.1,
                  letterSpacing: '-0.03em',
                  color: '#ffffff',
                  textShadow: '0 2px 20px rgba(0, 0, 0, 0.5)',
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
                variant="h6"
                sx={{
                  mb: 4,
                  color: 'rgba(255, 255, 255, 0.9)',
                  fontWeight: 400,
                  lineHeight: 1.8,
                  fontSize: { xs: '1rem', md: '1.25rem' },
                  textShadow: '0 1px 10px rgba(0, 0, 0, 0.5)',
                  maxWidth: '90%',
                  mx: 'auto',
                }}
              >
                Alpha Crucible leverages <strong>AI-powered analysis of alternative data</strong> to generate
                sector-specific trading signals. We capture insights traditional financial analysis misses,
                providing you with rigorously backtested quantitative strategies validated through comprehensive testing.
              </Typography>
            </motion.div>

            <motion.div variants={fadeInUp}>
              <Box
                sx={{
                  display: 'flex',
                  gap: 2,
                  flexWrap: 'wrap',
                  justifyContent: 'center',
                  mb: 4,
                }}
              >
                <motion.div
                  whileHover={{ scale: 1.05, y: -2 }}
                  whileTap={{ scale: 0.95 }}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
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
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
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
                      borderColor: 'rgba(255, 255, 255, 0.5)',
                      color: '#ffffff',
                      backdropFilter: 'blur(10px)',
                      background: 'rgba(255, 255, 255, 0.1)',
                      '&:hover': {
                        borderWidth: 2,
                        borderColor: 'rgba(255, 255, 255, 0.8)',
                        transform: 'translateY(-2px)',
                        background: 'rgba(255, 255, 255, 0.2)',
                        boxShadow: '0 10px 30px rgba(0, 0, 0, 0.3)',
                      },
                    }}
                  >
                    Join Discord
                  </Button>
                </motion.div>
              </Box>
            </motion.div>
          </motion.div>
        </Container>

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
                borderRadius: 1, // Minimal border radius
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
          width: '100%',
          margin: '0 auto',
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

            <Grid container spacing={4} justifyContent="center">
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
                        borderRadius: 1, // Minimal border radius
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

      {/* Live News Preview */}
      <LiveNewsPreview />
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

            <Grid container spacing={6} justifyContent="center">
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
                      borderRadius: 1, // Minimal border radius
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
                      borderRadius: 1, // Minimal border radius
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

            <Grid container spacing={4} justifyContent="center">
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
                        borderRadius: 1, // Minimal border radius
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
                              borderRadius: 1, // Minimal border radius
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
                  borderRadius: 1, // Minimal border radius
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

            <Grid container spacing={4} justifyContent="center">
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
                        borderRadius: 1, // Minimal border radius
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
                                borderRadius: 1, // Minimal border radius
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
          <Grid container spacing={6} justifyContent="center">
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
                    borderRadius: 1, // Minimal border radius
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
                    borderRadius: 1, // Minimal border radius
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
                borderRadius: 1, // Minimal border radius
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
