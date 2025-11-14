/**
 * Animated Background Component
 * Creates stunning animated backgrounds with particles and gradients
 * Also includes backtest chart in the background
 */

import React, { useEffect, useRef } from 'react';
import { Box } from '@mui/material';
import { useTheme } from '@/contexts/ThemeContext';
import { useQuery } from 'react-query';
import { backtestApi, navApi } from '@/services/api';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis } from 'recharts';
import { motion } from 'framer-motion';

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  radius: number;
  color: string;
}

const AnimatedBackground: React.FC = () => {
  const { isDarkMode } = useTheme();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const particlesRef = useRef<Particle[]>([]);
  const animationFrameRef = useRef<number>();

  // Fetch most recent backtest for background chart
  const { data: latestBacktestData } = useQuery(
    'latest-backtest-bg',
    () => backtestApi.getBacktests(1, 1),
    {
      staleTime: 5 * 60 * 1000,
      refetchOnWindowFocus: false,
    }
  );

  const latestBacktest = latestBacktestData?.backtests?.[0];
  const latestRunId = latestBacktest?.run_id;

  // Fetch NAV data for the latest backtest
  const { data: latestNavData, isLoading: navLoading } = useQuery(
    ['backtest-nav-bg', latestRunId],
    () => navApi.getBacktestNav(latestRunId!),
    {
      enabled: !!latestRunId,
      staleTime: 5 * 60 * 1000,
      refetchOnWindowFocus: false,
    }
  );


  // Debug: log data availability
  React.useEffect(() => {
    console.log('AnimatedBackground - Chart data status:', {
      hasBacktest: !!latestBacktest,
      runId: latestRunId,
      hasNavData: !!latestNavData,
      navDataLength: latestNavData?.nav_data?.length || 0,
      isLoading: navLoading,
    });
  }, [latestBacktest, latestRunId, latestNavData, navLoading]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d', { alpha: true });
    if (!ctx) return;

    // Set canvas size
    const setCanvasSize = () => {
      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);
      canvas.style.width = `${rect.width}px`;
      canvas.style.height = `${rect.height}px`;
    };

    setCanvasSize();

    const resizeCanvas = () => {
      setCanvasSize();
      // Reposition particles after resize
      particlesRef.current.forEach((particle) => {
        particle.x = Math.min(particle.x, canvas.width / (window.devicePixelRatio || 1));
        particle.y = Math.min(particle.y, canvas.height / (window.devicePixelRatio || 1));
      });
    };

    window.addEventListener('resize', resizeCanvas, { passive: true });

      // Create data-driven line particles
      const createParticles = () => {
        const particles: Particle[] = [];
        const particleCount = 100; // More particles for visibility
        const width = canvas.width / (window.devicePixelRatio || 1);
        const height = canvas.height / (window.devicePixelRatio || 1);
      
      const colors = isDarkMode
        ? [
            'rgba(59, 130, 246, 0.3)',
            'rgba(37, 99, 235, 0.3)',
            'rgba(139, 92, 246, 0.25)',
            'rgba(168, 85, 247, 0.25)',
          ]
        : [
            'rgba(37, 99, 235, 0.2)',
            'rgba(139, 92, 246, 0.2)',
            'rgba(59, 130, 246, 0.18)',
            'rgba(168, 85, 247, 0.18)',
          ];

      // Create particles in a more structured, grid-like pattern that resembles data points
      const gridCols = 12;
      const gridRows = 8;
      const cellWidth = width / gridCols;
      const cellHeight = height / gridRows;

      for (let i = 0; i < particleCount; i++) {
        const col = Math.floor(i % gridCols);
        const row = Math.floor(i / gridCols);
        
        // Add some randomness but keep grid structure
        const baseX = col * cellWidth + cellWidth / 2;
        const baseY = row * cellHeight + cellHeight / 2;
        
        particles.push({
          x: baseX + (Math.random() - 0.5) * cellWidth * 0.6,
          y: baseY + (Math.random() - 0.5) * cellHeight * 0.6,
          vx: (Math.random() - 0.5) * 0.3, // Slower, more controlled movement
          vy: (Math.random() - 0.5) * 0.3,
          radius: Math.random() * 2 + 1, // Larger particles for visibility
          color: colors[Math.floor(Math.random() * colors.length)],
        });
      }

      particlesRef.current = particles;
    };

    createParticles();

    const animate = () => {
      // Clear with better performance
      ctx.save();
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.restore();

      const width = canvas.width / (window.devicePixelRatio || 1);
      const height = canvas.height / (window.devicePixelRatio || 1);

      // Update and draw particles
      const particles = particlesRef.current;
      
      for (let i = 0; i < particles.length; i++) {
        const particle = particles[i];
        
        particle.x += particle.vx;
        particle.y += particle.vy;

        // Bounce off edges instead of wrapping for more controlled movement
        if (particle.x < 0 || particle.x > width) particle.vx *= -1;
        if (particle.y < 0 || particle.y > height) particle.vy *= -1;
        particle.x = Math.max(0, Math.min(width, particle.x));
        particle.y = Math.max(0, Math.min(height, particle.y));
      }


      // Draw particles as small points (data points)
      for (let i = 0; i < particles.length; i++) {
        const particle = particles[i];
        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
        ctx.fillStyle = particle.color;
        ctx.fill();
      }

      animationFrameRef.current = requestAnimationFrame(animate);
    };

    animationFrameRef.current = requestAnimationFrame(animate);

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isDarkMode]);

  return (
    <>
      {/* Backtest Chart Background - No text, just the graph */}
      {latestNavData?.nav_data && latestNavData.nav_data.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.4 }}
          transition={{ duration: 2, ease: 'easeOut' }}
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            zIndex: 0,
            pointerEvents: 'none',
            overflow: 'hidden',
          }}
        >
          <motion.div
            animate={{
              scale: [1, 1.04, 1],
              y: [0, -15, 0],
            }}
            transition={{
              duration: 20,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
            style={{
              width: '100%',
              height: '100%',
            }}
          >
            <Box
              sx={{
                width: '100%',
                height: '100%',
                '& svg': {
                  filter: 'blur(4px)',
                  transition: 'filter 0.3s ease',
                },
                '& .recharts-wrapper': {
                  pointerEvents: 'none !important',
                },
                '& .recharts-tooltip-wrapper': {
                  display: 'none !important',
                },
                '& .recharts-legend-wrapper': {
                  display: 'none !important',
                },
                '& .recharts-cartesian-grid': {
                  display: 'none !important',
                },
                '& .recharts-cartesian-axis': {
                  display: 'none !important',
                },
                '& text': {
                  display: 'none !important',
                  opacity: 0,
                },
                '& .recharts-cartesian-axis-tick-value': {
                  display: 'none !important',
                },
                '& .recharts-layer': {
                  '& text': {
                    display: 'none !important',
                  },
                },
              }}
            >
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                  data={latestNavData.nav_data.map(item => ({
                    date: item.nav_date,
                    portfolio: item.portfolio_nav,
                  }))}
                  margin={{ top: 0, right: 0, left: 0, bottom: 0 }}
                >
                  <defs>
                    <linearGradient id="bgChartGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.5}/>
                      <stop offset="50%" stopColor="#8b5cf6" stopOpacity={0.4}/>
                      <stop offset="100%" stopColor="#3b82f6" stopOpacity={0.2}/>
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="date" hide />
                  <YAxis hide />
                  <Area
                    type="monotone"
                    dataKey="portfolio"
                    stroke="#60a5fa"
                    fill="url(#bgChartGradient)"
                    strokeWidth={3}
                    isAnimationActive={true}
                    animationDuration={2000}
                    animationEasing="ease-out"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </Box>
          </motion.div>
        </motion.div>
      )}

      {/* Particles Canvas */}
      <Box
        component="canvas"
        ref={canvasRef}
        sx={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          zIndex: 0,
          pointerEvents: 'none',
          opacity: 0.6,
        }}
      />
    </>
  );
};

export default AnimatedBackground;

