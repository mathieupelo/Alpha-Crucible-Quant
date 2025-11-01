/**
 * Real-time News Feed Component
 * Displays aggregated news with sentiment analysis from GameCore-12 universe
 */

import React, { useState } from 'react';
import { useQuery } from 'react-query';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
  Link,
  CircularProgress,
  Alert,
  Paper,
} from '@mui/material';
import {
  Article as ArticleIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Remove as RemoveIcon,
  Launch as LaunchIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { format, parseISO, formatDistanceToNow } from 'date-fns';
import { newsApi } from '@/services/api';
import { useTheme } from '@/contexts/ThemeContext';

interface NewsItem {
  ticker: string;
  title: string;
  summary: string;
  publisher: string;
  link: string;
  pub_date: string;
  sentiment: {
    label: string;
    score: number;
    label_display: string;
    scores?: {
      positive: number;
      negative: number;
      neutral: number;
    };
  };
}

interface NewsFeedProps {
  universeName?: string;
  pollingInterval?: number; // in milliseconds
  maxItems?: number;
}

const NewsFeed: React.FC<NewsFeedProps> = ({
  universeName = 'GameCore-12 (GC-12)',
  pollingInterval = 30000, // 30 seconds
  maxItems = 10,
}) => {
  const { isDarkMode } = useTheme();
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // Fetch news with polling
  const { data, isLoading, error } = useQuery(
    ['news', universeName, maxItems],
    () => newsApi.getUniverseNews(universeName, maxItems),
    {
      refetchInterval: pollingInterval,
      staleTime: pollingInterval / 2,
      onSuccess: () => {
        setLastUpdate(new Date());
      },
    }
  );

  // Get sentiment color and icon
  const getSentimentStyle = (sentiment: NewsItem['sentiment']) => {
    switch (sentiment.label) {
      case 'positive':
        return {
          color: '#10b981',
          bgColor: isDarkMode ? 'rgba(16, 185, 129, 0.2)' : 'rgba(16, 185, 129, 0.1)',
          borderColor: isDarkMode ? 'rgba(16, 185, 129, 0.4)' : 'rgba(16, 185, 129, 0.3)',
          icon: <TrendingUpIcon sx={{ fontSize: 16 }} />,
        };
      case 'negative':
        return {
          color: '#ef4444',
          bgColor: isDarkMode ? 'rgba(239, 68, 68, 0.2)' : 'rgba(239, 68, 68, 0.1)',
          borderColor: isDarkMode ? 'rgba(239, 68, 68, 0.4)' : 'rgba(239, 68, 68, 0.3)',
          icon: <TrendingDownIcon sx={{ fontSize: 16 }} />,
        };
      default:
        return {
          color: '#6b7280',
          bgColor: isDarkMode ? 'rgba(107, 114, 128, 0.2)' : 'rgba(107, 114, 128, 0.1)',
          borderColor: isDarkMode ? 'rgba(107, 114, 128, 0.4)' : 'rgba(107, 114, 128, 0.3)',
          icon: <RemoveIcon sx={{ fontSize: 16 }} />,
        };
    }
  };

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
        return format(date, 'MMM dd, yyyy');
      }
    } catch {
      return dateStr;
    }
  };

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        Failed to load news. Please try again later.
      </Alert>
    );
  }

  return (
    <Box sx={{ position: 'relative' }}>
      {/* Header with last update indicator */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <motion.div
            animate={{ rotate: [0, 360] }}
            transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
            style={{ display: isLoading ? 'block' : 'none' }}
          >
            <CircularProgress size={20} />
          </motion.div>
          <Typography variant="h5" sx={{ fontWeight: 700 }}>
            Real-Time News Feed
          </Typography>
        </Box>
        <Typography variant="body2" color="text.secondary">
          {isLoading ? 'Updating...' : `Updated ${formatDistanceToNow(lastUpdate, { addSuffix: true })}`}
        </Typography>
      </Box>

      {/* News items */}
      {isLoading && !data ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
          <CircularProgress />
        </Box>
      ) : data && data.news && data.news.length > 0 ? (
        <AnimatePresence mode="popLayout">
          {data.news.map((item: NewsItem, index: number) => {
            const sentimentStyle = getSentimentStyle(item.sentiment);

            return (
              <motion.div
                key={`${item.ticker}-${item.pub_date}-${index}`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.4, delay: index * 0.05 }}
                layout
              >
                <Card
                  sx={{
                    mb: 2,
                    background: isDarkMode
                      ? 'linear-gradient(145deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.85) 100%)'
                      : 'linear-gradient(145deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.95) 100%)',
                    backdropFilter: 'blur(20px)',
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 3,
                    transition: 'all 0.3s ease',
                    position: 'relative',
                    overflow: 'hidden',
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
                      transform: 'translateY(-2px)',
                      boxShadow: `0 8px 24px ${sentimentStyle.color}20`,
                      borderColor: sentimentStyle.borderColor,
                    },
                  }}
                >
                  <CardContent sx={{ p: 3 }}>
                    {/* Header: Ticker, Sentiment, Time */}
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2, flexWrap: 'wrap', gap: 1 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                        <Chip
                          label={item.ticker}
                          size="small"
                          sx={{
                            fontWeight: 600,
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
                            color: sentimentStyle.color,
                            background: sentimentStyle.bgColor,
                            border: '1px solid',
                            borderColor: sentimentStyle.borderColor,
                            fontWeight: 500,
                          }}
                        />
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        {formatNewsDate(item.pub_date)}
                      </Typography>
                    </Box>

                    {/* Title */}
                    <Typography
                      variant="h6"
                      sx={{
                        fontWeight: 600,
                        mb: 1,
                        lineHeight: 1.4,
                        '&:hover': {
                          color: 'primary.main',
                        },
                      }}
                    >
                      <Link
                        href={item.link || '#'}
                        target="_blank"
                        rel="noopener noreferrer"
                        sx={{
                          color: 'inherit',
                          textDecoration: 'none',
                          display: 'flex',
                          alignItems: 'center',
                          gap: 0.5,
                          '&:hover': {
                            textDecoration: 'underline',
                          },
                        }}
                      >
                        {item.title || item.summary?.substring(0, 100) || 'News Article'}
                        <LaunchIcon sx={{ fontSize: 14, opacity: 0.6 }} />
                      </Link>
                    </Typography>

                    {/* Summary */}
                    {item.summary && (
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{
                          mb: 2,
                          lineHeight: 1.6,
                          display: '-webkit-box',
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: 'vertical',
                          overflow: 'hidden',
                        }}
                      >
                        {item.summary}
                      </Typography>
                    )}

                    {/* Footer: Publisher and Sentiment Score */}
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mt: 2, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
                      <Typography variant="caption" color="text.secondary">
                        {item.publisher || 'Unknown Source'}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                        {/* Sentiment Score Badge */}
                        <Box
                          sx={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 0.5,
                            px: 1.5,
                            py: 0.5,
                            borderRadius: 2,
                            background: sentimentStyle.bgColor,
                            border: '1px solid',
                            borderColor: sentimentStyle.borderColor,
                          }}
                        >
                          <Typography
                            variant="caption"
                            sx={{
                              fontWeight: 600,
                              color: sentimentStyle.color,
                              fontSize: '0.7rem',
                            }}
                          >
                            {item.sentiment.label_display}: {(item.sentiment.score * 100).toFixed(0)}%
                          </Typography>
                        </Box>
                        {/* Sentiment Breakdown (if available) */}
                        {item.sentiment.scores && (
                          <Box sx={{ display: 'flex', gap: 0.5, alignItems: 'center' }}>
                            <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.65rem' }}>
                              P:{(item.sentiment.scores.positive * 100).toFixed(0)}% N:{(item.sentiment.scores.negative * 100).toFixed(0)}% U:{(item.sentiment.scores.neutral * 100).toFixed(0)}%
                            </Typography>
                          </Box>
                        )}
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </AnimatePresence>
      ) : (
        <Paper
          sx={{
            p: 4,
            textAlign: 'center',
            background: isDarkMode ? 'rgba(30, 41, 59, 0.5)' : 'rgba(248, 250, 252, 0.5)',
          }}
        >
          <ArticleIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
          <Typography variant="body1" color="text.secondary">
            No news available at this time
          </Typography>
        </Paper>
      )}
    </Box>
  );
};

export default NewsFeed;

