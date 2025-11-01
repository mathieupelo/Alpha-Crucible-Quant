/**
 * Gradient Mesh Background
 * Creates animated gradient mesh effect
 */

import React, { useEffect, useRef } from 'react';
import { Box } from '@mui/material';
import { useTheme } from '@/contexts/ThemeContext';

const GradientMesh: React.FC = () => {
  const { isDarkMode } = useTheme();
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    // Set initial gradient positions
    let pos1 = { x: 20, y: 50 };
    let pos2 = { x: 80, y: 80 };
    let pos3 = { x: 50, y: 20 };

    const updateGradient = () => {
      // Smoothly animate positions
      pos1.x += (Math.random() * 60 + 10 - pos1.x) * 0.02;
      pos1.y += (Math.random() * 60 + 20 - pos1.y) * 0.02;
      pos2.x += (Math.random() * 60 + 30 - pos2.x) * 0.02;
      pos2.y += (Math.random() * 60 + 50 - pos2.y) * 0.02;
      pos3.x += (Math.random() * 60 + 20 - pos3.x) * 0.02;
      pos3.y += (Math.random() * 60 + 10 - pos3.y) * 0.02;

      const gradient = isDarkMode
        ? `radial-gradient(circle at ${pos1.x}% ${pos1.y}%, rgba(37, 99, 235, 0.15) 0%, transparent 50%), 
           radial-gradient(circle at ${pos2.x}% ${pos2.y}%, rgba(139, 92, 246, 0.15) 0%, transparent 50%),
           radial-gradient(circle at ${pos3.x}% ${pos3.y}%, rgba(59, 130, 246, 0.1) 0%, transparent 50%)`
        : `radial-gradient(circle at ${pos1.x}% ${pos1.y}%, rgba(37, 99, 235, 0.08) 0%, transparent 50%), 
           radial-gradient(circle at ${pos2.x}% ${pos2.y}%, rgba(139, 92, 246, 0.08) 0%, transparent 50%),
           radial-gradient(circle at ${pos3.x}% ${pos3.y}%, rgba(59, 130, 246, 0.05) 0%, transparent 50%)`;

      container.style.background = gradient;
    };

    // Initial gradient
    updateGradient();

    // Update gradient smoothly using requestAnimationFrame
    let animationFrame: number;
    const animate = () => {
      updateGradient();
      animationFrame = requestAnimationFrame(animate);
    };
    animationFrame = requestAnimationFrame(animate);

    return () => {
      if (animationFrame) {
        cancelAnimationFrame(animationFrame);
      }
    };
  }, [isDarkMode]);

  return (
    <Box
      ref={containerRef}
      sx={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        zIndex: 0,
        pointerEvents: 'none',
        transition: 'background 0.3s ease-out',
      }}
    />
  );
};

export default GradientMesh;

