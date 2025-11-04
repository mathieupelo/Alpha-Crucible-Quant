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
  YouTube as YouTubeIcon,
  Launch as LaunchIcon,
  ArrowForward as ArrowForwardIcon,
  Send as SendIcon,
  ContactMail as ContactMailIcon,
  AutoGraph as AutoGraphIcon,
  Calculate as CalculateIcon,
  Assessment as AssessmentIcon,
  DataObject as DataObjectIcon,
  Category as CategoryIcon,
  SmartToy as SmartToyIcon,
  Reddit as RedditIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { format, parseISO } from 'date-fns';
import AnimatedBackground from '@/components/common/AnimatedBackground';
import GradientMesh from '@/components/common/GradientMesh';
import { useTheme } from '@/contexts/ThemeContext';
import { newsApi } from '@/services/api';
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts';
import SectorsSection from '@/components/sectors/SectorsSection';
import {
  TrendingDown as TrendingDownIcon,
  Remove as RemoveIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  RadioButtonChecked as RadioButtonCheckedIcon,
} from '@mui/icons-material';

// Discord Icon Component
const DiscordIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg
    {...props}
    viewBox="0 0 24 24"
    fill="currentColor"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028c.462-.63.874-1.295 1.226-1.994a.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/>
  </svg>
);

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
                      onClick={() => navigate('/news-deep-dive')}
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
                        cursor: 'pointer',
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

// Our Signals Component
const OurSignalsSection: React.FC = () => {
  const { isDarkMode } = useTheme();
  const [redditSentiment, setRedditSentiment] = useState(0);
  const [youtubeSentiment, setYoutubeSentiment] = useState(0);
  const [googleTrends, setGoogleTrends] = useState(0);

  // Mock data
  const redditPost = {
    username: 'u/TradingPro2024',
    subreddit: 'r/wallstreetbets',
    timeAgo: '2 hours ago',
    title: 'TSLA looking bullish after the latest earnings call',
    content: 'Just analyzed the Q4 earnings and the guidance looks solid. Production numbers are up and they\'re expanding into new markets. Bullish signal here!',
    stock: 'TSLA',
    targetSentiment: 72,
  };

  const youtubeComment = {
    username: 'MarketWatcher99',
    timeAgo: '3 hours ago',
    content: 'This stock has been on fire lately! The fundamentals are solid and the technicals are pointing to continued growth. Definitely worth watching.',
    stock: 'NVDA',
    targetSentiment: 85,
  };

  const googleTrendsData = {
    keyword: 'AI Stocks',
    targetScore: 92,
    chartData: [
      { time: '00:00', value: 45 },
      { time: '04:00', value: 52 },
      { time: '08:00', value: 68 },
      { time: '12:00', value: 75 },
      { time: '16:00', value: 82 },
      { time: '20:00', value: 88 },
      { time: '24:00', value: 92 },
    ],
  };

  // Tickering animation for sentiment scores
  React.useEffect(() => {
    const duration = 3000; // 3 seconds for slow tickering
    const steps = 60;
    const interval = duration / steps;

    // Reddit sentiment animation
    let redditStep = 0;
    const redditIncrement = redditPost.targetSentiment / steps;
    const redditTimer = setInterval(() => {
      redditStep++;
      const current = Math.min(redditPost.targetSentiment, redditIncrement * redditStep);
      setRedditSentiment(Math.floor(current));
      if (redditStep >= steps) clearInterval(redditTimer);
    }, interval);

    // YouTube sentiment animation
    let youtubeStep = 0;
    const youtubeIncrement = youtubeComment.targetSentiment / steps;
    const youtubeTimer = setInterval(() => {
      youtubeStep++;
      const current = Math.min(youtubeComment.targetSentiment, youtubeIncrement * youtubeStep);
      setYoutubeSentiment(Math.floor(current));
      if (youtubeStep >= steps) clearInterval(youtubeTimer);
    }, interval);

    // Google Trends animation
    let trendsStep = 0;
    const trendsIncrement = googleTrendsData.targetScore / steps;
    const trendsTimer = setInterval(() => {
      trendsStep++;
      const current = Math.min(googleTrendsData.targetScore, trendsIncrement * trendsStep);
      setGoogleTrends(Math.floor(current));
      if (trendsStep >= steps) clearInterval(trendsTimer);
    }, interval);

    return () => {
      clearInterval(redditTimer);
      clearInterval(youtubeTimer);
      clearInterval(trendsTimer);
    };
  }, []);

  const getSentimentLabel = (score: number) => {
    if (score >= 50) return 'Positive';
    if (score <= -50) return 'Negative';
    return 'Neutral';
  };

  const getSentimentColor = (score: number) => {
    if (score >= 50) return '#10b981';
    if (score <= -50) return '#ef4444';
    return '#6b7280';
  };

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
                Our Signals
              </Typography>
              <Typography variant="h6" color="text.secondary" sx={{ maxWidth: 700, mx: 'auto' }}>
                Real-time sentiment analysis from multiple data sources
              </Typography>
            </Box>
          </motion.div>

          <Grid container spacing={3} sx={{ mt: 2 }}>
            {/* Reddit Sentiment Card */}
            <Grid item xs={12} md={4}>
              <motion.div variants={scaleIn} whileHover={{ y: -5, transition: { duration: 0.3 } }}>
                <Card
                  sx={{
                    height: '100%',
                    background: isDarkMode
                      ? 'linear-gradient(145deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.85) 100%)'
                      : 'linear-gradient(145deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.95) 100%)',
                    backdropFilter: 'blur(20px)',
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 1,
                    overflow: 'hidden',
                    position: 'relative',
                  }}
                >
                  <CardContent sx={{ p: 3 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                      <RedditIcon sx={{ color: '#ff4500', fontSize: 24 }} />
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        Reddit Sentiment
                      </Typography>
                    </Box>

                    {/* Reddit Post Card */}
                    <Paper
                      sx={{
                        p: 2,
                        mb: 3,
                        background: isDarkMode ? 'rgba(15, 23, 42, 0.5)' : 'rgba(248, 250, 252, 0.8)',
                        border: '1px solid',
                        borderColor: 'divider',
                        borderRadius: 1,
                      }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <Typography variant="caption" color="text.secondary">
                          {redditPost.username}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          •
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {redditPost.subreddit}
                        </Typography>
                        <Typography variant="caption" color="text.secondary" sx={{ ml: 'auto' }}>
                          {redditPost.timeAgo}
                        </Typography>
                      </Box>
                      <Chip
                        label={redditPost.stock}
                        size="small"
                        sx={{
                          mb: 1,
                          background: 'linear-gradient(135deg, rgba(37, 99, 235, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%)',
                          border: '1px solid',
                          borderColor: 'primary.main',
                        }}
                      />
                      <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                        {redditPost.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {redditPost.content}
                      </Typography>
                    </Paper>

                    {/* Sentiment Score */}
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <Typography variant="body2" color="text.secondary">
                        Sentiment Score:
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography
                          variant="h5"
                          sx={{
                            fontWeight: 800,
                            color: getSentimentColor(redditSentiment),
                            minWidth: 60,
                            textAlign: 'right',
                          }}
                        >
                          {redditSentiment > 0 ? '+' : ''}{redditSentiment}%
                        </Typography>
                        <Chip
                          label={getSentimentLabel(redditSentiment)}
                          size="small"
                          sx={{
                            background: `${getSentimentColor(redditSentiment)}20`,
                            color: getSentimentColor(redditSentiment),
                            border: `1px solid ${getSentimentColor(redditSentiment)}`,
                          }}
                        />
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>

            {/* YouTube Sentiment Card */}
            <Grid item xs={12} md={4}>
              <motion.div variants={scaleIn} whileHover={{ y: -5, transition: { duration: 0.3 } }}>
                <Card
                  sx={{
                    height: '100%',
                    background: isDarkMode
                      ? 'linear-gradient(145deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.85) 100%)'
                      : 'linear-gradient(145deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.95) 100%)',
                    backdropFilter: 'blur(20px)',
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 1,
                    overflow: 'hidden',
                    position: 'relative',
                  }}
                >
                  <CardContent sx={{ p: 3 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                      <YouTubeIcon sx={{ color: '#ff0000', fontSize: 24 }} />
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        YouTube Sentiment
                      </Typography>
                    </Box>

                    {/* YouTube Comment Card */}
                    <Paper
                      sx={{
                        p: 2,
                        mb: 3,
                        background: isDarkMode ? 'rgba(15, 23, 42, 0.5)' : 'rgba(248, 250, 252, 0.8)',
                        border: '1px solid',
                        borderColor: 'divider',
                        borderRadius: 1,
                      }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <Typography variant="caption" sx={{ fontWeight: 600 }}>
                          {youtubeComment.username}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {youtubeComment.timeAgo}
                        </Typography>
                      </Box>
                      <Chip
                        label={youtubeComment.stock}
                        size="small"
                        sx={{
                          mb: 1,
                          background: 'linear-gradient(135deg, rgba(37, 99, 235, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%)',
                          border: '1px solid',
                          borderColor: 'primary.main',
                        }}
                      />
                      <Typography variant="body2" color="text.secondary">
                        {youtubeComment.content}
                      </Typography>
                    </Paper>

                    {/* Sentiment Score */}
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <Typography variant="body2" color="text.secondary">
                        Sentiment Score:
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography
                          variant="h5"
                          sx={{
                            fontWeight: 800,
                            color: getSentimentColor(youtubeSentiment),
                            minWidth: 60,
                            textAlign: 'right',
                          }}
                        >
                          {youtubeSentiment > 0 ? '+' : ''}{youtubeSentiment}%
                        </Typography>
                        <Chip
                          label={getSentimentLabel(youtubeSentiment)}
                          size="small"
                          sx={{
                            background: `${getSentimentColor(youtubeSentiment)}20`,
                            color: getSentimentColor(youtubeSentiment),
                            border: `1px solid ${getSentimentColor(youtubeSentiment)}`,
                          }}
                        />
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>

            {/* Google Trends Card */}
            <Grid item xs={12} md={4}>
              <motion.div variants={scaleIn} whileHover={{ y: -5, transition: { duration: 0.3 } }}>
                <Card
                  sx={{
                    height: '100%',
                    background: isDarkMode
                      ? 'linear-gradient(145deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.85) 100%)'
                      : 'linear-gradient(145deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.95) 100%)',
                    backdropFilter: 'blur(20px)',
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 1,
                    overflow: 'hidden',
                    position: 'relative',
                  }}
                >
                  <CardContent sx={{ p: 3 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                      <TrendingUpIcon sx={{ color: '#4285f4', fontSize: 24 }} />
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        Google Trends
                      </Typography>
                    </Box>

                    {/* Trending Keyword */}
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                        Trending Keyword:
                      </Typography>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        {googleTrendsData.keyword}
                      </Typography>
                    </Box>

                    {/* Chart */}
                    <Box sx={{ height: 120, mb: 2 }}>
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={googleTrendsData.chartData}>
                          <XAxis
                            dataKey="time"
                            tick={{ fontSize: 10, fill: isDarkMode ? '#94a3b8' : '#64748b' }}
                            axisLine={{ stroke: isDarkMode ? '#475569' : '#cbd5e1' }}
                          />
                          <YAxis
                            tick={{ fontSize: 10, fill: isDarkMode ? '#94a3b8' : '#64748b' }}
                            axisLine={{ stroke: isDarkMode ? '#475569' : '#cbd5e1' }}
                            domain={[0, 100]}
                          />
                          <Tooltip
                            contentStyle={{
                              background: isDarkMode ? '#1e293b' : '#ffffff',
                              border: `1px solid ${isDarkMode ? '#475569' : '#e2e8f0'}`,
                              borderRadius: '8px',
                            }}
                          />
                          <Line
                            type="monotone"
                            dataKey="value"
                            stroke="#4285f4"
                            strokeWidth={2}
                            dot={false}
                            activeDot={{ r: 4 }}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </Box>

                    {/* Popularity Score */}
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <Typography variant="body2" color="text.secondary">
                        Popularity Score:
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography
                          variant="h5"
                          sx={{
                            fontWeight: 800,
                            color: '#4285f4',
                            minWidth: 60,
                            textAlign: 'right',
                          }}
                        >
                          {googleTrends}%
                        </Typography>
                        <Chip
                          label="Trending"
                          size="small"
                          sx={{
                            background: '#4285f420',
                            color: '#4285f4',
                            border: '1px solid #4285f4',
                          }}
                        />
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          </Grid>
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

      {/* Hero Section - Modern Bold Design */}
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
          pt: 0,
          pb: { xs: 8, md: 12 },
          mt: { xs: -4, md: -6 },
        }}
      >
        {/* Animated Background Elements */}
        <Box
          sx={{
            position: 'absolute',
            top: '10%',
            right: '5%',
            width: '400px',
            height: '400px',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, rgba(96, 165, 250, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%)',
            filter: 'blur(80px)',
            zIndex: 0,
          }}
          component={motion.div}
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
        <Box
          sx={{
            position: 'absolute',
            bottom: '15%',
            left: '5%',
            width: '300px',
            height: '300px',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, rgba(52, 211, 153, 0.15) 0%, rgba(96, 165, 250, 0.15) 100%)',
            filter: 'blur(60px)',
            zIndex: 0,
          }}
          component={motion.div}
          animate={{
            scale: [1, 1.3, 1],
            opacity: [0.3, 0.6, 0.3],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: 'easeInOut',
            delay: 1,
          }}
        />

        <Container
          maxWidth="xl"
          sx={{
            position: 'relative',
            zIndex: 3,
            px: { xs: 3, md: 4 },
          }}
        >
          <Grid container spacing={4} alignItems="center">
            {/* Left Side - Main Title & Description */}
            <Grid item xs={12} md={7}>
              <motion.div
                initial="hidden"
                animate="visible"
                variants={staggerContainer}
              >
                {/* Badge */}
                <motion.div variants={fadeInUp}>
                  <Chip
                    label="Quantitative Trading Platform"
                    sx={{
                      mb: 3,
                      px: 2,
                      py: 0.5,
                      background: 'linear-gradient(135deg, rgba(37, 99, 235, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%)',
                      border: '1px solid rgba(255, 255, 255, 0.3)',
                      color: '#ffffff',
                      fontWeight: 600,
                      fontSize: '0.875rem',
                      backdropFilter: 'blur(10px)',
                    }}
                  />
                </motion.div>

                {/* Main Title */}
                <motion.div variants={fadeInUp}>
                  <Typography
                    variant="h1"
                    sx={{
                      fontSize: { xs: '2.5rem', md: '4rem', lg: '5rem' },
                      fontWeight: 900,
                      mb: 4,
                      lineHeight: 1.1,
                      letterSpacing: '-0.04em',
                      color: '#ffffff',
                      textShadow: '0 4px 30px rgba(0, 0, 0, 0.5)',
                    }}
                  >
                    Where{' '}
                    <Box
                      component="span"
                      sx={{
                        background: 'linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%)',
                        backgroundClip: 'text',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        position: 'relative',
                      }}
                    >
                      Alternative Data
                    </Box>
                    <br />
                    Meets{' '}
                    <Box
                      component="span"
                      sx={{
                        background: 'linear-gradient(135deg, #34d399 0%, #60a5fa 100%)',
                        backgroundClip: 'text',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                      }}
                    >
                      Sector-Specific
                    </Box>
                    <br />
                    <Box
                      component="span"
                      sx={{
                        background: 'linear-gradient(135deg, #a78bfa 0%, #f472b6 100%)',
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
                      AI-Processed Signals
                    </Box>
                  </Typography>
                </motion.div>

                {/* Description */}
                <motion.div variants={fadeInUp}>
                  <Typography
                    variant="h6"
                    sx={{
                      mb: 5,
                      color: 'rgba(255, 255, 255, 0.85)',
                      fontWeight: 400,
                      lineHeight: 1.8,
                      fontSize: { xs: '1rem', md: '1.25rem' },
                      textShadow: '0 1px 10px rgba(0, 0, 0, 0.5)',
                      maxWidth: '90%',
                    }}
                  >
                    Transform unconventional data into actionable trading signals through sector-focused AI analysis. 
                    Our platform processes alternative data sources to generate rigorously backtested quantitative strategies 
                    that traditional analysis can't see.
                  </Typography>
                </motion.div>

                {/* CTA Buttons */}
                <motion.div variants={fadeInUp}>
                  <Box
                    sx={{
                      display: 'flex',
                      gap: 2,
                      flexWrap: 'wrap',
                      mb: 4,
                    }}
                  >
                    <motion.div
                      whileHover={{ scale: 1.05, y: -2 }}
                      whileTap={{ scale: 0.95 }}
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
                          '&:hover': {
                            background: 'linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%)',
                            boxShadow: '0 25px 50px rgba(37, 99, 235, 0.6)',
                            transform: 'translateY(-2px)',
                          },
                        }}
                      >
                        Explore Backtests
                      </Button>
                    </motion.div>
                    <motion.div
                      whileHover={{ scale: 1.05, y: -2 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      <Button
                        variant="outlined"
                        size="large"
                        startIcon={<DiscordIcon style={{ width: 24, height: 24 }} />}
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
            </Grid>

            {/* Right Side - Three Pillars Cards */}
            <Grid item xs={12} md={5}>
              <motion.div
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true, amount: 0.3 }}
                variants={staggerContainer}
              >
                {/* Pillar 01 - Alternative Data */}
                <motion.div
                  variants={fadeInUp}
                  whileHover={{ scale: 1.02, y: -8 }}
                  style={{ marginBottom: '1.5rem' }}
                >
                  <Paper
                    elevation={0}
                    sx={{
                      p: 3.5,
                      background: 'linear-gradient(135deg, rgba(37, 99, 235, 0.25) 0%, rgba(139, 92, 246, 0.25) 100%)',
                      backdropFilter: 'blur(30px)',
                      border: '1.5px solid rgba(255, 255, 255, 0.25)',
                      borderRadius: 3,
                      position: 'relative',
                      overflow: 'hidden',
                      transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                      '&::before': {
                        content: '"01"',
                        position: 'absolute',
                        top: -10,
                        right: -10,
                        fontSize: '8rem',
                        fontWeight: 900,
                        lineHeight: 1,
                        background: 'linear-gradient(135deg, rgba(96, 165, 250, 0.1) 0%, rgba(167, 139, 250, 0.1) 100%)',
                        backgroundClip: 'text',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        opacity: 0.3,
                        pointerEvents: 'none',
                      },
                      '&:hover': {
                        background: 'linear-gradient(135deg, rgba(37, 99, 235, 0.35) 0%, rgba(139, 92, 246, 0.35) 100%)',
                        borderColor: 'rgba(255, 255, 255, 0.4)',
                        boxShadow: '0 20px 60px rgba(37, 99, 235, 0.5)',
                      },
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                      <Box
                        sx={{
                          width: 56,
                          height: 56,
                          borderRadius: 2,
                          background: 'linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          boxShadow: '0 10px 30px rgba(96, 165, 250, 0.4)',
                        }}
                      >
                        <DataObjectIcon sx={{ fontSize: 32, color: '#ffffff' }} />
                      </Box>
                      <Box>
                        <Typography
                          variant="h5"
                          sx={{
                            fontWeight: 800,
                            background: 'linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%)',
                            backgroundClip: 'text',
                            WebkitBackgroundClip: 'text',
                            WebkitTextFillColor: 'transparent',
                            fontSize: { xs: '1.25rem', md: '1.5rem' },
                          }}
                        >
                          Alternative Data
                        </Typography>
                        <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '0.75rem' }}>
                          Non-traditional sources
                        </Typography>
                      </Box>
                    </Box>
                    <Typography
                      variant="body2"
                      sx={{
                        color: 'rgba(255, 255, 255, 0.9)',
                        lineHeight: 1.7,
                        fontSize: '0.95rem',
                      }}
                    >
                      Social sentiment, news flow, web traffic, and more - uncovering insights before they are reflected on the market.
                    </Typography>
                  </Paper>
                </motion.div>

                {/* Pillar 02 - Sector-Specific */}
                <motion.div
                  variants={fadeInUp}
                  whileHover={{ scale: 1.02, y: -8 }}
                  style={{ marginBottom: '1.5rem' }}
                >
                  <Paper
                    elevation={0}
                    sx={{
                      p: 3.5,
                      background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.25) 0%, rgba(59, 130, 246, 0.25) 100%)',
                      backdropFilter: 'blur(30px)',
                      border: '1.5px solid rgba(255, 255, 255, 0.25)',
                      borderRadius: 3,
                      position: 'relative',
                      overflow: 'hidden',
                      transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                      '&::before': {
                        content: '"02"',
                        position: 'absolute',
                        top: -10,
                        right: -10,
                        fontSize: '8rem',
                        fontWeight: 900,
                        lineHeight: 1,
                        background: 'linear-gradient(135deg, rgba(52, 211, 153, 0.1) 0%, rgba(96, 165, 250, 0.1) 100%)',
                        backgroundClip: 'text',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        opacity: 0.3,
                        pointerEvents: 'none',
                      },
                      '&:hover': {
                        background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.35) 0%, rgba(59, 130, 246, 0.35) 100%)',
                        borderColor: 'rgba(255, 255, 255, 0.4)',
                        boxShadow: '0 20px 60px rgba(16, 185, 129, 0.5)',
                      },
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                      <Box
                        sx={{
                          width: 56,
                          height: 56,
                          borderRadius: 2,
                          background: 'linear-gradient(135deg, #34d399 0%, #60a5fa 100%)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          boxShadow: '0 10px 30px rgba(52, 211, 153, 0.4)',
                        }}
                      >
                        <CategoryIcon sx={{ fontSize: 32, color: '#ffffff' }} />
                      </Box>
                      <Box>
                        <Typography
                          variant="h5"
                          sx={{
                            fontWeight: 800,
                            background: 'linear-gradient(135deg, #34d399 0%, #60a5fa 100%)',
                            backgroundClip: 'text',
                            WebkitBackgroundClip: 'text',
                            WebkitTextFillColor: 'transparent',
                            fontSize: { xs: '1.25rem', md: '1.5rem' },
                          }}
                        >
                          Sector-Specific
                        </Typography>
                        <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '0.75rem' }}>
                          Industry-focused signals
                        </Typography>
                      </Box>
                    </Box>
                    <Typography
                      variant="body2"
                      sx={{
                        color: 'rgba(255, 255, 255, 0.9)',
                        lineHeight: 1.7,
                        fontSize: '0.95rem',
                      }}
                    >
                      Every signal tailored to unique industry dynamics and drivers, not generic market-wide approaches.
                    </Typography>
                  </Paper>
                </motion.div>

                {/* Pillar 03 - AI-Processed Signals */}
                <motion.div
                  variants={fadeInUp}
                  whileHover={{ scale: 1.02, y: -8 }}
                >
                  <Paper
                    elevation={0}
                    sx={{
                      p: 3.5,
                      background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.25) 0%, rgba(236, 72, 153, 0.25) 100%)',
                      backdropFilter: 'blur(30px)',
                      border: '1.5px solid rgba(255, 255, 255, 0.25)',
                      borderRadius: 3,
                      position: 'relative',
                      overflow: 'hidden',
                      transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                      '&::before': {
                        content: '"03"',
                        position: 'absolute',
                        top: -10,
                        right: -10,
                        fontSize: '8rem',
                        fontWeight: 900,
                        lineHeight: 1,
                        background: 'linear-gradient(135deg, rgba(167, 139, 250, 0.1) 0%, rgba(244, 114, 182, 0.1) 100%)',
                        backgroundClip: 'text',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        opacity: 0.3,
                        pointerEvents: 'none',
                      },
                      '&:hover': {
                        background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.35) 0%, rgba(236, 72, 153, 0.35) 100%)',
                        borderColor: 'rgba(255, 255, 255, 0.4)',
                        boxShadow: '0 20px 60px rgba(139, 92, 246, 0.5)',
                      },
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                      <Box
                        sx={{
                          width: 56,
                          height: 56,
                          borderRadius: 2,
                          background: 'linear-gradient(135deg, #a78bfa 0%, #f472b6 100%)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          boxShadow: '0 10px 30px rgba(167, 139, 250, 0.4)',
                        }}
                      >
                        <SmartToyIcon sx={{ fontSize: 32, color: '#ffffff' }} />
                      </Box>
                      <Box>
                        <Typography
                          variant="h5"
                          sx={{
                            fontWeight: 800,
                            background: 'linear-gradient(135deg, #a78bfa 0%, #f472b6 100%)',
                            backgroundClip: 'text',
                            WebkitBackgroundClip: 'text',
                            WebkitTextFillColor: 'transparent',
                            fontSize: { xs: '1.25rem', md: '1.5rem' },
                          }}
                        >
                          AI-Processed Signals
                        </Typography>
                        <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '0.75rem' }}>
                          Advanced algorithms
                        </Typography>
                      </Box>
                    </Box>
                    <Typography
                      variant="body2"
                      sx={{
                        color: 'rgba(255, 255, 255, 0.9)',
                        lineHeight: 1.7,
                        fontSize: '0.95rem',
                      }}
                    >
                      AI algorithms identify patterns and correlations invisible to traditional analysis, generating actionable signals.
                    </Typography>
                  </Paper>
                </motion.div>
              </motion.div>
            </Grid>
          </Grid>
        </Container>

        {/* Scroll Indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 1.5 }}
          style={{
            position: 'absolute',
            bottom: 80,
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
                borderRadius: 1,
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

      {/* Our Signals Section */}
      <OurSignalsSection />

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
                          startIcon={<DiscordIcon style={{ width: 24, height: 24 }} />}
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
