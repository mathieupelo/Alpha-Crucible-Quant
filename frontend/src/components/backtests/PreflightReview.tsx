/**
 * Preflight Review Component
 * Displays backtest configuration review before execution
 */

import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Button,
  CircularProgress,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Edit as EditIcon,
  PlayArrow as PlayArrowIcon,
} from '@mui/icons-material';
import { BacktestCreateRequest } from '@/types';
import { PreflightResult } from '@/hooks/useBacktestConfig';

interface PreflightReviewProps {
  formData: Partial<BacktestCreateRequest>;
  preflightResult: PreflightResult;
  universesData?: { universes: Array<{ id: number; name: string }> };
  isRunning: boolean;
  onRun: () => void;
  onEdit: () => void;
  onCancel: () => void;
}

export const PreflightReview: React.FC<PreflightReviewProps> = ({
  formData,
  preflightResult,
  universesData,
  isRunning,
  onRun,
  onEdit,
  onCancel,
}) => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom sx={{ mb: 3 }}>
          Review & Confirm
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600 }}>
              Backtest Configuration
            </Typography>
            <List dense>
              <ListItem>
                <ListItemText 
                  primary="Name" 
                  secondary={formData.name || 'Unnamed Backtest'} 
                />
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="Universe" 
                  secondary={universesData?.universes.find(u => u.id === formData.universe_id)?.name} 
                />
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="Date Range" 
                  secondary={`${formData.start_date} to ${formData.end_date}`} 
                />
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="Rebalancing Frequency" 
                  secondary={formData.rebalancing_frequency} 
                />
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="Max Position Weight" 
                  secondary={`${(formData.max_weight || 0) * 100}%`} 
                />
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="Selected Signals" 
                  secondary={(formData.signals || []).join(', ')} 
                />
              </ListItem>
            </List>
          </Grid>

          <Grid item xs={12} md={6}>
            <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600 }}>
              Rebalancing Dates
            </Typography>
            <Box sx={{ maxHeight: 200, overflow: 'auto' }}>
              <List dense>
                {preflightResult.rebalancingDates.map((date, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <CheckCircleIcon color="success" fontSize="small" />
                    </ListItemIcon>
                    <ListItemText 
                      primary={new Date(date).toLocaleDateString()} 
                      secondary={`Trading day ${index + 1}`}
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
          </Grid>
        </Grid>

        <Divider sx={{ my: 3 }} />

        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            onClick={onRun}
            disabled={isRunning}
            startIcon={isRunning ? <CircularProgress size={20} /> : <PlayArrowIcon />}
          >
            {isRunning ? 'Running Backtest...' : 'Run Backtest'}
          </Button>
          <Button
            variant="outlined"
            onClick={onEdit}
            startIcon={<EditIcon />}
          >
            Edit Configuration
          </Button>
          <Button
            variant="outlined"
            onClick={onCancel}
          >
            Cancel
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};

