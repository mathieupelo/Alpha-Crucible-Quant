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
  Group as GroupIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';

import { universeApi } from '@/services/api';
import { TickerValidation, UniverseCompany } from '@/types';

const UniverseDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const universeId = parseInt(id || '0');

  // State
  const [tickerInput, setTickerInput] = useState('');
  const [companies, setCompanies] = useState<UniverseCompany[]>([]);
  const [expandedCompanies, setExpandedCompanies] = useState<Set<string>>(new Set());
  const [validationResults, setValidationResults] = useState<TickerValidation[]>([]);
  const [isValidating, setIsValidating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [companyToDelete, setCompanyToDelete] = useState<string | null>(null);

  // Fetch universe details
  const {
    data: universe,
    isLoading: universeLoading,
    error: universeError,
  } = useQuery(['universe', universeId], () => universeApi.getUniverse(universeId), {
    enabled: !!universeId,
  });

  // Fetch universe companies
  const {
    data: companiesData,
    isLoading: companiesLoading,
    error: companiesError,
  } = useQuery(['universe-companies', universeId], () => universeApi.getUniverseCompanies(universeId), {
    enabled: !!universeId,
  });


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

  // Initialize companies when data loads
  useEffect(() => {
    if (companiesData?.companies) {
      setCompanies(companiesData.companies);
    }
  }, [companiesData]);

  const handleAddTicker = async () => {
    const ticker = tickerInput.trim().toUpperCase();
    if (!ticker) return;
    
    try {
      await universeApi.addUniverseCompany(universeId, ticker);
      queryClient.invalidateQueries(['universe-companies', universeId]);
      setTickerInput('');
      setError(null);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to add company');
    }
  };

  const handleRemoveCompany = (companyUid: string) => {
    setCompanyToDelete(companyUid);
    setDeleteDialogOpen(true);
  };

  const confirmRemoveCompany = async () => {
    if (companyToDelete) {
      try {
        await universeApi.removeUniverseCompany(universeId, companyToDelete);
        queryClient.invalidateQueries(['universe-companies', universeId]);
        setCompanyToDelete(null);
        setDeleteDialogOpen(false);
        setError(null);
      } catch (error: any) {
        setError(error.response?.data?.detail || 'Failed to remove company');
      }
    }
  };

  const handleToggleExpand = (companyUid: string) => {
    const newExpanded = new Set(expandedCompanies);
    if (newExpanded.has(companyUid)) {
      newExpanded.delete(companyUid);
    } else {
      newExpanded.add(companyUid);
    }
    setExpandedCompanies(newExpanded);
  };

  const handleValidateTickers = async () => {
    const tickers = companies.map(c => c.main_ticker).filter(Boolean);
    if (tickers.length === 0) return;
    
    setIsValidating(true);
    validateTickersMutation.mutate(tickers);
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

  if (universeError || companiesError) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        Failed to load universe data. Please check your connection and try again.
      </Alert>
    );
  }

  if (universeLoading || companiesLoading) {
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
            label={`${companies.length} companies`}
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

      {/* Validation Section */}
      {companies.length > 0 && (
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Ticker Validation
              </Typography>
              <Button
                variant="outlined"
                onClick={handleValidateTickers}
                disabled={isValidating || companies.length === 0}
                startIcon={isValidating ? <CircularProgress size={16} /> : null}
              >
                {isValidating ? 'Validating...' : 'Validate Tickers'}
              </Button>
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

      {/* Companies List */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Current Companies ({companies.length})
          </Typography>
          
          {companies.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <GroupIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="body1" color="text.secondary">
                No companies added yet. Add some tickers to get started.
              </Typography>
            </Box>
          ) : (
            <List>
              {companies.map((company, index) => {
                const validation = getValidationResult(company.main_ticker);
                const isExpanded = expandedCompanies.has(company.company_uid);
                const hasMultipleTickers = company.all_tickers && company.all_tickers.length > 1;
                
                return (
                  <React.Fragment key={company.company_uid}>
                    <ListItem>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                            <Typography variant="body1" sx={{ fontWeight: 500 }}>
                              {company.company_name || company.main_ticker}
                            </Typography>
                            <Chip 
                              label={company.main_ticker} 
                              size="small" 
                              variant="outlined"
                              color="primary"
                            />
                            {hasMultipleTickers && (
                              <Chip 
                                label={`+${company.all_tickers.length - 1} more`}
                                size="small"
                                variant="outlined"
                                onClick={() => handleToggleExpand(company.company_uid)}
                                sx={{ cursor: 'pointer' }}
                              />
                            )}
                            {validation && (
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                {validation.is_valid ? (
                                  <CheckCircleIcon color="success" fontSize="small" />
                                ) : (
                                  <CancelIcon color="error" fontSize="small" />
                                )}
                              </Box>
                            )}
                          </Box>
                        }
                        secondary={
                          <Box>
                            {validation?.is_valid && (
                              <Typography variant="caption" color="success.main">
                                {validation.company_name || "Valid"}
                              </Typography>
                            )}
                            {isExpanded && hasMultipleTickers && (
                              <Box sx={{ mt: 1 }}>
                                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                                  All tickers:
                                </Typography>
                                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                  {company.all_tickers.map((ticker) => (
                                    <Chip 
                                      key={ticker}
                                      label={ticker} 
                                      size="small"
                                      variant={ticker === company.main_ticker ? "filled" : "outlined"}
                                      color={ticker === company.main_ticker ? "primary" : "default"}
                                    />
                                  ))}
                                </Box>
                              </Box>
                            )}
                          </Box>
                        }
                      />
                      <ListItemSecondaryAction>
                        <Tooltip title="Remove Company">
                          <IconButton
                            edge="end"
                            onClick={() => handleRemoveCompany(company.company_uid)}
                            color="error"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </ListItemSecondaryAction>
                    </ListItem>
                    {index < companies.length - 1 && <Divider />}
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
        <DialogTitle>Remove Company</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to remove this company from this universe?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={confirmRemoveCompany} color="error" variant="contained">
            Remove
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default UniverseDetail;
