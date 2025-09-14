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
  const formatValue = (val: number | undefined): string => {
    if (val === undefined || val === null) return 'N/A';
    return val.toFixed(2);
  };

  const getColorValue = (color: string): string => {
    const colorMap: Record<string, string> = {
      primary: '#2563eb',
      secondary: '#10b981',
      success: '#10b981',
      error: '#ef4444',
      warning: '#f59e0b',
      info: '#3b82f6',
    };
    return colorMap[color] || colorMap.primary;
  };

  return (
    <Card
      sx={{
        height: '100%',
        backgroundImage: 'none',
        backgroundColor: 'background.paper',
        border: '1px solid',
        borderColor: 'divider',
        transition: 'all 0.2s ease-in-out',
        '&:hover': {
          borderColor: getColorValue(color),
          boxShadow: `0 4px 12px 0 ${getColorValue(color)}20`,
        },
        ...sx,
      }}
    >
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          {icon && (
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 40,
                height: 40,
                borderRadius: 2,
                backgroundColor: `${getColorValue(color)}20`,
                color: getColorValue(color),
                mr: 2,
              }}
            >
              {icon}
            </Box>
          )}
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{ fontWeight: 500, textTransform: 'uppercase', letterSpacing: 0.5 }}
          >
            {title}
          </Typography>
        </Box>

        {loading ? (
          <Skeleton variant="text" width="60%" height={32} />
        ) : (
          <Typography
            variant="h4"
            component="div"
            sx={{
              fontWeight: 700,
              color: getColorValue(color),
              lineHeight: 1.2,
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
                  fontWeight: 400,
                }}
              >
                {unit}
              </Typography>
            )}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

export default MetricCard;

