/**
 * Live News Preview Component
 * Displays a carousel of recent news articles with sentiment analysis
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from 'react-query';
import {
  Box,
  Typography,
  Container,
  Button,
  Card,
  CardContent,
  Chip,
  IconButton,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Remove as RemoveIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  RadioButtonChecked as RadioButtonCheckedIcon,
  ArrowForward as ArrowForwardIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { format, parseISO } from 'date-fns';
import { useTheme } from '@/contexts/ThemeContext';
import { newsApi } from '@/services/api';
import { fadeInUp, staggerContainer } from '@/components/home/animations';

export const LiveNewsPreview: React.FC = () => {
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

  const previewNews = newsData?.news || [];
  const visibleItems = 3;
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
        const gap = 24;
        
        const newIndex = Math.max(0, currentIndex - 1);
        setCurrentIndex(newIndex);
        
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
        const gap = 24;
        
        const newIndex = Math.min(maxIndex, currentIndex + 1);
        setCurrentIndex(newIndex);
        
        const targetScroll = newIndex * (cardWidth + gap);
        container.scrollTo({
          left: targetScroll,
          behavior: 'smooth',
        });
      }
    }
  };

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

          <Box 
            sx={{ 
              position: 'relative', 
              mb: 4,
              px: { xs: 2, md: 3 },
              overflow: 'visible',
            }}
          >
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
                width: '100%',
                maxWidth: '100%',
                '& > *': {
                  flexShrink: 0,
                },
                isolation: 'isolate',
                transform: 'translateZ(0)',
                willChange: 'scroll-position',
                '&::-webkit-scrollbar': {
                  display: 'none',
                },
                scrollbarWidth: 'none',
                msOverflowStyle: 'none',
              }}
            >
              {newsLoading || displayNews.length < 3 ? (
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
                        borderRadius: 1,
                        boxShadow: 'none',
                      }}
                    >
                      <CardContent sx={{ p: 3 }}>
                        <Box sx={{ mb: 2, borderRadius: 1, overflow: 'hidden', width: '100%', height: '120px', bgcolor: isDarkMode ? 'rgba(148, 163, 184, 0.1)' : 'rgba(148, 163, 184, 0.05)' }} />
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
                        borderRadius: 1,
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
                        {item.image_url && (
                          <Box
                            sx={{
                              mb: 2,
                              borderRadius: 1,
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

