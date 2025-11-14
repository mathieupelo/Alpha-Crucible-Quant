/**
 * Animated Background Component
 * Creates stunning animated backgrounds with particles and gradients
 */

import React, { useEffect, useRef } from 'react';
import { Box } from '@mui/material';
import { useTheme } from '@/contexts/ThemeContext';

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

