/**
 * Home Page - Premium Animated Version
 * Ultra-polished landing page with Netflix/Apple/Spotify-level animations
 */

import React, { useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Container,
  Button,
  Chip,
  Paper,
} from '@mui/material';
import {
  Launch as LaunchIcon,
  ArrowForward as ArrowForwardIcon,
  DataObject as DataObjectIcon,
  Category as CategoryIcon,
  Speed as SpeedIcon,
  Analytics as AnalyticsIcon,
  Security as SecurityIcon,
  TrendingUp as TrendingUpIcon,
  AutoAwesome as AutoAwesomeIcon,
  PrecisionManufacturing as PrecisionManufacturingIcon,
  ShowChart as ShowChartIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import AnimatedBackground from '@/components/common/AnimatedBackground';
import GradientMesh from '@/components/common/GradientMesh';
import { useTheme } from '@/contexts/ThemeContext';
import SectorsSection from '@/components/sectors/SectorsSection';
import { LiveNewsPreview } from '@/components/news/LiveNewsPreview';
import { OurSignalsSection } from '@/components/home/OurSignalsSection';
import { DiscordIcon } from '@/components/common/DiscordIcon';
import { CONFIG } from '@/components/home/constants';
import { fadeInUp, staggerContainer, scaleIn } from '@/components/home/animations';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const { isDarkMode } = useTheme();
  const heroRef = useRef<HTMLDivElement>(null);

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
        <Container
          maxWidth="xl"
          sx={{
            position: 'relative',
            zIndex: 3,
            px: { xs: 3, md: 4 },
          }}
        >
          {/* Header Section - Compact */}
          <Box sx={{ mb: 6, textAlign: 'center' }}>
            <motion.div
              initial="hidden"
              animate="visible"
              variants={staggerContainer}
            >
              <motion.div variants={fadeInUp}>
                <Chip
                  label="Quantitative Trading Platform"
                  sx={{
                    mb: 2,
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

              <motion.div variants={fadeInUp}>
                <Typography
                  variant="h1"
                  sx={{
                    fontSize: { xs: '2.5rem', md: '4rem', lg: '5rem' },
                    fontWeight: 900,
                    mb: 2,
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
                    }}
                  >
                    Alternative Data
                  </Box>
                  {' '}Meets{' '}
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
                  {' '}
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

              <motion.div variants={fadeInUp}>
                <Typography
                  variant="h6"
                  sx={{
                    mb: 4,
                    color: 'rgba(255, 255, 255, 0.85)',
                    fontWeight: 400,
                    lineHeight: 1.6,
                    fontSize: { xs: '1rem', md: '1.15rem' },
                    textShadow: '0 1px 3px rgba(0, 0, 0, 0.2)',
                    maxWidth: '800px',
                    mx: 'auto',
                  }}
                >
                  Transform alternative data into sector-based trading signals through AI analysis.
                </Typography>
              </motion.div>

              <motion.div variants={fadeInUp}>
                <Box
                  sx={{
                    display: 'flex',
                    gap: 2,
                    flexWrap: 'wrap',
                    justifyContent: 'center',
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
                        boxShadow: '0 4px 12px rgba(37, 99, 235, 0.15)',
                        '&:hover': {
                          background: 'linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%)',
                          boxShadow: '0 6px 16px rgba(37, 99, 235, 0.2)',
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
                          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
                        },
                      }}
                    >
                      Join Discord
                    </Button>
                  </motion.div>
                </Box>
              </motion.div>
            </motion.div>
          </Box>

          {/* Center Piece - Animated Flow Diagram */}
          <Box sx={{ width: '100%', display: 'flex', justifyContent: 'center', mb: 4 }}>
            <motion.div
              initial="hidden"
              animate="visible"
              variants={staggerContainer}
              style={{ position: 'relative', width: '100%', maxWidth: '1200px' }}
            >
              <Box
                sx={{
                  position: 'relative',
                  width: '100%',
                  height: { xs: '500px', md: '600px' },
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                {/* Stage 1: Sectors */}
                <Box
                  sx={{
                    position: 'absolute',
                    left: { xs: '22%', md: '22%' },
                    top: '50%',
                    transform: 'translate(-50%, -50%)',
                  }}
                >
                  <motion.div
                    initial={{ opacity: 0, x: -100 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                  >
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    {['Video Games', 'Movies', 'Sports'].map((sector, i) => (
                      <motion.div
                        key={sector}
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.5, delay: 0.3 + i * 0.15 }}
                        whileHover={{ scale: 1.05 }}
                      >
                        <Box
                          sx={{
                            width: { xs: 140, md: 180 },
                            py: 2,
                            px: 2.5,
                            borderRadius: 2,
                            background: 'linear-gradient(135deg, rgba(52, 211, 153, 0.3) 0%, rgba(96, 165, 250, 0.3) 100%)',
                            backdropFilter: 'blur(20px)',
                            border: '2px solid rgba(52, 211, 153, 0.5)',
                            display: 'flex',
                            alignItems: 'center',
                            gap: 1.5,
                            boxShadow: '0 2px 8px rgba(52, 211, 153, 0.15)',
                          }}
                        >
                          <CategoryIcon sx={{ fontSize: { xs: 24, md: 28 }, color: '#34d399' }} />
                          <Typography
                            variant="body2"
                            sx={{
                              color: '#ffffff',
                              fontWeight: 600,
                              fontSize: { xs: '0.75rem', md: '0.875rem' },
                            }}
                          >
                            {sector}
                          </Typography>
                        </Box>
                      </motion.div>
                    ))}
                  </Box>
                  </motion.div>
                </Box>

                {/* Floating data points - flowing from Sectors to AI Processing */}
                {[...Array(6)].map((_, i) => (
                  <Box
                    key={`sector-to-ai-${i}`}
                    component={motion.div}
                    initial={{ opacity: 0, scale: 0 }}
                    animate={{
                      opacity: [0, 1, 1, 0.6, 0, 0, 0],
                      scale: [0, 1, 1, 0.9, 0.5, 0, 0],
                      x: [0, 60, 90, 110, 130, 130, 130],
                      y: [0, -20 + (i % 3) * 12, -25 + (i % 3) * 15, -30 + (i % 3) * 18, -30 + (i % 3) * 18, -30 + (i % 3) * 18, -30 + (i % 3) * 18],
                    }}
                    transition={{
                      duration: 8,
                      repeat: Infinity,
                      repeatDelay: 25,
                      delay: i * 0.5,
                      ease: 'linear',
                      times: [0, 0.15, 0.35, 0.525, 0.55, 0.7, 1],
                    }}
                    sx={{
                      position: 'absolute',
                      left: { xs: '28%', md: '29%' },
                      top: '50%',
                      transform: 'translateY(-50%)',
                      zIndex: 1,
                    }}
                  >
                    <Box
                      component={motion.div}
                      initial={{
                        background: 'linear-gradient(135deg, #34d399 0%, #34d399 100%)',
                        boxShadow: '0 0 2px rgba(52, 211, 153, 0.2)',
                      }}
                      animate={{
                        background: [
                          'linear-gradient(135deg, #34d399 0%, #34d399 100%)',
                          'linear-gradient(135deg, #34d399 0%, #34d399 100%)',
                          'linear-gradient(135deg, #34d399 0%, #34d399 100%)',
                          'linear-gradient(135deg, #34d399 40%, #a78bfa 60%)',
                          'linear-gradient(135deg, #a78bfa 0%, #a78bfa 100%)',
                          'linear-gradient(135deg, #a78bfa 0%, #a78bfa 100%)',
                          'linear-gradient(135deg, #34d399 0%, #34d399 100%)',
                        ],
                        boxShadow: [
                          '0 0 2px rgba(52, 211, 153, 0.2)',
                          '0 0 2px rgba(52, 211, 153, 0.2)',
                          '0 0 2px rgba(52, 211, 153, 0.2)',
                          '0 0 2px rgba(52, 211, 153, 0.15), 0 0 2px rgba(167, 139, 250, 0.15)',
                          '0 0 2px rgba(167, 139, 250, 0.2)',
                          '0 0 2px rgba(167, 139, 250, 0.2)',
                          '0 0 2px rgba(52, 211, 153, 0.2)',
                        ],
                      }}
                      transition={{
                        duration: 8,
                        repeat: Infinity,
                        repeatDelay: 25,
                        delay: i * 0.5,
                        ease: 'linear',
                        times: [0, 0.15, 0.35, 0.525, 0.55, 0.7, 1],
                      }}
                      sx={{
                        width: 6,
                        height: 6,
                        borderRadius: '50%',
                        background: 'linear-gradient(135deg, #34d399 0%, #34d399 100%)',
                        boxShadow: '0 0 2px rgba(52, 211, 153, 0.2)',
                      }}
                    />
                  </Box>
                ))}

                {/* Arrow 1: Sectors to Alternative Data */}
                <Box
                  sx={{
                    position: 'absolute',
                    left: { xs: '36%', md: '36%' },
                    top: '50%',
                    width: { xs: '10%', md: '12%' },
                    height: '2px',
                    transform: 'translateY(-50%)',
                  }}
                >
                  <motion.svg
                    initial={{ pathLength: 0, opacity: 0 }}
                    animate={{ pathLength: 1, opacity: 1 }}
                    transition={{ duration: 1, delay: 0.8 }}
                    style={{ width: '100%', height: '100%' }}
                  >
                  <defs>
                    <linearGradient id="arrowGradient1" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stopColor="#34d399" stopOpacity={0} />
                      <stop offset="50%" stopColor="#34d399" stopOpacity={0.8} />
                      <stop offset="100%" stopColor="#60a5fa" stopOpacity={0.8} />
                    </linearGradient>
                    <marker
                      id="arrowhead1"
                      markerWidth="10"
                      markerHeight="10"
                      refX="9"
                      refY="3"
                      orient="auto"
                    >
                      <polygon points="0 0, 10 3, 0 6" fill="#60a5fa" />
                    </marker>
                  </defs>
                  <line
                    x1="0"
                    y1="0"
                    x2="100%"
                    y2="0"
                    stroke="url(#arrowGradient1)"
                    strokeWidth="3"
                    markerEnd="url(#arrowhead1)"
                  />
                  </motion.svg>
                </Box>

                {/* Stage 2: Alternative Data (Multiple sources per sector) - AI Processing Container */}
                <Box
                  sx={{
                    position: 'absolute',
                    left: { xs: '50%', md: '50%' },
                    top: '50%',
                    transform: 'translate(-50%, -50%)',
                  }}
                >
                  <Box
                    component={motion.div}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.8, delay: 1 }}
                    sx={{ position: 'relative' }}
                  >
                    {/* AI Processing Container Box */}
                    <Box
                      component={motion.div}
                      animate={{
                        boxShadow: [
                          '0 0 8px rgba(167, 139, 250, 0.1)',
                          '0 0 12px rgba(167, 139, 250, 0.15)',
                          '0 0 8px rgba(167, 139, 250, 0.1)',
                          '0 0 8px rgba(167, 139, 250, 0.1)',
                          '0 0 8px rgba(167, 139, 250, 0.1)',
                          '0 0 12px rgba(167, 139, 250, 0.15)',
                          '0 0 8px rgba(167, 139, 250, 0.1)',
                          '0 0 8px rgba(167, 139, 250, 0.1)',
                        ],
                        borderColor: [
                          'rgba(167, 139, 250, 0.3)',
                          'rgba(167, 139, 250, 0.5)',
                          'rgba(167, 139, 250, 0.3)',
                          'rgba(167, 139, 250, 0.3)',
                          'rgba(167, 139, 250, 0.3)',
                          'rgba(167, 139, 250, 0.5)',
                          'rgba(167, 139, 250, 0.3)',
                          'rgba(167, 139, 250, 0.3)',
                        ],
                      }}
                      transition={{
                        duration: 33,
                        repeat: Infinity,
                        ease: 'easeInOut',
                        times: [0, 0.15, 0.318, 0.318, 0.424, 0.55, 0.742, 0.742, 1],
                      }}
                      sx={{
                        position: 'relative',
                        p: 3,
                        borderRadius: 3,
                        backdropFilter: 'blur(20px)',
                        background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(236, 72, 153, 0.1) 100%)',
                        border: '2px solid rgba(167, 139, 250, 0.3)',
                        minWidth: { xs: 180, md: 220 },
                        overflow: 'hidden',
                        '&::before': {
                          content: '""',
                          position: 'absolute',
                          top: -2,
                          left: -2,
                          right: -2,
                          bottom: -2,
                          borderRadius: 3,
                          background: 'linear-gradient(135deg, rgba(167, 139, 250, 0.2), rgba(236, 72, 153, 0.2), rgba(167, 139, 250, 0.2))',
                          backgroundSize: '200% 200%',
                          WebkitMask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
                          WebkitMaskComposite: 'xor',
                          maskComposite: 'exclude',
                          animation: 'shimmer 6s ease-in-out infinite',
                          zIndex: -1,
                        },
                        '&::after': {
                          content: '""',
                          position: 'absolute',
                          top: '50%',
                          left: '50%',
                          transform: 'translate(-50%, -50%)',
                          width: '100%',
                          height: '100%',
                          borderRadius: 3,
                          background: 'radial-gradient(circle, rgba(167, 139, 250, 0.04) 0%, transparent 70%)',
                          animation: 'pulseGlow 5s ease-in-out infinite',
                          zIndex: 0,
                          pointerEvents: 'none',
                        },
                        '@keyframes pulseGlow': {
                          '0%, 100%': {
                            opacity: 0.1,
                            transform: 'translate(-50%, -50%)',
                          },
                          '50%': {
                            opacity: 0.2,
                            transform: 'translate(-50%, -50%)',
                          },
                        },
                        '@keyframes shimmer': {
                          '0%': {
                            backgroundPosition: '0% 50%',
                          },
                          '50%': {
                            backgroundPosition: '100% 50%',
                          },
                          '100%': {
                            backgroundPosition: '0% 50%',
                          },
                        },
                      }}
                    >
                      {/* Alternative Data Boxes */}
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5, alignItems: 'center', pt: 0.5, position: 'relative', zIndex: 1 }}>
                        {['Social', 'News', 'Traffic'].map((dataType, i) => (
                          <motion.div
                            key={dataType}
                            initial={{ opacity: 0, y: -20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5, delay: 1.2 + i * 0.15 }}
                          >
                            <Box
                              sx={{
                                width: { xs: 100, md: 130 },
                                py: 1.5,
                                px: 2,
                                borderRadius: 2,
                                background: 'linear-gradient(135deg, rgba(96, 165, 250, 0.3) 0%, rgba(167, 139, 250, 0.3) 100%)',
                                backdropFilter: 'blur(20px)',
                                border: '2px solid rgba(96, 165, 250, 0.5)',
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                gap: 0.5,
                                boxShadow: '0 2px 8px rgba(96, 165, 250, 0.15)',
                              }}
                            >
                              <DataObjectIcon sx={{ fontSize: { xs: 20, md: 24 }, color: '#60a5fa' }} />
                              <Typography
                                variant="caption"
                                sx={{
                                  color: '#ffffff',
                                  fontWeight: 600,
                                  fontSize: { xs: '0.65rem', md: '0.7rem' },
                                }}
                              >
                                {dataType}
                              </Typography>
                            </Box>
                          </motion.div>
                        ))}
                      </Box>
                    </Box>
                  </Box>
                </Box>

                {/* Floating data points - flowing from AI Processing to Trading Signals */}
                {[...Array(6)].map((_, i) => (
                  <Box
                    key={i}
                    component={motion.div}
                    initial={{ opacity: 0, scale: 0 }}
                    animate={{
                      opacity: [0, 0, 0, 1, 0.8, 0.3, 0],
                      scale: [0, 0, 0, 1, 1, 0.8, 0],
                      x: [0, 0, 0, 45, 80, 100, 100],
                      y: [0, 0, 0, -20 + (i % 3) * 12, -25 + (i % 3) * 15, -30 + (i % 3) * 18, -30 + (i % 3) * 18],
                    }}
                    transition={{
                      duration: 8,
                      repeat: Infinity,
                      repeatDelay: 25,
                      delay: 14 + i * 0.5,
                      ease: 'linear',
                    }}
                    sx={{
                      position: 'absolute',
                      left: { xs: '58%', md: '60%' },
                      top: '50%',
                      transform: 'translateY(-50%)',
                      zIndex: 1,
                    }}
                  >
                    <Box
                      component={motion.div}
                      initial={{
                        background: 'linear-gradient(135deg, #a78bfa 0%, #a78bfa 100%)',
                        boxShadow: '0 0 2px rgba(167, 139, 250, 0.2)',
                      }}
                      animate={{
                        background: [
                          'linear-gradient(135deg, #a78bfa 0%, #a78bfa 100%)',
                          'linear-gradient(135deg, #a78bfa 0%, #a78bfa 100%)',
                          'linear-gradient(135deg, #a78bfa 0%, #a78bfa 100%)',
                          'linear-gradient(135deg, #a78bfa 0%, #a78bfa 100%)',
                          'linear-gradient(135deg, #a78bfa 0%, #a78bfa 100%)',
                          'linear-gradient(135deg, #a78bfa 70%, #34d399 30%)',
                          'linear-gradient(135deg, #34d399 0%, #34d399 100%)',
                        ],
                        boxShadow: [
                          '0 0 2px rgba(167, 139, 250, 0.2)',
                          '0 0 2px rgba(167, 139, 250, 0.2)',
                          '0 0 2px rgba(167, 139, 250, 0.2)',
                          '0 0 2px rgba(167, 139, 250, 0.2)',
                          '0 0 2px rgba(167, 139, 250, 0.2)',
                          '0 0 2px rgba(167, 139, 250, 0.15), 0 0 2px rgba(52, 211, 153, 0.15)',
                          '0 0 2px rgba(52, 211, 153, 0.2)',
                        ],
                      }}
                      transition={{
                        duration: 8,
                        repeat: Infinity,
                        repeatDelay: 25,
                        delay: 14 + i * 0.5,
                        ease: 'linear',
                      }}
                      sx={{
                        width: 6,
                        height: 6,
                        borderRadius: '50%',
                        background: 'linear-gradient(135deg, #a78bfa 0%, #a78bfa 100%)',
                        boxShadow: '0 0 2px rgba(167, 139, 250, 0.2)',
                      }}
                    />
                  </Box>
                ))}


                {/* Stage 4: Signals (Graphs) */}
                <Box
                  sx={{
                    position: 'absolute',
                    left: { xs: '75%', md: '78%' },
                    top: '50%',
                    transform: 'translate(-50%, -50%)',
                  }}
                >
                  <motion.div
                    initial={{ opacity: 0, x: 100 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.8, delay: 2.6 }}
                  >
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    {[1, 2, 3].map((_, i) => (
                      <motion.div
                        key={i}
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.5, delay: 2.8 + i * 0.2 }}
                        whileHover={{ scale: 1.05 }}
                      >
                        <Box
                          sx={{
                            width: { xs: 140, md: 180 },
                            height: { xs: 80, md: 100 },
                            borderRadius: 2,
                            background: 'linear-gradient(135deg, rgba(52, 211, 153, 0.3) 0%, rgba(96, 165, 250, 0.3) 100%)',
                            backdropFilter: 'blur(20px)',
                            border: '2px solid rgba(52, 211, 153, 0.5)',
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: 1,
                            boxShadow: '0 2px 8px rgba(52, 211, 153, 0.15)',
                            position: 'relative',
                            overflow: 'hidden',
                          }}
                        >
                          <ShowChartIcon sx={{ fontSize: { xs: 32, md: 40 }, color: '#34d399' }} />
                          <Typography
                            variant="caption"
                            sx={{
                              color: '#ffffff',
                              fontWeight: 600,
                              fontSize: { xs: '0.65rem', md: '0.7rem' },
                            }}
                          >
                            Trading Signal
                          </Typography>
                          {/* Animated graph line */}
                          <Box
                            component="svg"
                            sx={{
                              position: 'absolute',
                              bottom: 8,
                              left: 8,
                              right: 8,
                              height: 30,
                              opacity: 0.6,
                            }}
                          >
                            <motion.path
                              d={
                                i === 0
                                  ? "M 0,20 L 20,15 L 40,18 L 60,12 L 80,16 L 100,14 L 120,17 L 140,13 L 160,15"
                                  : i === 1
                                  ? "M 0,15 Q 30,25 60,20 Q 90,15 120,22 Q 150,18 160,20"
                                  : "M 0,22 L 25,18 L 50,25 L 75,16 L 100,23 L 125,17 L 150,20 L 160,19"
                              }
                              fill="none"
                              stroke="#34d399"
                              strokeWidth="2"
                              initial={{ pathLength: 0 }}
                              animate={{ pathLength: 1 }}
                              transition={{ duration: 2, delay: 24.5 + i * 0.3, repeat: Infinity, repeatDelay: 31 }}
                            />
                          </Box>
                        </Box>
                      </motion.div>
                    ))}
                  </Box>
                  </motion.div>
                </Box>
              </Box>
            </motion.div>
          </Box>
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

      {/* About Alpha Crucible Section */}
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
            {/* Section Header */}
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
                About Alpha Crucible
              </Typography>
              <Typography
                variant="h6"
                align="center"
                sx={{
                  mb: 6,
                  color: 'text.secondary',
                  maxWidth: '700px',
                  mx: 'auto',
                  lineHeight: 1.7,
                }}
              >
                Transforming alternative data into actionable trading signals through sector-focused AI analysis
              </Typography>
            </motion.div>

            {/* Mission & Vision Cards */}
            <Grid container spacing={4} sx={{ mb: 6 }}>
              <Grid item xs={12} md={6}>
                <motion.div
                  variants={scaleIn}
                  whileHover={{ y: -8, transition: { duration: 0.3 } }}
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
                      borderRadius: 2,
                      transition: 'all 0.3s ease',
                      position: 'relative',
                      overflow: 'hidden',
                      '&:hover': {
                        boxShadow: '0 30px 80px rgba(37, 99, 235, 0.3)',
                        borderColor: 'primary.main',
                      },
                      '&::before': {
                        content: '""',
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        height: '4px',
                        background: 'linear-gradient(90deg, #60a5fa 0%, #a78bfa 100%)',
                      },
                    }}
                  >
                    <CardContent sx={{ p: 4 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
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
                          <AutoAwesomeIcon sx={{ fontSize: 32, color: '#ffffff' }} />
                        </Box>
                        <Typography variant="h4" sx={{ fontWeight: 700 }}>
                          Our Mission
                        </Typography>
                      </Box>
                      <Typography variant="body1" sx={{ mb: 2, lineHeight: 1.8, fontSize: '1.05rem' }}>
                        Alpha Crucible revolutionizes quantitative trading by combining <strong>sector-specific intelligence</strong>, 
                        <strong> alternative data integration</strong>, and <strong>AI-powered signal processing</strong> to deliver 
                        insights that traditional analysis cannot provide.
                      </Typography>
                      <Typography variant="body1" sx={{ lineHeight: 1.8, fontSize: '1.05rem', color: 'text.secondary' }}>
                        While traditional analysis relies on price and volume data available to everyone, we process millions of 
                        alternative data points—social sentiment, news flow, web traffic patterns, and more—using advanced AI 
                        algorithms to extract meaningful, actionable signals tailored to specific industries.
                      </Typography>
                    </CardContent>
                  </Card>
                </motion.div>
              </Grid>
              <Grid item xs={12} md={6}>
                <motion.div
                  variants={scaleIn}
                  whileHover={{ y: -8, transition: { duration: 0.3 } }}
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
                      borderRadius: 2,
                      transition: 'all 0.3s ease',
                      position: 'relative',
                      overflow: 'hidden',
                      '&:hover': {
                        boxShadow: '0 30px 80px rgba(16, 185, 129, 0.3)',
                        borderColor: 'success.main',
                      },
                      '&::before': {
                        content: '""',
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        height: '4px',
                        background: 'linear-gradient(90deg, #34d399 0%, #60a5fa 100%)',
                      },
                    }}
                  >
                    <CardContent sx={{ p: 4 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
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
                          <TrendingUpIcon sx={{ fontSize: 32, color: '#ffffff' }} />
                        </Box>
                        <Typography variant="h4" sx={{ fontWeight: 700 }}>
                          Our Approach
                        </Typography>
                      </Box>
                      <Typography variant="body1" sx={{ mb: 2, lineHeight: 1.8, fontSize: '1.05rem' }}>
                        We combine <strong>rigorous backtesting</strong> with <strong>real-time signal generation</strong> to ensure 
                        every strategy is validated against historical data before deployment. Our CVXOPT-based portfolio optimization 
                        engine delivers mathematically sound allocations.
                      </Typography>
                      <Typography variant="body1" sx={{ lineHeight: 1.8, fontSize: '1.05rem', color: 'text.secondary' }}>
                        The platform processes millions of data points daily, using AI to identify patterns and correlations invisible 
                        to traditional analysis. Every signal undergoes comprehensive backtesting, giving you confidence in today's 
                        fast-moving markets.
                      </Typography>
                    </CardContent>
                  </Card>
                </motion.div>
              </Grid>
            </Grid>

            {/* Key Features Grid */}
            <motion.div variants={fadeInUp}>
              <Typography
                variant="h4"
                align="center"
                sx={{
                  fontWeight: 700,
                  mb: 4,
                  color: 'text.primary',
                }}
              >
                What Sets Us Apart
              </Typography>
            </motion.div>

            <Grid container spacing={4}>
              <Grid item xs={12} sm={6} md={4}>
                <motion.div
                  variants={fadeInUp}
                  whileHover={{ y: -5, transition: { duration: 0.2 } }}
                >
                  <Paper
                    elevation={0}
                    sx={{
                      p: 3,
                      height: '100%',
                      background: isDarkMode
                        ? 'rgba(30, 41, 59, 0.6)'
                        : 'rgba(255, 255, 255, 0.8)',
                      backdropFilter: 'blur(10px)',
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: 2,
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        borderColor: 'primary.main',
                        boxShadow: '0 10px 30px rgba(37, 99, 235, 0.2)',
                      },
                    }}
                  >
                    <Box
                      sx={{
                        width: 48,
                        height: 48,
                        borderRadius: 1.5,
                        background: 'linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        mb: 2,
                      }}
                    >
                      <SpeedIcon sx={{ fontSize: 24, color: '#ffffff' }} />
                    </Box>
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 1.5 }}>
                      Real-Time Processing
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'text.secondary', lineHeight: 1.7 }}>
                      Process millions of data points daily with sub-second latency, ensuring you never miss a critical signal.
                    </Typography>
                  </Paper>
                </motion.div>
              </Grid>

              <Grid item xs={12} sm={6} md={4}>
                <motion.div
                  variants={fadeInUp}
                  whileHover={{ y: -5, transition: { duration: 0.2 } }}
                >
                  <Paper
                    elevation={0}
                    sx={{
                      p: 3,
                      height: '100%',
                      background: isDarkMode
                        ? 'rgba(30, 41, 59, 0.6)'
                        : 'rgba(255, 255, 255, 0.8)',
                      backdropFilter: 'blur(10px)',
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: 2,
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        borderColor: 'success.main',
                        boxShadow: '0 10px 30px rgba(16, 185, 129, 0.2)',
                      },
                    }}
                  >
                    <Box
                      sx={{
                        width: 48,
                        height: 48,
                        borderRadius: 1.5,
                        background: 'linear-gradient(135deg, #34d399 0%, #60a5fa 100%)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        mb: 2,
                      }}
                    >
                      <AnalyticsIcon sx={{ fontSize: 24, color: '#ffffff' }} />
                    </Box>
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 1.5 }}>
                      Rigorous Backtesting
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'text.secondary', lineHeight: 1.7 }}>
                      Every signal is validated against historical data with comprehensive performance metrics and risk analysis.
                    </Typography>
                  </Paper>
                </motion.div>
              </Grid>

              <Grid item xs={12} sm={6} md={4}>
                <motion.div
                  variants={fadeInUp}
                  whileHover={{ y: -5, transition: { duration: 0.2 } }}
                >
                  <Paper
                    elevation={0}
                    sx={{
                      p: 3,
                      height: '100%',
                      background: isDarkMode
                        ? 'rgba(30, 41, 59, 0.6)'
                        : 'rgba(255, 255, 255, 0.8)',
                      backdropFilter: 'blur(10px)',
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: 2,
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        borderColor: 'secondary.main',
                        boxShadow: '0 10px 30px rgba(139, 92, 246, 0.2)',
                      },
                    }}
                  >
                    <Box
                      sx={{
                        width: 48,
                        height: 48,
                        borderRadius: 1.5,
                        background: 'linear-gradient(135deg, #a78bfa 0%, #f472b6 100%)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        mb: 2,
                      }}
                    >
                      <PrecisionManufacturingIcon sx={{ fontSize: 24, color: '#ffffff' }} />
                    </Box>
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 1.5 }}>
                      Portfolio Optimization
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'text.secondary', lineHeight: 1.7 }}>
                      CVXOPT-based optimization engine delivers mathematically sound portfolio allocations with risk-adjusted returns.
                    </Typography>
                  </Paper>
                </motion.div>
              </Grid>

              <Grid item xs={12} sm={6} md={4}>
                <motion.div
                  variants={fadeInUp}
                  whileHover={{ y: -5, transition: { duration: 0.2 } }}
                >
                  <Paper
                    elevation={0}
                    sx={{
                      p: 3,
                      height: '100%',
                      background: isDarkMode
                        ? 'rgba(30, 41, 59, 0.6)'
                        : 'rgba(255, 255, 255, 0.8)',
                      backdropFilter: 'blur(10px)',
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: 2,
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        borderColor: 'primary.main',
                        boxShadow: '0 10px 30px rgba(37, 99, 235, 0.2)',
                      },
                    }}
                  >
                    <Box
                      sx={{
                        width: 48,
                        height: 48,
                        borderRadius: 1.5,
                        background: 'linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        mb: 2,
                      }}
                    >
                      <CategoryIcon sx={{ fontSize: 24, color: '#ffffff' }} />
                    </Box>
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 1.5 }}>
                      Sector-Specific Focus
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'text.secondary', lineHeight: 1.7 }}>
                      Tailored signals for Video Games, Movies, and Sports—each optimized for unique industry dynamics and drivers.
                    </Typography>
                  </Paper>
                </motion.div>
              </Grid>

              <Grid item xs={12} sm={6} md={4}>
                <motion.div
                  variants={fadeInUp}
                  whileHover={{ y: -5, transition: { duration: 0.2 } }}
                >
                  <Paper
                    elevation={0}
                    sx={{
                      p: 3,
                      height: '100%',
                      background: isDarkMode
                        ? 'rgba(30, 41, 59, 0.6)'
                        : 'rgba(255, 255, 255, 0.8)',
                      backdropFilter: 'blur(10px)',
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: 2,
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        borderColor: 'success.main',
                        boxShadow: '0 10px 30px rgba(16, 185, 129, 0.2)',
                      },
                    }}
                  >
                    <Box
                      sx={{
                        width: 48,
                        height: 48,
                        borderRadius: 1.5,
                        background: 'linear-gradient(135deg, #34d399 0%, #60a5fa 100%)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        mb: 2,
                      }}
                    >
                      <DataObjectIcon sx={{ fontSize: 24, color: '#ffffff' }} />
                    </Box>
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 1.5 }}>
                      Alternative Data Sources
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'text.secondary', lineHeight: 1.7 }}>
                      Social sentiment, news flow, web traffic, and more—uncovering insights before they're reflected in the market.
                    </Typography>
                  </Paper>
                </motion.div>
              </Grid>

              <Grid item xs={12} sm={6} md={4}>
                <motion.div
                  variants={fadeInUp}
                  whileHover={{ y: -5, transition: { duration: 0.2 } }}
                >
                  <Paper
                    elevation={0}
                    sx={{
                      p: 3,
                      height: '100%',
                      background: isDarkMode
                        ? 'rgba(30, 41, 59, 0.6)'
                        : 'rgba(255, 255, 255, 0.8)',
                      backdropFilter: 'blur(10px)',
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: 2,
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        borderColor: 'secondary.main',
                        boxShadow: '0 10px 30px rgba(139, 92, 246, 0.2)',
                      },
                    }}
                  >
                    <Box
                      sx={{
                        width: 48,
                        height: 48,
                        borderRadius: 1.5,
                        background: 'linear-gradient(135deg, #a78bfa 0%, #f472b6 100%)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        mb: 2,
                      }}
                    >
                      <SecurityIcon sx={{ fontSize: 24, color: '#ffffff' }} />
                    </Box>
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 1.5 }}>
                      Enterprise-Grade Platform
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'text.secondary', lineHeight: 1.7 }}>
                      Modern React + FastAPI architecture with comprehensive REST API, real-time data integration, and cloud scalability.
                    </Typography>
                  </Paper>
                </motion.div>
              </Grid>
            </Grid>
          </motion.div>
        </Container>
      </Box>
    </Box>
  );
};

export default Home;
