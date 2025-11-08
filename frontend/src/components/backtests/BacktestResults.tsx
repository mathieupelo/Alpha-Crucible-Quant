/**
 * Backtest Results Component
 * Displays backtest execution results
 */

import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Alert,
  Button,
} from '@mui/material';
import {
  Visibility as VisibilityIcon,
} from '@mui/icons-material';

interface BacktestResultsProps {
  runResult: { success: boolean; runId?: string; error?: string };
  onViewResults: () => void;
  onRunAnother: () => void;
  onCancel: () => void;
}

export const BacktestResults: React.FC<BacktestResultsProps> = ({
  runResult,
  onViewResults,
  onRunAnother,
  onCancel,
}) => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom sx={{ mb: 3 }}>
          Backtest Results
        </Typography>

        {runResult.success ? (
          <Alert severity="success" sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Backtest Completed Successfully!
            </Typography>
            <Typography variant="body2">
              Your backtest has been created and executed. You can now view the detailed results and analysis.
            </Typography>
          </Alert>
        ) : (
          <Alert severity="error" sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Backtest Failed
            </Typography>
            <Typography variant="body2">
              {runResult.error}
            </Typography>
          </Alert>
        )}

        <Box sx={{ display: 'flex', gap: 2 }}>
          {runResult.success && (
            <Button
              variant="contained"
              onClick={onViewResults}
              startIcon={<VisibilityIcon />}
            >
              View Results
            </Button>
          )}
          <Button
            variant="outlined"
            onClick={onRunAnother}
          >
            Run Another Backtest
          </Button>
          <Button
            variant="outlined"
            onClick={onCancel}
          >
            Back to Dashboard
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};

