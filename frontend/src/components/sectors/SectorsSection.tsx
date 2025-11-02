/**
 * Sectors Section Component
 * Displays information about our sectors: Video Games, Movies, and Sports
 * Professional design with large images and brief descriptions
 */

import React, { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from 'react-query';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  Button,
} from '@mui/material';
import {
  SportsEsports as GamesIcon,
  Movie as MoviesIcon,
  SportsFootball as SportsIcon,
  ArrowForward as ArrowForwardIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useTheme } from '@/contexts/ThemeContext';
import { universeApi } from '@/services/api';

interface Sector {
  id: string;
  name: string;
  description: string;
  imageUrl?: string;
  gradient: string;
  icon: React.ReactNode;
  comingSoon?: boolean;
  universeName?: string; // Universe name to find (e.g., "GameCore-12" or "MovieCore-8")
}

const SectorsSection: React.FC = () => {
  const { isDarkMode } = useTheme();
  const navigate = useNavigate();

  // Fetch universes to get their IDs
  const { data: universesData } = useQuery(
    'universes-for-sectors',
    () => universeApi.getUniverses(),
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
      refetchOnWindowFocus: false,
    }
  );

  // Find universe IDs for each sector
  const gameCoreUniverse = useMemo(() => {
    if (!universesData) return null;
    return universesData.universes.find(u => 
      u.name.includes('GameCore-12') || u.name.includes('GC-12')
    );
  }, [universesData]);

  const movieCoreUniverse = useMemo(() => {
    if (!universesData) return null;
    return universesData.universes.find(u => 
      u.name.includes('MovieCore-8') || u.name.includes('MC-8')
    );
  }, [universesData]);

  // Define sectors - Video Games, Movies, and Sports
  const sectors: Sector[] = [
    {
      id: 'video-games',
      name: 'Video Games',
      description: 'Analyzing alternative data from game trailers, player engagement metrics, and gaming ecosystem dynamics.',
      imageUrl: '/sectors/gaming.webp',
      gradient: 'linear-gradient(135deg, rgba(16, 185, 129, 0.9) 0%, rgba(6, 182, 212, 0.9) 100%)',
      icon: <GamesIcon sx={{ fontSize: 64 }} />,
      universeName: 'GameCore-12',
    },
    {
      id: 'movies',
      name: 'Movies',
      description: 'Tracking box office performance, streaming metrics, and content release schedules as alternative data signals.',
      imageUrl: '/sectors/movies.png',
      gradient: 'linear-gradient(135deg, rgba(236, 72, 153, 0.9) 0%, rgba(245, 158, 11, 0.9) 100%)',
      icon: <MoviesIcon sx={{ fontSize: 64 }} />,
      universeName: 'MovieCore-8',
    },
    {
      id: 'sports',
      name: 'Sports',
      description: 'Coming soon: Comprehensive analysis of sports-related alternative data and market signals.',
      imageUrl: '/sectors/sports.png',
      gradient: 'linear-gradient(135deg, rgba(37, 99, 235, 0.9) 0%, rgba(59, 130, 246, 0.9) 100%)',
      icon: <SportsIcon sx={{ fontSize: 64 }} />,
      comingSoon: true,
    },
  ];

  // Handle navigation to universe
  const handleNavigateToUniverse = (sector: Sector) => {
    if (sector.comingSoon) {
      navigate('/universes');
      return;
    }

    let universeId: number | null = null;
    if (sector.id === 'video-games' && gameCoreUniverse) {
      universeId = gameCoreUniverse.id;
    } else if (sector.id === 'movies' && movieCoreUniverse) {
      universeId = movieCoreUniverse.id;
    }

    if (universeId) {
      navigate(`/universes/${universeId}`);
    } else {
      // Fallback to universes list if not found
      navigate('/universes');
    }
  };

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
        staggerChildren: 0.15,
        delayChildren: 0.1,
      },
    },
  };

  const scaleIn = {
    hidden: { opacity: 0, scale: 0.95 },
    visible: {
      opacity: 1,
      scale: 1,
      transition: { duration: 0.6, ease: [0.6, -0.05, 0.01, 0.99] },
    },
  };

  return (
    <Box
      sx={{
        py: { xs: 8, md: 14 },
        background: 'transparent',
        position: 'relative',
        zIndex: 1,
      }}
    >
      <Box sx={{ maxWidth: '1400px', mx: 'auto', px: { xs: 2, md: 4 } }}>
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          variants={staggerContainer}
        >
          {/* Header */}
          <motion.div variants={fadeInUp}>
            <Box sx={{ textAlign: 'center', mb: { xs: 6, md: 10 } }}>
              <Typography
                variant="h2"
                sx={{
                  fontWeight: 800,
                  mb: 2,
                  fontSize: { xs: '2rem', md: '3rem' },
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
                sx={{ 
                  maxWidth: 700, 
                  mx: 'auto', 
                  lineHeight: 1.7,
                  fontSize: { xs: '0.95rem', md: '1.1rem' },
                }}
              >
                Three core entertainment sectors powered by alternative data analysis
              </Typography>
            </Box>
          </motion.div>

          {/* Sectors Grid */}
          <Grid container spacing={{ xs: 4, md: 5 }}>
            {sectors.map((sector, index) => (
              <Grid item xs={12} md={4} key={sector.id}>
                <motion.div
                  variants={scaleIn}
                  whileHover={{
                    y: -8,
                    scale: 1.02,
                    transition: { duration: 0.3 },
                  }}
                >
                  <Card
                    sx={{
                      height: '100%',
                      position: 'relative',
                      overflow: 'hidden',
                      borderRadius: { xs: 2, md: 3 },
                      background: 'transparent',
                      border: 'none',
                      boxShadow: 'none',
                      cursor: sector.comingSoon ? 'default' : 'pointer',
                      transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                      '&:hover': {
                        '& .sector-image': {
                          transform: 'scale(1.05)',
                          '& img': {
                            filter: 'blur(0px) !important',
                          },
                        },
                        '& .sector-overlay': {
                          background: 'transparent !important',
                        },
                      },
                    }}
                  >
                    {/* Large Image Container */}
                    <Box
                      className="sector-image"
                      sx={{
                        position: 'relative',
                        width: '100%',
                        height: { xs: 320, md: 420 },
                        borderRadius: { xs: 2, md: 3 },
                        overflow: 'hidden',
                        background: sector.gradient,
                        transition: 'transform 0.6s cubic-bezier(0.4, 0, 0.2, 1)',
                        '&::before': {
                          content: '""',
                          position: 'absolute',
                          top: 0,
                          left: 0,
                          right: 0,
                          bottom: 0,
                          background: sector.imageUrl 
                            ? (sector.id === 'video-games' 
                                ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.6) 0%, rgba(6, 182, 212, 0.6) 100%)'
                                : sector.id === 'movies'
                                ? 'linear-gradient(135deg, rgba(236, 72, 153, 0.6) 0%, rgba(245, 158, 11, 0.6) 100%)'
                                : 'linear-gradient(135deg, rgba(37, 99, 235, 0.6) 0%, rgba(59, 130, 246, 0.6) 100%)')
                            : sector.gradient,
                          zIndex: 1,
                        },
                      }}
                    >
                      {/* Background Image */}
                      {sector.imageUrl && (
                        <Box
                          component="img"
                          src={sector.imageUrl}
                          alt={sector.name}
                          className="sector-image-img"
                          sx={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover',
                            zIndex: 0,
                            filter: 'blur(2px)',
                            transition: 'filter 0.6s cubic-bezier(0.4, 0, 0.2, 1)',
                          }}
                          onError={(e) => {
                            // If image fails to load, hide it and show gradient only
                            e.currentTarget.style.display = 'none';
                          }}
                        />
                      )}

                      {/* Gradient Overlay - Almost completely transparent, disappears on hover */}
                      <Box
                        className="sector-overlay"
                        sx={{
                          position: 'absolute',
                          top: 0,
                          left: 0,
                          right: 0,
                          bottom: 0,
                          background: sector.imageUrl 
                            ? (sector.id === 'video-games' 
                                ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.02) 0%, rgba(6, 182, 212, 0.03) 100%), linear-gradient(to bottom, rgba(0, 0, 0, 0.02) 0%, rgba(0, 0, 0, 0.03) 100%)'
                                : sector.id === 'movies'
                                ? 'linear-gradient(135deg, rgba(236, 72, 153, 0.02) 0%, rgba(245, 158, 11, 0.03) 100%), linear-gradient(to bottom, rgba(0, 0, 0, 0.02) 0%, rgba(0, 0, 0, 0.03) 100%)'
                                : 'linear-gradient(135deg, rgba(37, 99, 235, 0.02) 0%, rgba(59, 130, 246, 0.03) 100%), linear-gradient(to bottom, rgba(0, 0, 0, 0.02) 0%, rgba(0, 0, 0, 0.03) 100%)')
                            : sector.gradient,
                          zIndex: 2,
                          transition: 'background 0.6s cubic-bezier(0.4, 0, 0.2, 1)',
                        }}
                      />

                      {/* Fallback gradient pattern when no image */}
                      {!sector.imageUrl && (
                        <Box
                          sx={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            width: '100%',
                            height: '100%',
                            background: `radial-gradient(circle at 30% 50%, rgba(255, 255, 255, 0.1) 0%, transparent 50%), ${sector.gradient}`,
                            zIndex: 0,
                          }}
                        />
                      )}

                      {/* Icon */}
                      <Box
                        sx={{
                          position: 'absolute',
                          top: '50%',
                          left: '50%',
                          transform: 'translate(-50%, -50%)',
                          zIndex: 3,
                          color: 'white',
                          opacity: 0.9,
                          filter: 'drop-shadow(0 4px 12px rgba(0, 0, 0, 0.3))',
                        }}
                      >
                        <motion.div
                          animate={{
                            scale: [1, 1.1, 1],
                            opacity: [0.9, 1, 0.9],
                          }}
                          transition={{
                            duration: 3 + index * 0.5,
                            repeat: Infinity,
                            ease: 'easeInOut',
                            delay: index * 0.2,
                          }}
                        >
                          {sector.icon}
                        </motion.div>
                      </Box>

                      {/* Coming Soon Badge */}
                      {sector.comingSoon && (
                        <Box
                          sx={{
                            position: 'absolute',
                            top: 16,
                            right: 16,
                            zIndex: 4,
                          }}
                        >
                          <Chip
                            label="Coming Soon"
                            sx={{
                              background: 'rgba(255, 255, 255, 0.95)',
                              color: '#1e293b',
                              fontWeight: 700,
                              fontSize: '0.75rem',
                              height: 32,
                              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
                              '& .MuiChip-label': {
                                px: 2,
                              },
                            }}
                          />
                        </Box>
                      )}
                    </Box>

                    {/* Content Section */}
                    <CardContent
                      sx={{
                        p: { xs: 3, md: 4 },
                        background: isDarkMode
                          ? 'rgba(15, 23, 42, 0.6)'
                          : 'rgba(255, 255, 255, 0.95)',
                        backdropFilter: 'blur(20px)',
                        borderRadius: { xs: 2, md: 3 },
                        mt: { xs: -2, md: -3 },
                        position: 'relative',
                        zIndex: 5,
                        border: '1px solid',
                        borderColor: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.08)',
                      }}
                    >
                      {/* Title */}
                      <Typography
                        variant="h4"
                        sx={{
                          fontWeight: 700,
                          mb: 1.5,
                          fontSize: { xs: '1.5rem', md: '1.75rem' },
                          color: isDarkMode ? '#f8fafc' : '#0f172a',
                          textAlign: 'center',
                        }}
                      >
                        {sector.name}
                      </Typography>

                      {/* Brief Description */}
                      <Typography
                        variant="body1"
                        sx={{
                          color: isDarkMode ? 'rgba(255, 255, 255, 0.8)' : 'rgba(0, 0, 0, 0.7)',
                          lineHeight: 1.7,
                          fontSize: { xs: '0.9rem', md: '1rem' },
                          fontWeight: 400,
                          mb: 2.5,
                        }}
                      >
                        {sector.description}
                      </Typography>

                      {/* View Universe Link */}
                      <Box sx={{ textAlign: 'center', mt: 2 }}>
                        <Button
                          variant="outlined"
                          endIcon={<ArrowForwardIcon />}
                          onClick={() => handleNavigateToUniverse(sector)}
                          disabled={sector.comingSoon}
                          sx={{
                            textTransform: 'none',
                            fontWeight: 600,
                            borderRadius: 2,
                            px: 3,
                            py: 1,
                            borderWidth: 1.5,
                            borderColor: isDarkMode ? 'rgba(255, 255, 255, 0.3)' : 'rgba(0, 0, 0, 0.3)',
                            color: isDarkMode ? '#f8fafc' : '#0f172a',
                            '&:hover': {
                              borderWidth: 1.5,
                              borderColor: isDarkMode ? 'rgba(255, 255, 255, 0.5)' : 'rgba(0, 0, 0, 0.5)',
                              backgroundColor: isDarkMode ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)',
                              transform: 'translateY(-1px)',
                            },
                            '&:disabled': {
                              opacity: 0.5,
                            },
                          }}
                        >
                          {sector.comingSoon ? 'Coming Soon' : 'View Universe'}
                        </Button>
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

