/**
 * Performance Chart Component
 * Displays portfolio performance over time using Recharts
 */

import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { Box, Typography, useTheme } from '@mui/material';
import { format, parseISO } from 'date-fns';

import { NavData } from '@/types';

interface PerformanceChartProps {
  data: NavData[];
  height?: number;
  showBenchmark?: boolean;
}

const PerformanceChart: React.FC<PerformanceChartProps> = ({
  data,
  height = 400,
  showBenchmark = true,
}) => {
  const theme = useTheme();

  // Transform data for chart
  const chartData = data.map((item) => ({
    date: item.nav_date,
    portfolio: item.portfolio_nav,
    benchmark: item.benchmark_nav || null,
    pnl: item.pnl || 0,
  }));

  // Calculate performance metrics
  const firstValue = chartData[0]?.portfolio || 0;
  const lastValue = chartData[chartData.length - 1]?.portfolio || 0;
  const totalReturn = firstValue > 0 ? ((lastValue - firstValue) / firstValue) * 100 : 0;

  const formatXAxisLabel = (tickItem: string) => {
    try {
      return format(parseISO(tickItem), 'MMM dd');
    } catch {
      return tickItem;
    }
  };

  const formatTooltipLabel = (label: string) => {
    try {
      return format(parseISO(label), 'MMM dd, yyyy');
    } catch {
      return label;
    }
  };

  const formatValue = (value: number, name: string) => {
    if (name === 'pnl') {
      return [`$${value.toFixed(2)}`, 'PnL'];
    }
    return [`$${value.toFixed(2)}`, name === 'portfolio' ? 'Portfolio' : 'Benchmark'];
  };

  if (!data || data.length === 0) {
    return (
      <Box
        sx={{
          height,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: 'background.default',
          borderRadius: 1,
          border: '1px dashed',
          borderColor: 'divider',
        }}
      >
        <Typography variant="body2" color="text.secondary">
          No performance data available
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%', height }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={chartData}
          margin={{
            top: 20,
            right: 30,
            left: 20,
            bottom: 20,
          }}
        >
          <CartesianGrid 
            strokeDasharray="3 3" 
            stroke={theme.palette.divider}
            opacity={0.3}
          />
          <XAxis
            dataKey="date"
            tickFormatter={formatXAxisLabel}
            stroke={theme.palette.text.secondary}
            fontSize={12}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            tickFormatter={(value) => `$${value.toLocaleString()}`}
            stroke={theme.palette.text.secondary}
            fontSize={12}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip
            labelFormatter={formatTooltipLabel}
            formatter={formatValue}
            contentStyle={{
              backgroundColor: theme.palette.background.paper,
              border: `1px solid ${theme.palette.divider}`,
              borderRadius: 8,
              boxShadow: theme.shadows[4],
            }}
            labelStyle={{
              color: theme.palette.text.primary,
              fontWeight: 600,
            }}
          />
          <Legend />
          
          {/* Reference line at starting value */}
          <ReferenceLine
            y={firstValue}
            stroke={theme.palette.text.secondary}
            strokeDasharray="2 2"
            opacity={0.5}
            label={{ value: "Starting Value", position: "top" }}
          />
          
          {/* Portfolio line */}
          <Line
            type="monotone"
            dataKey="portfolio"
            stroke={theme.palette.primary.main}
            strokeWidth={3}
            dot={false}
            activeDot={{
              r: 6,
              stroke: theme.palette.primary.main,
              strokeWidth: 2,
              fill: theme.palette.background.paper,
            }}
          />
          
          {/* Benchmark line */}
          {showBenchmark && (
            <Line
              type="monotone"
              dataKey="benchmark"
              stroke={theme.palette.secondary.main}
              strokeWidth={2}
              dot={false}
              strokeDasharray="5 5"
              activeDot={{
                r: 4,
                stroke: theme.palette.secondary.main,
                strokeWidth: 2,
                fill: theme.palette.background.paper,
              }}
            />
          )}
        </LineChart>
      </ResponsiveContainer>
      
      {/* Performance summary */}
      <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          Total Return: {totalReturn.toFixed(2)}%
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {data.length} data points
        </Typography>
      </Box>
    </Box>
  );
};

export default PerformanceChart;

