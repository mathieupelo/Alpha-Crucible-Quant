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

    // Create particles
    const createParticles = () => {
      const particles: Particle[] = [];
      const particleCount = 50;
      const width = canvas.width / (window.devicePixelRatio || 1);
      const height = canvas.height / (window.devicePixelRatio || 1);
      
      const colors = isDarkMode
        ? [
            'rgba(37, 99, 235, 0.4)',
            'rgba(139, 92, 246, 0.4)',
            'rgba(59, 130, 246, 0.3)',
            'rgba(168, 85, 247, 0.3)',
          ]
        : [
            'rgba(37, 99, 235, 0.2)',
            'rgba(139, 92, 246, 0.2)',
            'rgba(59, 130, 246, 0.15)',
            'rgba(168, 85, 247, 0.15)',
          ];

      for (let i = 0; i < particleCount; i++) {
        particles.push({
          x: Math.random() * width,
          y: Math.random() * height,
          vx: (Math.random() - 0.5) * 0.5,
          vy: (Math.random() - 0.5) * 0.5,
          radius: Math.random() * 2 + 1,
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
      const connectionDistance = 150;
      const strokeOpacity = isDarkMode ? 0.2 : 0.1;

      // Update and draw particles
      const particles = particlesRef.current;
      for (let i = 0; i < particles.length; i++) {
        const particle = particles[i];
        
        particle.x += particle.vx;
        particle.y += particle.vy;

        // Wrap around edges
        if (particle.x < 0) particle.x = width;
        if (particle.x > width) particle.x = 0;
        if (particle.y < 0) particle.y = height;
        if (particle.y > height) particle.y = 0;

        // Draw particle
        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
        ctx.fillStyle = particle.color;
        ctx.fill();

        // Draw connections (only to particles after current one to avoid duplicates)
        for (let j = i + 1; j < particles.length; j++) {
          const other = particles[j];
          const dx = particle.x - other.x;
          const dy = particle.y - other.y;
          const distanceSquared = dx * dx + dy * dy;

          if (distanceSquared < connectionDistance * connectionDistance) {
            const distance = Math.sqrt(distanceSquared);
            ctx.beginPath();
            ctx.moveTo(particle.x, particle.y);
            ctx.lineTo(other.x, other.y);
            ctx.strokeStyle = `rgba(37, 99, 235, ${strokeOpacity * (1 - distance / connectionDistance)})`;
            ctx.lineWidth = 0.5;
            ctx.stroke();
          }
        }
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
      }}
    />
  );
};

export default AnimatedBackground;

