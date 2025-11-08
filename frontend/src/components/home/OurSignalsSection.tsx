/**
 * Our Signals Section Component
 * Displays real-time sentiment analysis from Reddit, YouTube, and Google Trends
 */

import React, { useState } from 'react';
import {
  Box,
  Typography,
  Container,
  Grid,
  Card,
  CardContent,
  Chip,
  Paper,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  Reddit as RedditIcon,
  YouTube as YouTubeIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts';
import { useTheme } from '@/contexts/ThemeContext';
import { fadeInUp, staggerContainer, scaleIn } from '@/components/home/animations';

const redditPosts: Array<{
  username: string;
  subreddit: string;
  timeAgo: string;
  title: string;
  content: string;
  stock: string;
  sentimentScore: number;
}> = [
  {
    username: 'u/AssassinFan42',
    subreddit: 'r/assassinscreed',
    timeAgo: '2 hours ago',
    title: 'Just finished the new AC and WOW this is peak Ubisoft',
    content: 'The new Assassin\'s Creed game is absolutely incredible! The world building is insane and the gameplay mechanics feel so smooth. Ubisoft really outdid themselves with this one. Best AC game in years! $UBI',
    stock: 'UBI',
    sentimentScore: 78,
  },
  {
    username: 'u/XboxGamer99',
    subreddit: 'r/XboxSeriesX',
    timeAgo: '4 hours ago',
    title: 'Game Pass is the best value in gaming right now',
    content: 'Microsoft Game Pass is absolutely insane. I just got access to so many games day one and the library keeps growing. This is why I love my Xbox. Microsoft is killing it! $MSFT',
    stock: 'MSFT',
    sentimentScore: 85,
  },
  {
    username: 'u/FarCryPlayer',
    subreddit: 'r/farcry',
    timeAgo: '5 hours ago',
    title: 'Far Cry 7 leaked gameplay looks absolutely insane',
    content: 'Just saw some leaked footage of Far Cry 7 and it looks like Ubisoft is going all out. The graphics are next level and the open world looks massive. Can\'t wait for this to drop! $UBI',
    stock: 'UBI',
    sentimentScore: 82,
  },
  {
    username: 'u/HaloVeteran',
    subreddit: 'r/halo',
    timeAgo: '7 hours ago',
    title: 'Halo Infinite Season 5 is actually good now',
    content: 'Microsoft finally listened to the community. The new Halo Infinite update fixed so many issues and added great content. This is the Halo we deserved from launch. $MSFT',
    stock: 'MSFT',
    sentimentScore: 72,
  },
  {
    username: 'u/GamingCritic',
    subreddit: 'r/gaming',
    timeAgo: '8 hours ago',
    title: 'Is it just me or is Ubisoft getting worse with microtransactions?',
    content: 'Played the new Watch Dogs and the amount of microtransactions is ridiculous. Feels like they\'re trying to squeeze every penny. Used to love their games but this is getting out of hand. $UBI',
    stock: 'UBI',
    sentimentScore: -28,
  },
  {
    username: 'u/CoDPlayer2024',
    subreddit: 'r/ModernWarfare',
    timeAgo: '10 hours ago',
    title: 'Call of Duty is becoming too expensive',
    content: 'Another year, another $70 CoD game with $20 battle passes. Activision Blizzard is just milking the franchise dry at this point. When did gaming become so expensive? $ATVI',
    stock: 'ATVI',
    sentimentScore: -32,
  },
  {
    username: 'u/ApexLegend',
    subreddit: 'r/apexlegends',
    timeAgo: '12 hours ago',
    title: 'EA just dropped the best Apex update in a while',
    content: 'The new Apex Legends season is actually fire! New legend is balanced, map changes are great, and the battle pass is worth it this time. EA finally did something right! $EA',
    stock: 'EA',
    sentimentScore: 68,
  },
  {
    username: 'u/RainbowSixVet',
    subreddit: 'r/Rainbow6',
    timeAgo: '14 hours ago',
    title: 'Ubisoft just dropped the best R6 update in months',
    content: 'The new Rainbow Six Siege update is fire! New operators are balanced and the map rework is incredible. Ubisoft really listens to the community feedback. This is why I keep coming back! $UBI',
    stock: 'UBI',
    sentimentScore: 65,
  },
];

export const OurSignalsSection: React.FC = () => {
  const { isDarkMode } = useTheme();
  const [redditSentiment, setRedditSentiment] = useState(0);
  const [youtubeSentiment, setYoutubeSentiment] = useState(0);
  const [googleTrends, setGoogleTrends] = useState(0);
  const [currentRedditPostIndex, setCurrentRedditPostIndex] = useState(0);

  const redditPost = React.useMemo(() => {
    return redditPosts[currentRedditPostIndex];
  }, [currentRedditPostIndex]);

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

  React.useEffect(() => {
    const postRotationInterval = 10000;
    const rotationTimer = setInterval(() => {
      setCurrentRedditPostIndex((prevIndex) => (prevIndex + 1) % redditPosts.length);
    }, postRotationInterval);
    return () => clearInterval(rotationTimer);
  }, []);

  React.useEffect(() => {
    setRedditSentiment(0);
    const currentPost = redditPosts[currentRedditPostIndex];
    const targetSentiment = currentPost.sentimentScore;
    const duration = 3000;
    const steps = 60;
    const interval = duration / steps;
    let redditStep = 0;
    const redditTimer = setInterval(() => {
      redditStep++;
      const progress = Math.min(1, redditStep / steps);
      const current = targetSentiment * progress;
      setRedditSentiment(Math.floor(current));
      if (redditStep >= steps) clearInterval(redditTimer);
    }, interval);
    return () => clearInterval(redditTimer);
  }, [currentRedditPostIndex]);

  React.useEffect(() => {
    const duration = 3000;
    const steps = 60;
    const interval = duration / steps;
    let youtubeStep = 0;
    const youtubeIncrement = youtubeComment.targetSentiment / steps;
    const youtubeTimer = setInterval(() => {
      youtubeStep++;
      const current = Math.min(youtubeComment.targetSentiment, youtubeIncrement * youtubeStep);
      setYoutubeSentiment(Math.floor(current));
      if (youtubeStep >= steps) clearInterval(youtubeTimer);
    }, interval);
    let trendsStep = 0;
    const trendsIncrement = googleTrendsData.targetScore / steps;
    const trendsTimer = setInterval(() => {
      trendsStep++;
      const current = Math.min(googleTrendsData.targetScore, trendsIncrement * trendsStep);
      setGoogleTrends(Math.floor(current));
      if (trendsStep >= steps) clearInterval(trendsTimer);
    }, interval);
    return () => {
      clearInterval(youtubeTimer);
      clearInterval(trendsTimer);
    };
  }, []);

  const getSentimentLabel = (score: number) => {
    if (score > 20) return 'Positive';
    if (score <= -20) return 'Negative';
    return 'Neutral';
  };

  const getSentimentColor = (score: number) => {
    if (score > 20) return '#10b981';
    if (score <= -20) return '#ef4444';
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
                    <motion.div
                      key={currentRedditPostIndex}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      transition={{ duration: 0.3 }}
                    >
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
                          <Typography variant="caption" color="text.secondary">•</Typography>
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
                    </motion.div>
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
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                        Trending Keyword:
                      </Typography>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        {googleTrendsData.keyword}
                      </Typography>
                    </Box>
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

