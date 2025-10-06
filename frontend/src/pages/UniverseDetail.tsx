/**
 * Universe Detail Page
 * Manage tickers within a specific universe
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  TextField,
  Chip,
  Alert,
  Skeleton,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  Tooltip,
  CircularProgress,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  ArrowBack as ArrowBackIcon,
  Save as SaveIcon,
  Group as GroupIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';

import { universeApi } from '@/services/api';
import { TickerValidation } from '@/types';

const UniverseDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const universeId = parseInt(id || '0');

  // State
  const [tickerInput, setTickerInput] = useState('');
  const [tickers, setTickers] = useState<string[]>([]);
  const [validationResults, setValidationResults] = useState<TickerValidation[]>([]);
  const [isValidating, setIsValidating] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [tickerToDelete, setTickerToDelete] = useState<string | null>(null);

  // Fetch universe details
  const {
    data: universe,
    isLoading: universeLoading,
    error: universeError,
  } = useQuery(['universe', universeId], () => universeApi.getUniverse(universeId), {
    enabled: !!universeId,
  });

  // Fetch universe tickers
  const {
    data: tickersData,
    // isLoading: tickersLoading,
    error: tickersError,
  } = useQuery(['universe-tickers', universeId], () => universeApi.getUniverseTickers(universeId), {
    enabled: !!universeId,
  });

  // Update tickers mutation
  const updateTickersMutation = useMutation(
    (tickers: string[]) => universeApi.updateUniverseTickers(universeId, { tickers }),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['universe-tickers', universeId]);
        setHasChanges(false);
        setError(null);
      },
      onError: (error: any) => {
        setError(error.response?.data?.detail || 'Failed to update tickers');
      },
    }
  );

  // Remove ticker mutation
  // const removeTickerMutation = useMutation(
  //   (ticker: string) => universeApi.removeUniverseTicker(universeId, ticker),
  //   {
  //     onSuccess: () => {
  //       queryClient.invalidateQueries(['universe-tickers', universeId]);
  //       setTickerToDelete(null);
  //       setDeleteDialogOpen(false);
  //     },
  //     onError: (error: any) => {
  //       setError(error.response?.data?.detail || 'Failed to remove ticker');
  //     },
  //   }
  // );

  // Validate tickers mutation
  const validateTickersMutation = useMutation(universeApi.validateTickers, {
    onSuccess: (results) => {
      setValidationResults(results);
      setIsValidating(false);
    },
    onError: (error: any) => {
      setError(error.response?.data?.detail || 'Failed to validate tickers');
      setIsValidating(false);
    },
  });

  // Initialize tickers when data loads
  useEffect(() => {
    if (tickersData?.tickers) {
      const tickerList = tickersData.tickers.map(t => t.ticker);
      setTickers(tickerList);
    }
  }, [tickersData]);

  const handleAddTicker = () => {
    const ticker = tickerInput.trim().toUpperCase();
    if (ticker && !tickers.includes(ticker)) {
      const newTickers = [...tickers, ticker];
      setTickers(newTickers);
      setTickerInput('');
      setHasChanges(true);
    }
  };

  const handleRemoveTicker = (ticker: string) => {
    setTickerToDelete(ticker);
    setDeleteDialogOpen(true);
  };

  const confirmRemoveTicker = () => {
    if (tickerToDelete) {
      const newTickers = tickers.filter(t => t !== tickerToDelete);
      setTickers(newTickers);
      setHasChanges(true);
      setTickerToDelete(null);
      setDeleteDialogOpen(false);
    }
  };

  const handleValidateTickers = async () => {
    if (tickers.length === 0) return;
    
    setIsValidating(true);
    validateTickersMutation.mutate(tickers);
  };

  const handleSaveTickers = () => {
    updateTickersMutation.mutate(tickers);
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      handleAddTicker();
    }
  };

  const getValidationResult = (ticker: string): TickerValidation | undefined => {
    return validationResults.find(result => result.ticker === ticker);
  };

  const allTickersValid = validationResults.length > 0 && validationResults.every(result => result.is_valid);
  const hasInvalidTickers = validationResults.some(result => !result.is_valid);

  if (universeError || tickersError) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        Failed to load universe data. Please check your connection and try again.
      </Alert>
    );
  }

  if (universeLoading) {
    return (
      <Box>
        <Skeleton variant="text" height={40} width={300} />
        <Skeleton variant="text" height={24} width={200} sx={{ mb: 4 }} />
        <Skeleton variant="rectangular" height={400} />
      </Box>
    );
  }

  if (!universe) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        Universe not found.
      </Alert>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <IconButton onClick={() => navigate('/universes')} sx={{ mr: 1 }}>
            <ArrowBackIcon />
          </IconButton>
          <Box>
            <Typography variant="h4" component="h1" sx={{ fontWeight: 700 }}>
              {universe.name}
            </Typography>
            {universe.description && (
              <Typography variant="body1" color="text.secondary">
                {universe.description}
              </Typography>
            )}
          </Box>
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Chip
            icon={<GroupIcon />}
            label={`${tickers.length} tickers`}
            color="primary"
            variant="outlined"
          />
          <Typography variant="caption" color="text.secondary">
            Created {new Date(universe.created_at).toLocaleDateString()}
          </Typography>
        </Box>
      </Box>

      {/* Add Ticker Section */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Add Tickers
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <TextField
              label="Ticker Symbol"
              value={tickerInput}
              onChange={(e) => setTickerInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="e.g., AAPL, MSFT, GOOGL"
              sx={{ flexGrow: 1 }}
              helperText="Enter ticker symbols separated by commas or one at a time"
            />
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleAddTicker}
              disabled={!tickerInput.trim()}
            >
              Add
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Validation and Save Section */}
      {tickers.length > 0 && (
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Ticker Validation
              </Typography>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button
                  variant="outlined"
                  onClick={handleValidateTickers}
                  disabled={isValidating || tickers.length === 0}
                  startIcon={isValidating ? <CircularProgress size={16} /> : null}
                >
                  {isValidating ? 'Validating...' : 'Validate Tickers'}
                </Button>
                <Button
                  variant="contained"
                  onClick={handleSaveTickers}
                  disabled={!hasChanges || hasInvalidTickers}
                  startIcon={<SaveIcon />}
                >
                  Save Changes
                </Button>
              </Box>
            </Box>
            
            {validationResults.length > 0 && (
              <Alert 
                severity={allTickersValid ? "success" : hasInvalidTickers ? "error" : "info"}
                sx={{ mb: 2 }}
              >
                {allTickersValid 
                  ? "All tickers are valid and ready to save!"
                  : hasInvalidTickers 
                    ? "Some tickers are invalid. Please remove invalid tickers before saving."
                    : "Validation results will appear here."
                }
              </Alert>
            )}
          </CardContent>
        </Card>
      )}

      {/* Tickers List */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Current Tickers ({tickers.length})
          </Typography>
          
          {tickers.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <GroupIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="body1" color="text.secondary">
                No tickers added yet. Add some tickers to get started.
              </Typography>
            </Box>
          ) : (
            <List>
              {tickers.map((ticker, index) => {
                const validation = getValidationResult(ticker);
                return (
                  <React.Fragment key={ticker}>
                    <ListItem>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body1" sx={{ fontWeight: 500 }}>
                              {ticker}
                            </Typography>
                            {validation && (
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                {validation.is_valid ? (
                                  <CheckCircleIcon color="success" fontSize="small" />
                                ) : (
                                  <CancelIcon color="error" fontSize="small" />
                                )}
                                <Typography 
                                  variant="caption" 
                                  color={validation.is_valid ? "success.main" : "error.main"}
                                >
                                  {validation.is_valid 
                                    ? validation.company_name || "Valid"
                                    : validation.error_message || "Invalid"
                                  }
                                </Typography>
                              </Box>
                            )}
                          </Box>
                        }
                        secondary={validation?.is_valid ? validation.company_name : undefined}
                      />
                      <ListItemSecondaryAction>
                        <Tooltip title="Remove Ticker">
                          <IconButton
                            edge="end"
                            onClick={() => handleRemoveTicker(ticker)}
                            color="error"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </ListItemSecondaryAction>
                    </ListItem>
                    {index < tickers.length - 1 && <Divider />}
                  </React.Fragment>
                );
              })}
            </List>
          )}
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Remove Ticker</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to remove "{tickerToDelete}" from this universe?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={confirmRemoveTicker} color="error" variant="contained">
            Remove
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default UniverseDetail;
