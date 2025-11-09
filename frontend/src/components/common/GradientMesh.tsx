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

    // No gradient animation - background is transparent
    container.style.background = 'transparent';
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

