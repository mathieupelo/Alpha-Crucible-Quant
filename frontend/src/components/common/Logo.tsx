/**
 * Logo Component
 * Reusable logo component with different sizes and clickable functionality
 */

import React from 'react';
import { Box, BoxProps } from '@mui/material';
import { useNavigate } from 'react-router-dom';

interface LogoProps extends Omit<BoxProps, 'onClick'> {
  size?: 'small' | 'medium' | 'large' | 'xlarge';
  clickable?: boolean;
  showText?: boolean;
  variant?: 'default' | 'minimal';
}

const Logo: React.FC<LogoProps> = ({
  size = 'medium',
  clickable = true,
  showText = true,
  variant = 'default',
  sx,
  ...props
}) => {
  const navigate = useNavigate();

  const sizeMap = {
    small: { width: 32, height: 32 },
    medium: { width: 48, height: 48 },
    large: { width: 64, height: 64 },
    xlarge: { width: 96, height: 96 },
  };

  const textSizeMap = {
    small: 'h6',
    medium: 'h5',
    large: 'h4',
    xlarge: 'h3',
  } as const;

  const handleClick = () => {
    if (clickable) {
      navigate('/');
    }
  };

  const logoStyles = {
    display: 'flex',
    alignItems: 'center',
    gap: 1.5,
    cursor: clickable ? 'pointer' : 'default',
    transition: 'opacity 0.2s ease-in-out',
    '&:hover': clickable ? {
      opacity: 0.8,
    } : {},
    ...sx,
  };

  const imageStyles = {
    ...sizeMap[size],
    objectFit: 'contain' as const,
  };

  return (
    <Box sx={logoStyles} onClick={handleClick} {...props}>
      <Box
        component="img"
        src="/logo/AC logo.png"
        alt="Alpha Crucible Quant Logo"
        sx={imageStyles}
      />
      {showText && variant === 'default' && (
        <Box>
          <Box
            component="span"
            sx={{
              fontSize: textSizeMap[size],
              fontWeight: 700,
              color: 'text.primary',
              letterSpacing: '-0.025em',
              display: 'block',
              lineHeight: 1.2,
            }}
          >
            Alpha Crucible
          </Box>
          <Box
            component="span"
            sx={{
              fontSize: textSizeMap[size],
              fontWeight: 600,
              color: 'primary.main',
              letterSpacing: '-0.025em',
              display: 'block',
              lineHeight: 1.2,
            }}
          >
            Quant
          </Box>
        </Box>
      )}
      {showText && variant === 'minimal' && (
        <Box
          component="span"
          sx={{
            fontSize: textSizeMap[size],
            fontWeight: 700,
            color: 'text.primary',
            letterSpacing: '-0.025em',
          }}
        >
          AC Quant
        </Box>
      )}
    </Box>
  );
};

export default Logo;
