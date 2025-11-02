/**
 * News Deep Dive Page
 * Comprehensive research platform for analyzing news sentiment with GPT-4o-mini insights
 */

import React, { useState, useMemo } from 'react';
import { useQuery } from 'react-query';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
  Grid,
  Container,
  CircularProgress,
  Alert,
  Divider,
  LinearProgress,
  Paper,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Remove as RemoveIcon,
  Launch as LaunchIcon,
  Insights as InsightsIcon,
  Article as ArticleIcon,
  AutoAwesome as AutoAwesomeIcon,
  Movie as MovieIcon,
  Gamepad as GamepadIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { format, parseISO } from 'date-fns';
import { useTheme } from '@/contexts/ThemeContext';
import { newsApi, marketApi } from '@/services/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';
import ReactMarkdown from 'react-markdown';

interface NewsItem {
  ticker: string;
  title: string;
  summary: string;
  publisher: string;
  link: string;
  pub_date: string;
  image_url?: string;
  sentiment: {
    label: string;
    score: number;
    label_display: string;
  };
}

interface TickerData {
  ticker: string;
  news: NewsItem[];
  intradayData?: any;
  priceData?: any;
  gptAnalyses?: { [newsId: string]: any };
}

const NewsDeepDive: React.FC = () => {
  const { isDarkMode } = useTheme();
  const [useMovieCore8, setUseMovieCore8] = useState(true);
  const [selectedTicker, setSelectedTicker] = useState<string | null>(null);
  const [analyzingNews, setAnalyzingNews] = useState<Set<string>>(new Set());
  const [gptAnalyses, setGptAnalyses] = useState<{ [key: string]: any }>({});

  const universeName = useMovieCore8 ? "MovieCore-8 (MC-8)" : "GameCore-12 (GC-12)";

  // Fetch today's aggregated news
  const { data: newsData, isLoading: newsLoading, error: newsError, refetch: refetchNews } = useQuery(
    ['today-news', universeName],
    () => newsApi.getTodayNewsAggregated(universeName),
    {
      refetchInterval: 60000, // Refresh every minute for real-time updates
      staleTime: 30000,
    }
  );

  // Fetch statistics
  const { data: statsData, isLoading: statsLoading } = useQuery(
    ['news-statistics', universeName],
    () => newsApi.getNewsStatistics(universeName),
    {
      refetchInterval: 60000,
      staleTime: 30000,
    }
  );

  // Get all tickers with news
  const tickersWithNews = useMemo(() => {
    if (!newsData?.tickers) return [];
    return Object.keys(newsData.tickers).sort();
  }, [newsData]);

  // Auto-select first ticker if none selected
  React.useEffect(() => {
    if (!selectedTicker && tickersWithNews.length > 0) {
      setSelectedTicker(tickersWithNews[0]);
    }
  }, [tickersWithNews, selectedTicker]);

  // Fetch intraday data for selected ticker
  const { data: intradayData, isLoading: intradayLoading } = useQuery(
    ['intraday', selectedTicker],
    () => marketApi.getIntradayPriceData(selectedTicker!),
    {
      enabled: !!selectedTicker,
      refetchInterval: 60000, // Update every minute
      staleTime: 30000,
    }
  );

  // Fetch live price for selected ticker
  const { data: livePriceData } = useQuery(
    ['live-price', selectedTicker],
    () => marketApi.getLivePrice(selectedTicker!),
    {
      enabled: !!selectedTicker,
      refetchInterval: 30000, // Update every 30 seconds
      staleTime: 15000,
    }
  );

  // Handle GPT analysis for a news item
  const handleAnalyzeNews = async (newsItem: NewsItem) => {
    const newsId = `${newsItem.ticker}-${newsItem.pub_date}-${newsItem.title}`;
    if (analyzingNews.has(newsId)) return;
    
    setAnalyzingNews(prev => new Set(prev).add(newsId));
    
    try {
      const priceData = livePriceData ? {
        price: livePriceData.price,
        previous_close: livePriceData.previous_close,
        daily_change: livePriceData.daily_change,
        daily_change_percent: livePriceData.daily_change_percent,
      } : {};
      
      const analysis = await newsApi.analyzeNews({
        ticker: newsItem.ticker,
        title: newsItem.title,
        summary: newsItem.summary,
        sentiment: newsItem.sentiment,
        price_data: priceData,
        pub_date: newsItem.pub_date,
      });
      
      // Store analysis
      setGptAnalyses(prev => ({
        ...prev,
        [newsId]: analysis,
      }));
    } catch (error) {
      console.error('Error analyzing news:', error);
    } finally {
      setAnalyzingNews(prev => {
        const next = new Set(prev);
        next.delete(newsId);
        return next;
      });
    }
  };

  // Prepare chart data with news markers
  const chartData = useMemo(() => {
    if (!intradayData?.data || !newsData?.tickers || !selectedTicker) return [];
    
    const tickerNews = newsData.tickers[selectedTicker] || [];
    
    // Convert intraday data to chart format
    const chartPoints = intradayData.data.map((point: any) => ({
      time: format(parseISO(point.datetime), 'HH:mm'),
      datetime: point.datetime,
      price: point.close,
      volume: point.volume,
    }));
    
    return chartPoints;
  }, [intradayData, newsData, selectedTicker]);

  // Prepare news markers for chart
  const newsMarkers = useMemo(() => {
    if (!chartData.length || !newsData?.tickers || !selectedTicker) return [];
    
    const tickerNews = newsData.tickers[selectedTicker] || [];
    const markers: any[] = [];
    
    tickerNews.forEach((news: NewsItem) => {
      try {
        const newsTime = parseISO(news.pub_date);
        // Find closest chart point
        const closestPoint = chartData.reduce((closest: any, point: any) => {
          const pointTime = parseISO(point.datetime);
          const closestTime = parseISO(closest.datetime);
          const currentDiff = Math.abs(newsTime.getTime() - pointTime.getTime());
          const closestDiff = Math.abs(newsTime.getTime() - closestTime.getTime());
          return currentDiff < closestDiff ? point : closest;
        }, chartData[0]);
        
        if (closestPoint) {
          markers.push({
            time: closestPoint.time,
            price: closestPoint.price,
            newsTitle: news.title,
            newsSentiment: news.sentiment.label,
            newsScore: news.sentiment.score,
            newsTime: format(newsTime, 'HH:mm'),
            pubDate: news.pub_date,
          });
        }
      } catch (e) {
        console.error('Error processing news for chart:', e);
      }
    });
    
    return markers;
  }, [chartData, newsData, selectedTicker]);

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

  if (newsError) {
    return (
      <Container maxWidth="xl">
        <Alert severity="error" sx={{ mt: 4 }}>
          Failed to load news data. Please try again later.
        </Alert>
      </Container>
    );
  }

  return (
    <Box sx={{ py: 4, minHeight: '100vh' }}>
      <Container maxWidth="xl">
        {/* Header with Sector Toggle */}
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3, flexWrap: 'wrap', gap: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <motion.div
                key={useMovieCore8 ? 'movies' : 'gaming'}
                initial={{ scale: 0, rotate: -180 }}
                animate={{ scale: 1, rotate: 0 }}
                transition={{ duration: 0.6, type: 'spring', stiffness: 200 }}
              >
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: '48px',
                    height: '48px',
                    borderRadius: '50%',
                    background: useMovieCore8
                      ? 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)'
                      : 'linear-gradient(135deg, #10b981 0%, #06b6d4 100%)',
                    boxShadow: useMovieCore8
                      ? '0 0 20px rgba(139, 92, 246, 0.6)'
                      : '0 0 20px rgba(16, 185, 129, 0.6)',
                  }}
                >
                  {useMovieCore8 ? (
                    <MovieIcon sx={{ fontSize: 28, color: '#ffffff' }} />
                  ) : (
                    <GamepadIcon sx={{ fontSize: 28, color: '#ffffff' }} />
                  )}
                </Box>
              </motion.div>
              <Typography
                variant="h3"
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
                News Deep Dive
              </Typography>
            </Box>
            
            {/* Sector Toggle */}
            <Box
              sx={{
                display: 'flex',
                background: isDarkMode ? 'rgba(30, 41, 59, 0.6)' : 'rgba(248, 250, 252, 0.8)',
                borderRadius: 3,
                p: 0.5,
                border: '1px solid',
                borderColor: isDarkMode ? 'rgba(148, 163, 184, 0.2)' : 'rgba(148, 163, 184, 0.3)',
                gap: 0.5,
                position: 'relative',
              }}
            >
              <motion.div
                animate={{ left: useMovieCore8 ? '4px' : 'calc(50% + 2px)' }}
                transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                style={{
                  position: 'absolute',
                  top: '4px',
                  width: 'calc(50% - 6px)',
                  height: 'calc(100% - 8px)',
                  borderRadius: '8px',
                  background: useMovieCore8
                    ? 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)'
                    : 'linear-gradient(135deg, #10b981 0%, #06b6d4 100%)',
                  zIndex: 0,
                }}
              />
              <Box
                onClick={() => setUseMovieCore8(true)}
                sx={{
                  px: 3,
                  py: 1,
                  borderRadius: 2,
                  cursor: 'pointer',
                  position: 'relative',
                  zIndex: 1,
                  color: useMovieCore8 ? '#ffffff' : (isDarkMode ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.7)'),
                  fontWeight: useMovieCore8 ? 700 : 500,
                }}
              >
                Movies
              </Box>
              <Box
                onClick={() => setUseMovieCore8(false)}
                sx={{
                  px: 3,
                  py: 1,
                  borderRadius: 2,
                  cursor: 'pointer',
                  position: 'relative',
                  zIndex: 1,
                  color: useMovieCore8 ? (isDarkMode ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.7)') : '#ffffff',
                  fontWeight: useMovieCore8 ? 500 : 700,
                }}
              >
                Gaming
              </Box>
            </Box>
          </Box>
          
          <Typography variant="body1" color="text.secondary">
            Comprehensive analysis of today's news with AI-powered insights and real-time price tracking
          </Typography>
        </Box>

        {newsLoading || statsLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            {/* Aggregate Statistics */}
            {statsData && (
              <Grid container spacing={3} sx={{ mb: 4 }}>
                {/* Top Tickers */}
                <Grid item xs={12} md={6}>
                  <Card
                    sx={{
                      background: isDarkMode
                        ? 'linear-gradient(145deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.85) 100%)'
                        : 'linear-gradient(145deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.95) 100%)',
                      backdropFilter: 'blur(20px)',
                      border: '1px solid',
                      borderColor: 'divider',
                    }}
                  >
                    <CardContent>
                      <Typography variant="h6" sx={{ mb: 2, fontWeight: 700 }}>
                        Top Tickers by Sentiment Today
                      </Typography>
                      {statsData.top_tickers.length > 0 ? (
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                          {statsData.top_tickers.map((ticker: any, idx: number) => (
                            <Box key={ticker.ticker} sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                              <Typography variant="body2" sx={{ fontWeight: 600, minWidth: 40 }}>
                                #{idx + 1}
                              </Typography>
                              <Chip label={ticker.ticker} size="small" sx={{ fontWeight: 600 }} />
                              <Box sx={{ flexGrow: 1 }}>
                                <LinearProgress
                                  variant="determinate"
                                  value={ticker.avg_sentiment_score * 100}
                                  sx={{
                                    height: 8,
                                    borderRadius: 1,
                                    backgroundColor: isDarkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
                                    '& .MuiLinearProgress-bar': {
                                      backgroundColor: '#10b981',
                                    },
                                  }}
                                />
                              </Box>
                              <Typography variant="caption" color="text.secondary">
                                {ticker.total_news} news
                              </Typography>
                            </Box>
                          ))}
                        </Box>
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          No data available
                        </Typography>
                      )}
                    </CardContent>
                  </Card>
                </Grid>

                {/* Bottom Tickers */}
                <Grid item xs={12} md={6}>
                  <Card
                    sx={{
                      background: isDarkMode
                        ? 'linear-gradient(145deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.85) 100%)'
                        : 'linear-gradient(145deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.95) 100%)',
                      backdropFilter: 'blur(20px)',
                      border: '1px solid',
                      borderColor: 'divider',
                    }}
                  >
                    <CardContent>
                      <Typography variant="h6" sx={{ mb: 2, fontWeight: 700 }}>
                        Bottom Tickers by Sentiment Today
                      </Typography>
                      {statsData.bottom_tickers.length > 0 ? (
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                          {statsData.bottom_tickers.map((ticker: any, idx: number) => (
                            <Box key={ticker.ticker} sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                              <Typography variant="body2" sx={{ fontWeight: 600, minWidth: 40 }}>
                                #{idx + 1}
                              </Typography>
                              <Chip label={ticker.ticker} size="small" sx={{ fontWeight: 600 }} />
                              <Box sx={{ flexGrow: 1 }}>
                                <LinearProgress
                                  variant="determinate"
                                  value={ticker.avg_sentiment_score * 100}
                                  sx={{
                                    height: 8,
                                    borderRadius: 1,
                                    backgroundColor: isDarkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
                                    '& .MuiLinearProgress-bar': {
                                      backgroundColor: '#ef4444',
                                    },
                                  }}
                                />
                              </Box>
                              <Typography variant="caption" color="text.secondary">
                                {ticker.total_news} news
                              </Typography>
                            </Box>
                          ))}
                        </Box>
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          No data available
                        </Typography>
                      )}
                    </CardContent>
                  </Card>
                </Grid>

                {/* Sector Trends */}
                <Grid item xs={12} md={6}>
                  <Card
                    sx={{
                      background: isDarkMode
                        ? 'linear-gradient(145deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.85) 100%)'
                        : 'linear-gradient(145deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.95) 100%)',
                      backdropFilter: 'blur(20px)',
                      border: '1px solid',
                      borderColor: 'divider',
                    }}
                  >
                    <CardContent>
                      <Typography variant="h6" sx={{ mb: 2, fontWeight: 700 }}>
                        Sector Trends Today
                      </Typography>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                        <Box>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="body2">Positive</Typography>
                            <Typography variant="body2" sx={{ fontWeight: 600, color: '#10b981' }}>
                              {statsData.sector_trends_today.positive_percent.toFixed(1)}%
                            </Typography>
                          </Box>
                          <LinearProgress
                            variant="determinate"
                            value={statsData.sector_trends_today.positive_percent}
                            sx={{
                              height: 10,
                              borderRadius: 1,
                              backgroundColor: isDarkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
                              '& .MuiLinearProgress-bar': { backgroundColor: '#10b981' },
                            }}
                          />
                        </Box>
                        <Box>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="body2">Neutral</Typography>
                            <Typography variant="body2" sx={{ fontWeight: 600, color: '#6b7280' }}>
                              {statsData.sector_trends_today.neutral_percent.toFixed(1)}%
                            </Typography>
                          </Box>
                          <LinearProgress
                            variant="determinate"
                            value={statsData.sector_trends_today.neutral_percent}
                            sx={{
                              height: 10,
                              borderRadius: 1,
                              backgroundColor: isDarkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
                              '& .MuiLinearProgress-bar': { backgroundColor: '#6b7280' },
                            }}
                          />
                        </Box>
                        <Box>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="body2">Negative</Typography>
                            <Typography variant="body2" sx={{ fontWeight: 600, color: '#ef4444' }}>
                              {statsData.sector_trends_today.negative_percent.toFixed(1)}%
                            </Typography>
                          </Box>
                          <LinearProgress
                            variant="determinate"
                            value={statsData.sector_trends_today.negative_percent}
                            sx={{
                              height: 10,
                              borderRadius: 1,
                              backgroundColor: isDarkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
                              '& .MuiLinearProgress-bar': { backgroundColor: '#ef4444' },
                            }}
                          />
                        </Box>
                        <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
                          Total: {statsData.sector_trends_today.total_news} articles
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Weekly Trends */}
                <Grid item xs={12} md={6}>
                  <Card
                    sx={{
                      background: isDarkMode
                        ? 'linear-gradient(145deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.85) 100%)'
                        : 'linear-gradient(145deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.95) 100%)',
                      backdropFilter: 'blur(20px)',
                      border: '1px solid',
                      borderColor: 'divider',
                    }}
                  >
                    <CardContent>
                      <Typography variant="h6" sx={{ mb: 2, fontWeight: 700 }}>
                        Sector Trends This Week
                      </Typography>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                        <Box>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="body2">Positive</Typography>
                            <Typography variant="body2" sx={{ fontWeight: 600, color: '#10b981' }}>
                              {statsData.sector_trends_week.positive_percent.toFixed(1)}%
                            </Typography>
                          </Box>
                          <LinearProgress
                            variant="determinate"
                            value={statsData.sector_trends_week.positive_percent}
                            sx={{
                              height: 10,
                              borderRadius: 1,
                              backgroundColor: isDarkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
                              '& .MuiLinearProgress-bar': { backgroundColor: '#10b981' },
                            }}
                          />
                        </Box>
                        <Box>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="body2">Neutral</Typography>
                            <Typography variant="body2" sx={{ fontWeight: 600, color: '#6b7280' }}>
                              {statsData.sector_trends_week.neutral_percent.toFixed(1)}%
                            </Typography>
                          </Box>
                          <LinearProgress
                            variant="determinate"
                            value={statsData.sector_trends_week.neutral_percent}
                            sx={{
                              height: 10,
                              borderRadius: 1,
                              backgroundColor: isDarkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
                              '& .MuiLinearProgress-bar': { backgroundColor: '#6b7280' },
                            }}
                          />
                        </Box>
                        <Box>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="body2">Negative</Typography>
                            <Typography variant="body2" sx={{ fontWeight: 600, color: '#ef4444' }}>
                              {statsData.sector_trends_week.negative_percent.toFixed(1)}%
                            </Typography>
                          </Box>
                          <LinearProgress
                            variant="determinate"
                            value={statsData.sector_trends_week.negative_percent}
                            sx={{
                              height: 10,
                              borderRadius: 1,
                              backgroundColor: isDarkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
                              '& .MuiLinearProgress-bar': { backgroundColor: '#ef4444' },
                            }}
                          />
                        </Box>
                        <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
                          Total: {statsData.sector_trends_week.total_news} articles
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            )}

            {/* Ticker Selection and Charts */}
            {tickersWithNews.length > 0 && (
              <Box sx={{ mb: 4 }}>
                <Typography variant="h5" sx={{ mb: 2, fontWeight: 700 }}>
                  Select Ticker to View Analysis
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3 }}>
                  {tickersWithNews.map((ticker) => (
                    <Chip
                      key={ticker}
                      label={ticker}
                      onClick={() => setSelectedTicker(ticker)}
                      sx={{
                        cursor: 'pointer',
                        fontWeight: selectedTicker === ticker ? 700 : 500,
                        background: selectedTicker === ticker
                          ? (useMovieCore8
                              ? 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)'
                              : 'linear-gradient(135deg, #10b981 0%, #06b6d4 100%)')
                          : 'transparent',
                        color: selectedTicker === ticker ? '#ffffff' : 'inherit',
                        border: selectedTicker === ticker ? 'none' : '1px solid',
                        borderColor: 'divider',
                        '&:hover': {
                          background: selectedTicker === ticker
                            ? (useMovieCore8
                                ? 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)'
                                : 'linear-gradient(135deg, #10b981 0%, #06b6d4 100%)')
                            : (isDarkMode ? 'rgba(148, 163, 184, 0.15)' : 'rgba(148, 163, 184, 0.08)'),
                        },
                      }}
                    />
                  ))}
                </Box>

                {selectedTicker && newsData?.tickers[selectedTicker] && (
                  <Grid container spacing={3}>
                    {/* Intraday Price Chart */}
                    <Grid item xs={12}>
                      <Card
                        sx={{
                          background: isDarkMode
                            ? 'linear-gradient(145deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.85) 100%)'
                            : 'linear-gradient(145deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.95) 100%)',
                          backdropFilter: 'blur(20px)',
                          border: '1px solid',
                          borderColor: 'divider',
                        }}
                      >
                        <CardContent>
                          <Typography variant="h6" sx={{ mb: 2, fontWeight: 700 }}>
                            {selectedTicker} - Intraday Price Movement (Today)
                          </Typography>
                          {intradayLoading ? (
                            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                              <CircularProgress />
                            </Box>
                          ) : chartData.length > 0 ? (
                            <Box>
                              <ResponsiveContainer width="100%" height={400}>
                                <LineChart data={chartData}>
                                  <CartesianGrid strokeDasharray="3 3" stroke={isDarkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'} />
                                  <XAxis
                                    dataKey="time"
                                    stroke={isDarkMode ? '#cbd5e1' : '#475569'}
                                    style={{ fontSize: '12px' }}
                                  />
                                  <YAxis
                                    stroke={isDarkMode ? '#cbd5e1' : '#475569'}
                                    style={{ fontSize: '12px' }}
                                  />
                                  <Tooltip
                                    contentStyle={{
                                      background: isDarkMode ? 'rgba(30, 41, 59, 0.95)' : 'rgba(255, 255, 255, 0.95)',
                                      border: `1px solid ${isDarkMode ? 'rgba(148, 163, 184, 0.3)' : 'rgba(148, 163, 184, 0.2)'}`,
                                      borderRadius: '8px',
                                    }}
                                    formatter={(value: any, name: string, props: any) => {
                                      if (props.payload?.newsTitle) {
                                        return [
                                          <div key="news">
                                            <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>${Number(value).toFixed(2)}</div>
                                            <div style={{ fontSize: '11px', color: '#666', marginTop: '4px' }}>
                                              <strong>News:</strong> {props.payload.newsTitle}
                                            </div>
                                          </div>,
                                          'Price',
                                        ];
                                      }
                                      return [`$${Number(value).toFixed(2)}`, 'Price'];
                                    }}
                                  />
                                  <Legend />
                                  <Line
                                    type="monotone"
                                    dataKey="price"
                                    stroke={useMovieCore8 ? '#8b5cf6' : '#10b981'}
                                    strokeWidth={2}
                                    dot={false}
                                    activeDot={{ r: 6 }}
                                  />
                                  {/* News markers */}
                                  {newsMarkers.map((marker, idx) => (
                                    <ReferenceLine
                                      key={`news-${idx}`}
                                      x={marker.time}
                                      stroke={
                                        marker.newsSentiment === 'positive' ? '#10b981' :
                                        marker.newsSentiment === 'negative' ? '#ef4444' : '#6b7280'
                                      }
                                      strokeWidth={2}
                                      strokeDasharray="5 5"
                                    />
                                  ))}
                                </LineChart>
                              </ResponsiveContainer>
                              {/* Legend for news markers */}
                              {newsMarkers.length > 0 && (
                                <Box sx={{ mt: 2, display: 'flex', gap: 2, flexWrap: 'wrap', fontSize: '0.75rem' }}>
                                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    <Box sx={{ width: 16, height: 2, background: '#10b981', borderStyle: 'dashed', borderWidth: '1px' }} />
                                    <Typography variant="caption" color="text.secondary">Positive News</Typography>
                                  </Box>
                                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    <Box sx={{ width: 16, height: 2, background: '#ef4444', borderStyle: 'dashed', borderWidth: '1px' }} />
                                    <Typography variant="caption" color="text.secondary">Negative News</Typography>
                                  </Box>
                                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    <Box sx={{ width: 16, height: 2, background: '#6b7280', borderStyle: 'dashed', borderWidth: '1px' }} />
                                    <Typography variant="caption" color="text.secondary">Neutral News</Typography>
                                  </Box>
                                </Box>
                              )}
                            </Box>
                          ) : (
                            <Box sx={{ textAlign: 'center', py: 4 }}>
                              <Typography variant="body2" color="text.secondary">
                                No intraday data available for {selectedTicker}
                              </Typography>
                            </Box>
                          )}
                          {livePriceData && (
                            <Box sx={{ mt: 2, display: 'flex', gap: 3, flexWrap: 'wrap' }}>
                              <Typography variant="body2">
                                <strong>Current:</strong> ${livePriceData.price?.toFixed(2)}
                              </Typography>
                              <Typography variant="body2" sx={{ color: livePriceData.daily_change_percent >= 0 ? '#10b981' : '#ef4444' }}>
                                <strong>Change:</strong> {livePriceData.daily_change_percent >= 0 ? '+' : ''}
                                {livePriceData.daily_change_percent?.toFixed(2)}%
                              </Typography>
                            </Box>
                          )}
                        </CardContent>
                      </Card>
                    </Grid>

                    {/* News Items for Selected Ticker */}
                    <Grid item xs={12}>
                      <Typography variant="h5" sx={{ mb: 2, fontWeight: 700 }}>
                        News Articles for {selectedTicker}
                      </Typography>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                        {newsData.tickers[selectedTicker].map((newsItem: NewsItem, idx: number) => {
                          const sentimentStyle = getSentimentStyle(newsItem.sentiment);
                          return (
                            <Card
                              key={`${newsItem.ticker}-${newsItem.pub_date}-${idx}`}
                              sx={{
                                background: isDarkMode
                                  ? 'linear-gradient(145deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.85) 100%)'
                                  : 'linear-gradient(145deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.95) 100%)',
                                backdropFilter: 'blur(20px)',
                                border: '1px solid',
                                borderColor: 'divider',
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
                              }}
                            >
                              <CardContent sx={{ p: 3 }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2, flexWrap: 'wrap' }}>
                                  <Chip
                                    icon={sentimentStyle.icon}
                                    label={newsItem.sentiment.label_display}
                                    size="small"
                                    sx={{
                                      color: sentimentStyle.color,
                                      background: sentimentStyle.bgColor,
                                      border: '1px solid',
                                      borderColor: sentimentStyle.borderColor,
                                      fontWeight: 600,
                                    }}
                                  />
                                  <Typography variant="caption" color="text.secondary">
                                    {format(parseISO(newsItem.pub_date), 'MMM dd, yyyy HH:mm')}
                                  </Typography>
                                  <Typography variant="caption" color="text.secondary">
                                    {newsItem.publisher}
                                  </Typography>
                                </Box>
                                
                                <Typography
                                  variant="h6"
                                  sx={{
                                    fontWeight: 600,
                                    mb: 1.5,
                                    fontSize: '1.1rem',
                                  }}
                                >
                                  <a
                                    href={newsItem.link || '#'}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    style={{
                                      color: 'inherit',
                                      textDecoration: 'none',
                                      display: 'flex',
                                      alignItems: 'flex-start',
                                      gap: '4px',
                                    }}
                                  >
                                    {newsItem.title}
                                    <LaunchIcon sx={{ fontSize: 16, opacity: 0.6, mt: 0.25 }} />
                                  </a>
                                </Typography>
                                
                                {newsItem.summary && (
                                  <Typography
                                    variant="body2"
                                    color="text.secondary"
                                    sx={{
                                      mb: 2,
                                      lineHeight: 1.6,
                                    }}
                                  >
                                    {newsItem.summary}
                                  </Typography>
                                )}
                                
                                <Box sx={{ display: 'flex', gap: 1, mt: 2, flexWrap: 'wrap' }}>
                                  <Chip
                                    label={`Sentiment: ${(newsItem.sentiment.score * 100).toFixed(0)}%`}
                                    size="small"
                                    sx={{
                                      fontSize: '0.75rem',
                                      background: sentimentStyle.bgColor,
                                      border: '1px solid',
                                      borderColor: sentimentStyle.borderColor,
                                      color: sentimentStyle.color,
                                      fontWeight: 600,
                                    }}
                                  />
                                  <Chip
                                    icon={<AutoAwesomeIcon sx={{ fontSize: 16 }} />}
                                    label={analyzingNews.has(`${newsItem.ticker}-${newsItem.pub_date}-${newsItem.title}`) ? "Analyzing..." : "Analyze with AI"}
                                    size="small"
                                    onClick={() => handleAnalyzeNews(newsItem)}
                                    disabled={analyzingNews.has(`${newsItem.ticker}-${newsItem.pub_date}-${newsItem.title}`)}
                                    sx={{
                                      cursor: 'pointer',
                                      fontSize: '0.75rem',
                                      background: 'linear-gradient(135deg, #2563eb 0%, #8b5cf6 100%)',
                                      color: '#ffffff',
                                      fontWeight: 600,
                                      '&:hover': {
                                        background: analyzingNews.has(`${newsItem.ticker}-${newsItem.pub_date}-${newsItem.title}`) 
                                          ? 'linear-gradient(135deg, #2563eb 0%, #8b5cf6 100%)'
                                          : 'linear-gradient(135deg, #1d4ed8 0%, #7c3aed 100%)',
                                      },
                                    }}
                                  />
                                </Box>
                                
                                {/* Display GPT Analysis */}
                                {gptAnalyses[`${newsItem.ticker}-${newsItem.pub_date}-${newsItem.title}`] && (() => {
                                  // Parse the analysis into sections
                                  const analysisText = gptAnalyses[`${newsItem.ticker}-${newsItem.pub_date}-${newsItem.title}`].analysis;
                                  const parseSections = (text: string) => {
                                    const sections: { [key: string]: string } = {};
                                    const summaryMatch = text.match(/##\s*Brief Summary\s*\n([\s\S]*?)(?=##|$)/i);
                                    const priceMatch = text.match(/##\s*Price Impact\s*\n([\s\S]*?)(?=##|$)/i);
                                    const sentimentMatch = text.match(/##\s*Sentiment Analysis\s*\n([\s\S]*?)(?=##|$)/i);
                                    
                                    sections.summary = summaryMatch ? summaryMatch[1].trim() : '';
                                    sections.priceImpact = priceMatch ? priceMatch[1].trim() : '';
                                    sections.sentiment = sentimentMatch ? sentimentMatch[1].trim() : '';
                                    
                                    // Fallback: if sections not found, try to split by any h2 headers
                                    if (!sections.summary && !sections.priceImpact && !sections.sentiment) {
                                      const parts = text.split(/##\s*/);
                                      if (parts.length > 1) {
                                        sections.summary = parts.find(p => p.toLowerCase().includes('summary'))?.replace(/^[^\n]+\n/, '').trim() || '';
                                        sections.priceImpact = parts.find(p => p.toLowerCase().includes('price'))?.replace(/^[^\n]+\n/, '').trim() || '';
                                        sections.sentiment = parts.find(p => p.toLowerCase().includes('sentiment'))?.replace(/^[^\n]+\n/, '').trim() || '';
                                      }
                                    }
                                    
                                    return sections;
                                  };
                                  
                                  const sections = parseSections(analysisText);
                                  const hasSections = sections.summary || sections.priceImpact || sections.sentiment;
                                  
                                  return (
                                    <Box sx={{ mt: 3 }}>
                                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                                        <AutoAwesomeIcon sx={{ fontSize: 20, color: '#2563eb' }} />
                                        <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#2563eb' }}>
                                          AI Analysis (GPT-4o-mini)
                                        </Typography>
                                      </Box>
                                      
                                      {hasSections ? (
                                        <Grid container spacing={2}>
                                          {/* Summary - smaller width to give more space to right side */}
                                          <Grid item xs={12} md={6}>
                                            <Card
                                              sx={{
                                                height: '100%',
                                                background: isDarkMode
                                                  ? 'rgba(37, 99, 235, 0.1)'
                                                  : 'rgba(37, 99, 235, 0.05)',
                                                border: '1px solid',
                                                borderColor: isDarkMode
                                                  ? 'rgba(37, 99, 235, 0.3)'
                                                  : 'rgba(37, 99, 235, 0.2)',
                                              }}
                                            >
                                              <CardContent>
                                                <Typography variant="h6" sx={{ fontWeight: 700, mb: 1.5, color: '#2563eb' }}>
                                                  Brief Summary
                                                </Typography>
                                                <Box
                                                  sx={{
                                                    '& p': {
                                                      marginBottom: 1,
                                                      lineHeight: 1.7,
                                                      color: 'text.primary',
                                                    },
                                                    '& ul, & ol': {
                                                      marginLeft: 2,
                                                      marginBottom: 1,
                                                      paddingLeft: 2,
                                                    },
                                                    '& li': {
                                                      marginBottom: 0.5,
                                                      lineHeight: 1.7,
                                                    },
                                                    '& strong': {
                                                      fontWeight: 700,
                                                      color: 'text.primary',
                                                    },
                                                  }}
                                                >
                                                  <ReactMarkdown>{sections.summary || 'No summary available.'}</ReactMarkdown>
                                                </Box>
                                              </CardContent>
                                            </Card>
                                          </Grid>
                                          
                                          {/* Price Impact & Sentiment - more width, stacked */}
                                          <Grid item xs={12} md={6}>
                                            <Grid container spacing={2} sx={{ height: '100%' }}>
                                              {/* Price Impact */}
                                              <Grid item xs={12}>
                                                <Card
                                                  sx={{
                                                    height: '100%',
                                                    background: isDarkMode
                                                      ? 'rgba(16, 185, 129, 0.1)'
                                                      : 'rgba(16, 185, 129, 0.05)',
                                                    border: '1px solid',
                                                    borderColor: isDarkMode
                                                      ? 'rgba(16, 185, 129, 0.3)'
                                                      : 'rgba(16, 185, 129, 0.2)',
                                                  }}
                                                >
                                                  <CardContent>
                                                    <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 1, color: '#10b981', fontSize: '0.95rem' }}>
                                                      Price Impact
                                                    </Typography>
                                                    <Box
                                                      sx={{
                                                        '& p': {
                                                          marginBottom: 0.75,
                                                          lineHeight: 1.6,
                                                          color: 'text.primary',
                                                          fontSize: '0.875rem',
                                                        },
                                                        '& strong': {
                                                          fontWeight: 700,
                                                          color: 'text.primary',
                                                        },
                                                      }}
                                                    >
                                                      <ReactMarkdown>{sections.priceImpact || 'No price impact analysis available.'}</ReactMarkdown>
                                                    </Box>
                                                  </CardContent>
                                                </Card>
                                              </Grid>
                                              
                                              {/* Sentiment Analysis */}
                                              <Grid item xs={12}>
                                                <Card
                                                  sx={{
                                                    height: '100%',
                                                    background: isDarkMode
                                                      ? 'rgba(139, 92, 246, 0.1)'
                                                      : 'rgba(139, 92, 246, 0.05)',
                                                    border: '1px solid',
                                                    borderColor: isDarkMode
                                                      ? 'rgba(139, 92, 246, 0.3)'
                                                      : 'rgba(139, 92, 246, 0.2)',
                                                  }}
                                                >
                                                  <CardContent>
                                                    <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 1, color: '#8b5cf6', fontSize: '0.95rem' }}>
                                                      Sentiment Analysis
                                                    </Typography>
                                                    <Box
                                                      sx={{
                                                        '& p': {
                                                          marginBottom: 0.75,
                                                          lineHeight: 1.6,
                                                          color: 'text.primary',
                                                          fontSize: '0.875rem',
                                                        },
                                                        '& strong': {
                                                          fontWeight: 700,
                                                          color: 'text.primary',
                                                        },
                                                      }}
                                                    >
                                                      <ReactMarkdown>{sections.sentiment || 'No sentiment analysis available.'}</ReactMarkdown>
                                                    </Box>
                                                  </CardContent>
                                                </Card>
                                              </Grid>
                                            </Grid>
                                          </Grid>
                                        </Grid>
                                      ) : (
                                        // Fallback: display full analysis if sections not parsed
                                        <Card
                                          sx={{
                                            background: isDarkMode
                                              ? 'rgba(37, 99, 235, 0.1)'
                                              : 'rgba(37, 99, 235, 0.05)',
                                            border: '1px solid',
                                            borderColor: isDarkMode
                                              ? 'rgba(37, 99, 235, 0.3)'
                                              : 'rgba(37, 99, 235, 0.2)',
                                          }}
                                        >
                                          <CardContent>
                                            <Box
                                              sx={{
                                                '& p': {
                                                  marginBottom: 1.5,
                                                  lineHeight: 1.7,
                                                  color: 'text.primary',
                                                },
                                                '& h2': {
                                                  marginTop: 2,
                                                  marginBottom: 1,
                                                  fontWeight: 700,
                                                  color: 'text.primary',
                                                  fontSize: '1.2rem',
                                                },
                                                '& ul, & ol': {
                                                  marginLeft: 2,
                                                  marginBottom: 1.5,
                                                  paddingLeft: 2,
                                                },
                                                '& li': {
                                                  marginBottom: 0.5,
                                                  lineHeight: 1.7,
                                                },
                                                '& strong': {
                                                  fontWeight: 700,
                                                  color: 'text.primary',
                                                },
                                              }}
                                            >
                                              <ReactMarkdown>{analysisText}</ReactMarkdown>
                                            </Box>
                                          </CardContent>
                                        </Card>
                                      )}
                                    </Box>
                                  );
                                })()}
                              </CardContent>
                            </Card>
                          );
                        })}
                      </Box>
                    </Grid>
                  </Grid>
                )}
              </Box>
            )}

            {tickersWithNews.length === 0 && !newsLoading && (
              <Paper sx={{ p: 4, textAlign: 'center' }}>
                <ArticleIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                <Typography variant="body1" color="text.secondary">
                  No news available for today
                </Typography>
              </Paper>
            )}
          </>
        )}
      </Container>
    </Box>
  );
};

export default NewsDeepDive;
