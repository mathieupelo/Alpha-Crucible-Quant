/**
 * Sectors Section Component
 * Displays information about our sectors: Video Games, Movies, and Entertainment
 */

import React from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
} from '@mui/material';
import {
  SportsEsports as GamesIcon,
  Movie as MoviesIcon,
  TheaterComedy as EntertainmentIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useTheme } from '@/contexts/ThemeContext';

interface Sector {
  id: string;
  name: string;
  icon: React.ReactNode;
  description: string;
  tickers: string[];
  gradient: string;
}

const SectorsSection: React.FC = () => {
  const { isDarkMode } = useTheme();

  // Define sectors - Video Games, Movies, and Entertainment (combination)
  const sectors: Sector[] = [
    {
      id: 'video-games',
      name: 'Video Games',
      icon: <GamesIcon sx={{ fontSize: 48 }} />,
      description: 'Pure-play game developers, gaming platforms, and companies with significant gaming revenue streams. We track alternative data signals from game trailers, player engagement metrics, and gaming ecosystem dynamics.',
      tickers: ['EA', 'TTWO', 'RBLX', 'OTGLF', 'SNAL', 'GRVY', 'GDEV', 'NCBDY'],
      gradient: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
    },
    {
      id: 'movies',
      name: 'Movies',
      icon: <MoviesIcon sx={{ fontSize: 48 }} />,
      description: 'Film studios, production companies, and entertainment distributors. Our analysis incorporates box office performance, streaming metrics, and content release schedules as alternative data signals.',
      tickers: ['WBD', 'SONY'],
      gradient: 'linear-gradient(135deg, #ec4899 0%, #f59e0b 100%)',
    },
    {
      id: 'entertainment',
      name: 'Entertainment',
      icon: <EntertainmentIcon sx={{ fontSize: 48 }} />,
      description: 'The broader entertainment sector combining both video games and movies. This aggregated view captures cross-sector trends, platform convergence, and unified entertainment industry dynamics.',
      tickers: ['MSFT', 'NTES'],
      gradient: 'linear-gradient(135deg, #2563eb 0%, #ec4899 100%)',
    },
  ];

  const fadeInUp = {
    hidden: { opacity: 0, y: 60 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.8, ease: [0.6, -0.05, 0.01, 0.99] },
    },
  };

  const staggerContainer = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
        delayChildren: 0.1,
      },
    },
  };

  const scaleIn = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: {
      opacity: 1,
      scale: 1,
      transition: { duration: 0.6, ease: [0.6, -0.05, 0.01, 0.99] },
    },
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
      <Box sx={{ maxWidth: '1200px', mx: 'auto', px: { xs: 2, md: 4 } }}>
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          variants={staggerContainer}
        >
          {/* Header */}
          <motion.div variants={fadeInUp}>
            <Box sx={{ textAlign: 'center', mb: 8 }}>
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
                Our Sectors
              </Typography>
              <Typography
                variant="h6"
                color="text.secondary"
                sx={{ maxWidth: 800, mx: 'auto', lineHeight: 1.7 }}
              >
                Alpha Crucible focuses on three core entertainment sectors, analyzing alternative data
                sources to generate actionable trading signals across video games, movies, and the broader entertainment ecosystem.
              </Typography>
            </Box>
          </motion.div>

          {/* Sectors Grid */}
          <Grid container spacing={4}>
            {sectors.map((sector, index) => (
              <Grid item xs={12} md={4} key={sector.id}>
                <motion.div
                  variants={scaleIn}
                  whileHover={{
                    y: -10,
                    scale: 1.02,
                    transition: { duration: 0.3 },
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
                      borderRadius: 1, // Minimal border radius
                      position: 'relative',
                      overflow: 'hidden',
                      transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                      '&::before': {
                        content: '""',
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        height: '4px',
                        background: sector.gradient,
                      },
                      '&:hover': {
                        boxShadow: `0 20px 60px ${sector.gradient.split(' ')[0]}40`,
                      },
                    }}
                  >
                    <CardContent sx={{ p: 4 }}>
                      {/* Icon */}
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
                            borderRadius: 3,
                            background: sector.gradient,
                            color: 'white',
                            mb: 3,
                            boxShadow: `0 10px 30px ${sector.gradient.split(' ')[0]}40`,
                          }}
                        >
                          {sector.icon}
                        </Box>
                      </motion.div>

                      {/* Title */}
                      <Typography
                        variant="h4"
                        sx={{
                          fontWeight: 700,
                          mb: 2,
                          background: sector.gradient,
                          backgroundClip: 'text',
                          WebkitBackgroundClip: 'text',
                          WebkitTextFillColor: 'transparent',
                        }}
                      >
                        {sector.name}
                      </Typography>

                      {/* Description */}
                      <Typography
                        variant="body1"
                        color="text.secondary"
                        sx={{ mb: 3, lineHeight: 1.7, minHeight: '80px' }}
                      >
                        {sector.description}
                      </Typography>

                      {/* Tickers */}
                      <Box sx={{ mt: 3 }}>
                        <Typography
                          variant="body2"
                          color="text.secondary"
                          sx={{ mb: 1.5, fontWeight: 600 }}
                        >
                          Key Tickers ({sector.tickers.length}):
                        </Typography>
                        <Box
                          sx={{
                            display: 'flex',
                            flexWrap: 'wrap',
                            gap: 1,
                          }}
                        >
                          {sector.tickers.map((ticker) => (
                            <Chip
                              key={ticker}
                              label={ticker}
                              size="small"
                              sx={{
                                fontWeight: 600,
                                background: isDarkMode
                                  ? 'rgba(37, 99, 235, 0.2)'
                                  : 'rgba(37, 99, 235, 0.1)',
                                border: '1px solid',
                                borderColor: 'primary.main',
                                '&:hover': {
                                  background: isDarkMode
                                    ? 'rgba(37, 99, 235, 0.3)'
                                    : 'rgba(37, 99, 235, 0.15)',
                                },
                              }}
                            />
                          ))}
                        </Box>
                      </Box>
                    </CardContent>
                  </Card>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </motion.div>
      </Box>
    </Box>
  );
};

export default SectorsSection;

