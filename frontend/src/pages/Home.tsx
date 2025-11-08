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
  SmartToy as SmartToyIcon,
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
                      borderRadius: 1,
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
                      borderRadius: 1,
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        boxShadow: '0 30px 80px rgba(37, 99, 235, 0.3)',
                      },
                    }}
                  >
                    <CardContent sx={{ p: 4 }}>
                      <Typography variant="h4" gutterBottom sx={{ fontWeight: 700, mb: 3 }}>
                        Our Approach
                      </Typography>
                      <Typography variant="body1" sx={{ mb: 3, lineHeight: 1.8, fontSize: '1.1rem' }}>
                        We combine <strong>rigorous backtesting</strong> with <strong>real-time signal generation</strong> to deliver 
                        actionable insights. Every signal is tested against historical data to ensure reliability and performance.
                      </Typography>
                      <Typography variant="body1" sx={{ lineHeight: 1.8, fontSize: '1.1rem' }}>
                        Our platform processes millions of data points daily, using AI to identify patterns and correlations 
                        that traditional analysis misses. The result? Signals that give you an edge in today's fast-moving markets.
                      </Typography>
                    </CardContent>
                  </Card>
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
