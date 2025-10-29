/**
 * Metric Card Component
 * Displays a single metric with icon and value
 */

import React from 'react';
import {
  Card,
  CardContent,
  Box,
  Typography,
  Skeleton,
} from '@mui/material';
import { SxProps, Theme } from '@mui/material/styles';
import { motion } from 'framer-motion';
import { useTheme } from '@/contexts/ThemeContext';

interface MetricCardProps {
  title: string;
  value?: number;
  unit?: string;
  icon?: React.ReactNode;
  color?: 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'info';
  loading?: boolean;
  sx?: SxProps<Theme>;
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  unit = '',
  icon,
  color = 'primary',
  loading = false,
  sx,
}) => {
  const { isDarkMode } = useTheme();

  const formatValue = (val: number | undefined): string => {
    if (val === undefined || val === null) return 'N/A';
    return val.toFixed(2);
  };

  const getColorValue = (color: string): string => {
    const colorMap: Record<string, string> = {
      primary: isDarkMode ? '#6366f1' : '#4f46e5',
      secondary: isDarkMode ? '#10b981' : '#059669',
      success: isDarkMode ? '#10b981' : '#059669',
      error: isDarkMode ? '#ef4444' : '#dc2626',
      warning: isDarkMode ? '#f59e0b' : '#d97706',
      info: isDarkMode ? '#06b6d4' : '#0891b2',
    };
    return colorMap[color] || colorMap.primary;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      whileHover={{ y: -4 }}
    >
      <Card
        sx={{
          height: '100%',
          background: isDarkMode 
            ? 'linear-gradient(145deg, #1e293b 0%, #334155 100%)'
            : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
          backdropFilter: 'none',
          border: '1px solid',
          borderColor: isDarkMode 
            ? 'rgba(148, 163, 184, 0.1)'
            : 'rgba(148, 163, 184, 0.2)',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: '3px',
            background: `linear-gradient(90deg, ${getColorValue(color)} 0%, ${getColorValue(color)}80 100%)`,
            opacity: 0,
            transition: 'opacity 0.3s ease',
          },
          '&:hover': {
            borderColor: getColorValue(color),
            boxShadow: isDarkMode 
              ? `0 12px 40px 0 ${getColorValue(color)}30, 0 8px 24px 0 rgba(0, 0, 0, 0.3)`
              : `0 12px 40px 0 ${getColorValue(color)}20, 0 8px 24px 0 rgba(0, 0, 0, 0.1)`,
            '&::before': {
              opacity: 1,
            },
          },
          ...sx,
        }}
      >
        <CardContent sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            {icon && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ duration: 0.3, delay: 0.1 }}
                whileHover={{ scale: 1.1, rotate: 5 }}
              >
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: 48,
                    height: 48,
                    borderRadius: 3,
                    background: isDarkMode 
                      ? `linear-gradient(135deg, ${getColorValue(color)}20 0%, ${getColorValue(color)}10 100%)`
                      : `linear-gradient(135deg, ${getColorValue(color)}15 0%, ${getColorValue(color)}05 100%)`,
                    color: getColorValue(color),
                    mr: 2,
                    border: `1px solid ${getColorValue(color)}30`,
                  }}
                >
                  {icon}
                </Box>
              </motion.div>
            )}
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ 
                fontWeight: 600, 
                textTransform: 'uppercase', 
                letterSpacing: 0.8,
                fontSize: '0.75rem',
              }}
            >
              {title}
            </Typography>
          </Box>

          {loading ? (
            <Skeleton 
              variant="text" 
              width="60%" 
              height={40} 
              sx={{ 
                borderRadius: 2,
                background: isDarkMode 
                  ? 'linear-gradient(90deg, rgba(148, 163, 184, 0.1) 0%, rgba(148, 163, 184, 0.2) 50%, rgba(148, 163, 184, 0.1) 100%)'
                  : 'linear-gradient(90deg, rgba(148, 163, 184, 0.1) 0%, rgba(148, 163, 184, 0.2) 50%, rgba(148, 163, 184, 0.1) 100%)',
              }} 
            />
          ) : (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3, delay: 0.2 }}
            >
              <Typography
                variant="h3"
                component="div"
                sx={{
                  fontWeight: 800,
                  background: `linear-gradient(135deg, ${getColorValue(color)} 0%, ${getColorValue(color)}80 100%)`,
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  lineHeight: 1.1,
                  mb: 0.5,
                }}
              >
                {formatValue(value)}
                {unit && (
                  <Typography
                    component="span"
                    variant="h6"
                    sx={{
                      ml: 0.5,
                      color: 'text.secondary',
                      fontWeight: 500,
                      fontSize: '1.25rem',
                    }}
                  >
                    {unit}
                  </Typography>
                )}
              </Typography>
            </motion.div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default MetricCard;

