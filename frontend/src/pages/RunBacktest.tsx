/**
 * Run Backtest Page
 * Allows users to configure and run backtests with preflight checks
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Alert,
  Stepper,
  Step,
  StepLabel,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  CircularProgress,
  FormHelperText,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  PlayArrow as PlayArrowIcon,
  Edit as EditIcon,
  Visibility as VisibilityIcon,
} from '@mui/icons-material';
import { useQuery, useMutation } from 'react-query';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

import { backtestApi, universeApi, signalApi } from '@/services/api';
import { BacktestCreateRequest } from '@/types';
import Logo from '@/components/common/Logo';

interface PreflightResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  rebalancingDates: string[];
  signalGaps: Array<{ ticker: string; signal: string; date: string }>;
}

const RunBacktest: React.FC = () => {
  const navigate = useNavigate();
  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState<Partial<BacktestCreateRequest>>({
    start_date: '2024-01-01',  // Default to a reasonable range within available signals
    end_date: '2024-12-31',    // Default to a reasonable range within available signals
    rebalancing_frequency: 'monthly',
    max_weight: 0.1,
    min_weight: 0.0,
    initial_capital: 10000,
    transaction_costs: 0.001,
    risk_aversion: 0.5,
    benchmark_ticker: 'SPY',
    use_equal_weight_benchmark: true,
    min_lookback_days: 252,
    max_lookback_days: 756,
    signal_combination_method: 'equal_weight',
    forward_fill_signals: true,
  });
  const [preflightResult, setPreflightResult] = useState<PreflightResult | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [runResult, setRunResult] = useState<{ success: boolean; runId?: string; error?: string } | null>(null);
  const [nameValidation, setNameValidation] = useState<{ 
    isValid: boolean; 
    message: string; 
    isChecking: boolean 
  }>({ isValid: true, message: '', isChecking: false });

  // Fetch universes
  const { data: universesData, isLoading: universesLoading } = useQuery(
    'universes',
    () => universeApi.getUniverses()
  );

  // Fetch available signal types
  const { data: signalTypesData, isLoading: signalsLoading } = useQuery(
    'signal-types',
    () => signalApi.getSignalTypes()
  );

  // Create backtest mutation
  const createBacktestMutation = useMutation(
    (request: BacktestCreateRequest) => backtestApi.createBacktest(request),
    {
      onSuccess: (data) => {
        setRunResult({ success: true, runId: data.run_id });
        setIsRunning(false);
        setActiveStep(2); // Move to results step
      },
      onError: (error: any) => {
        setRunResult({ 
          success: false, 
          error: error.response?.data?.detail || error.message || 'Failed to create backtest' 
        });
        setIsRunning(false);
        setActiveStep(2); // Move to results step even on error
      },
    }
  );

  const handleInputChange = (field: keyof BacktestCreateRequest, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Validate name when it changes
    if (field === 'name') {
      validateBacktestName(value);
    }
  };

  const validateBacktestName = async (name: string) => {
    // Clear previous validation state
    setNameValidation({ isValid: true, message: '', isChecking: false });

    // Check for empty or whitespace-only names
    if (!name || name.trim() === '') {
      setNameValidation({ isValid: false, message: 'Name is required', isChecking: false });
      return;
    }

    // Check for very long names (assuming 100 character limit)
    if (name.length > 100) {
      setNameValidation({ isValid: false, message: 'Name must be 100 characters or less', isChecking: false });
      return;
    }

    // Check for uniqueness
    setNameValidation({ isValid: true, message: '', isChecking: true });
    
    try {
      const result = await backtestApi.checkBacktestName(name);
      if (result.exists) {
        setNameValidation({ isValid: false, message: 'This backtest name already exists. Please choose a different name.', isChecking: false });
      } else {
        setNameValidation({ isValid: true, message: '', isChecking: false });
      }
    } catch (error) {
      console.error('Error checking backtest name:', error);
      setNameValidation({ isValid: false, message: 'Error checking name availability', isChecking: false });
    }
  };

  const validateForm = (): boolean => {
    const required = ['name', 'start_date', 'end_date', 'universe_id', 'signals'];
    return required.every(field => formData[field as keyof BacktestCreateRequest]) && 
           nameValidation.isValid && 
           !nameValidation.isChecking;
  };

  const runPreflightChecks = async (): Promise<PreflightResult> => {
    const errors: string[] = [];
    const warnings: string[] = [];
    const signalGaps: Array<{ ticker: string; signal: string; date: string }> = [];
    let rebalancingDates: string[] = [];

    try {
      // 1. Name validation
      if (!formData.name || formData.name.trim() === '') {
        errors.push('Backtest name is required');
        return { isValid: false, errors, warnings, rebalancingDates, signalGaps };
      }

      if (!nameValidation.isValid) {
        errors.push(nameValidation.message);
        return { isValid: false, errors, warnings, rebalancingDates, signalGaps };
      }

      if (nameValidation.isChecking) {
        errors.push('Name validation is still in progress');
        return { isValid: false, errors, warnings, rebalancingDates, signalGaps };
      }

      // 2. Universe validation
      if (!formData.universe_id) {
        errors.push('Universe must be selected');
        return { isValid: false, errors, warnings, rebalancingDates, signalGaps };
      }

      // 2.5. Signal date range validation
      if (formData.start_date && formData.end_date) {
        const startDate = new Date(formData.start_date);
        const endDate = new Date(formData.end_date);
        const availableStartDate = new Date('2020-10-17');  // Updated to actual signal range
        const availableEndDate = new Date('2025-09-21');    // Updated to actual signal range
        
        if (startDate < availableStartDate || endDate > availableEndDate) {
          warnings.push(`Selected date range (${formData.start_date} to ${formData.end_date}) extends beyond available signal data (2020-10-17 to 2025-09-21). Backtest will only use available signal data.`);
        }
      }

      const universe = universesData?.universes.find(u => u.id === formData.universe_id);
      if (!universe) {
        errors.push('Selected universe not found');
        return { isValid: false, errors, warnings, rebalancingDates, signalGaps };
      }

      if (universe.ticker_count < 5) {
        errors.push(`Universe "${universe.name}" must contain at least 5 tickers. Current count: ${universe.ticker_count}`);
        return { isValid: false, errors, warnings, rebalancingDates, signalGaps };
      }

      // 2. Get universe tickers for validation
      const tickersData = await universeApi.getUniverseTickers(formData.universe_id);
      const tickers = tickersData.tickers.map(t => t.ticker);

      // 3. Validate tickers
      const validationResults = await universeApi.validateTickers(tickers);
      const invalidTickers = validationResults.filter(r => !r.is_valid);
      if (invalidTickers.length > 0) {
        errors.push(`Invalid tickers found: ${invalidTickers.map(t => t.ticker).join(', ')}`);
      }

      // 4. Generate rebalancing dates based on selected frequency
      if (formData.start_date && formData.end_date) {
        const startDate = new Date(formData.start_date);
        const endDate = new Date(formData.end_date);
        const frequency = formData.rebalancing_frequency || 'monthly';
        
        const current = new Date(startDate);
        
        if (frequency === 'weekly') {
          // Weekly rebalancing - every 7 days
          while (current <= endDate) {
            rebalancingDates.push(current.toISOString().split('T')[0]);
            current.setDate(current.getDate() + 7);
          }
        } else if (frequency === 'monthly') {
          // Monthly rebalancing - first day of each month
          while (current <= endDate) {
            rebalancingDates.push(current.toISOString().split('T')[0]);
            current.setMonth(current.getMonth() + 1);
          }
        } else if (frequency === 'quarterly') {
          // Quarterly rebalancing - every 3 months
          while (current <= endDate) {
            rebalancingDates.push(current.toISOString().split('T')[0]);
            current.setMonth(current.getMonth() + 3);
          }
        }
      }

      // 5. Validate signals exist
      if (!formData.signals || formData.signals.length === 0) {
        errors.push('At least one signal must be selected');
      } else {
        const availableSignals = signalTypesData?.signal_types.map(s => s.signal_id) || [];
        const invalidSignals = formData.signals.filter(s => !availableSignals.includes(s));
        if (invalidSignals.length > 0) {
          errors.push(`Invalid signals: ${invalidSignals.join(', ')}`);
        }
      }

      // 6. Validate max weight
      if (formData.max_weight !== undefined && (formData.max_weight <= 0 || formData.max_weight > 1)) {
        errors.push('Max weight must be between 0 and 1');
      }

      // 7. Check for signal gaps (simplified - would need actual data checking)
      // This would require checking the database for missing signal scores
      // For now, we'll just add a warning if signals are selected
      if (formData.signals && formData.signals.length > 0) {
        warnings.push('Signal availability will be checked during execution');
      }

    } catch (error: any) {
      errors.push(`Preflight check failed: ${error.message}`);
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
      rebalancingDates,
      signalGaps
    };
  };

  const handlePreflight = async () => {
    setIsValidating(true);
    try {
      const result = await runPreflightChecks();
      setPreflightResult(result);
      if (result.isValid) {
        setActiveStep(1);
      }
    } finally {
      setIsValidating(false);
    }
  };

  const handleRunBacktest = async () => {
    if (!validateForm() || !preflightResult?.isValid) return;

    setIsRunning(true);
    setRunResult(null);

    const request: BacktestCreateRequest = {
      name: formData.name,
      start_date: formData.start_date!,
      end_date: formData.end_date!,
      universe_id: formData.universe_id!,
      signals: formData.signals!,
      initial_capital: formData.initial_capital,
      rebalancing_frequency: formData.rebalancing_frequency,
      evaluation_period: formData.evaluation_period,
      transaction_costs: formData.transaction_costs,
      max_weight: formData.max_weight,
      min_weight: formData.min_weight,
      risk_aversion: formData.risk_aversion,
      benchmark_ticker: formData.benchmark_ticker,
      use_equal_weight_benchmark: formData.use_equal_weight_benchmark,
      min_lookback_days: formData.min_lookback_days,
      max_lookback_days: formData.max_lookback_days,
      signal_weights: formData.signal_weights,
      signal_combination_method: formData.signal_combination_method,
      forward_fill_signals: formData.forward_fill_signals,
    };

    createBacktestMutation.mutate(request);
  };

  const handleViewResults = () => {
    if (runResult?.runId) {
      navigate(`/backtest/${runResult.runId}`);
    }
  };

  const steps = [
    'Configure Backtest',
    'Review & Confirm',
    'Execute & Results'
  ];

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Logo size="medium" showText={false} clickable={true} />
            <Typography variant="h4" component="h1" sx={{ fontWeight: 700 }}>
              Run Backtest
            </Typography>
          </Box>
          <Typography variant="body1" color="text.secondary">
            Configure and execute a quantitative trading strategy backtest
          </Typography>
        </Box>

        {/* Stepper */}
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Stepper activeStep={activeStep} orientation="horizontal">
              {steps.map((label) => (
                <Step key={label}>
                  <StepLabel>{label}</StepLabel>
                </Step>
              ))}
            </Stepper>
          </CardContent>
        </Card>

        {/* Step 1: Configuration */}
        {activeStep === 0 && (
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ mb: 3 }}>
                Backtest Configuration
              </Typography>
              
              <Grid container spacing={3}>
                {/* Backtest Name */}
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Backtest Name"
                    value={formData.name || ''}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    required
                    error={!nameValidation.isValid}
                    helperText={
                      nameValidation.isChecking 
                        ? "Checking name availability..." 
                        : nameValidation.message || "Enter a descriptive name for this backtest"
                    }
                    InputProps={{
                      endAdornment: nameValidation.isChecking ? (
                        <CircularProgress size={20} />
                      ) : nameValidation.isValid && formData.name ? (
                        <CheckCircleIcon color="success" />
                      ) : null
                    }}
                  />
                </Grid>

                {/* Universe Selection */}
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth required>
                    <InputLabel>Universe</InputLabel>
                    <Select
                      value={formData.universe_id || ''}
                      onChange={(e) => handleInputChange('universe_id', e.target.value)}
                      disabled={universesLoading}
                    >
                      {universesData?.universes.map((universe) => (
                        <MenuItem key={universe.id} value={universe.id}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
                            <Typography>{universe.name}</Typography>
                            <Chip 
                              label={`${universe.ticker_count} tickers`} 
                              size="small" 
                              color="primary" 
                              variant="outlined"
                            />
                          </Box>
                        </MenuItem>
                      ))}
                    </Select>
                    {universesLoading && <FormHelperText>Loading universes...</FormHelperText>}
                  </FormControl>
                </Grid>

                {/* Date Range */}
                <Grid item xs={12} md={6}>
                  <DatePicker
                    label="Start Date"
                    value={formData.start_date ? new Date(formData.start_date) : null}
                    onChange={(date) => handleInputChange('start_date', date?.toISOString().split('T')[0])}
                    slotProps={{ textField: { fullWidth: true, required: true } }}
                  />
                </Grid>

                <Grid item xs={12} md={6}>
                  <DatePicker
                    label="End Date"
                    value={formData.end_date ? new Date(formData.end_date) : null}
                    onChange={(date) => handleInputChange('end_date', date?.toISOString().split('T')[0])}
                    slotProps={{ textField: { fullWidth: true, required: true } }}
                    minDate={formData.start_date ? new Date(formData.start_date) : undefined}
                  />
                </Grid>

                {/* Rebalancing Frequency */}
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth required>
                    <InputLabel>Rebalancing Frequency</InputLabel>
                    <Select
                      value={formData.rebalancing_frequency || 'monthly'}
                      onChange={(e) => handleInputChange('rebalancing_frequency', e.target.value)}
                    >
                      <MenuItem value="weekly">Weekly</MenuItem>
                      <MenuItem value="monthly">Monthly</MenuItem>
                      <MenuItem value="quarterly">Quarterly</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>

                {/* Max Position Weight */}
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Max Position Weight"
                    type="number"
                    value={formData.max_weight || 0.1}
                    onChange={(e) => handleInputChange('max_weight', parseFloat(e.target.value))}
                    inputProps={{ min: 0, max: 1, step: 0.01 }}
                    required
                    helperText="Maximum weight for any single position (0-1)"
                  />
                </Grid>

                {/* Signals Selection */}
                <Grid item xs={12}>
                  <FormControl fullWidth required>
                    <InputLabel>Signals</InputLabel>
                    <Select
                      multiple
                      value={formData.signals || []}
                      onChange={(e) => handleInputChange('signals', e.target.value)}
                      disabled={signalsLoading}
                      renderValue={(selected) => (
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {(selected as string[]).map((value) => (
                            <Chip key={value} label={value} size="small" />
                          ))}
                        </Box>
                      )}
                    >
                      {signalTypesData?.signal_types.map((signal) => (
                        <MenuItem key={signal.signal_id} value={signal.signal_id}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
                            <Typography>{signal.name}</Typography>
                            <Typography variant="caption" color="text.secondary">
                              {signal.signal_id}
                            </Typography>
                          </Box>
                        </MenuItem>
                      ))}
                    </Select>
                    {signalsLoading && <FormHelperText>Loading signals...</FormHelperText>}
                    <FormHelperText>Select at least one signal to use for portfolio construction</FormHelperText>
                  </FormControl>
                </Grid>
              </Grid>

              {/* Preflight Results */}
              {preflightResult && (
                <Box sx={{ mt: 3 }}>
                  {preflightResult.errors.length > 0 && (
                    <Alert severity="error" sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Validation Errors:
                      </Typography>
                      <List dense>
                        {preflightResult.errors.map((error, index) => (
                          <ListItem key={index}>
                            <ListItemIcon>
                              <ErrorIcon color="error" />
                            </ListItemIcon>
                            <ListItemText primary={error} />
                          </ListItem>
                        ))}
                      </List>
                    </Alert>
                  )}

                  {preflightResult.warnings.length > 0 && (
                    <Alert severity="warning" sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Warnings:
                      </Typography>
                      <List dense>
                        {preflightResult.warnings.map((warning, index) => (
                          <ListItem key={index}>
                            <ListItemIcon>
                              <WarningIcon color="warning" />
                            </ListItemIcon>
                            <ListItemText primary={warning} />
                          </ListItem>
                        ))}
                      </List>
                    </Alert>
                  )}

                  {preflightResult.isValid && (
                    <Alert severity="success">
                      <Typography variant="subtitle2" gutterBottom>
                        All preflight checks passed!
                      </Typography>
                      <Typography variant="body2">
                        Ready to proceed with backtest execution.
                      </Typography>
                    </Alert>
                  )}
                </Box>
              )}

              {/* Action Buttons */}
              <Box sx={{ mt: 4, display: 'flex', gap: 2 }}>
                <Button
                  variant="contained"
                  onClick={handlePreflight}
                  disabled={!validateForm() || isValidating}
                  startIcon={isValidating ? <CircularProgress size={20} /> : <CheckCircleIcon />}
                >
                  {isValidating ? 'Validating...' : 'Validate Configuration'}
                </Button>
                <Button
                  variant="outlined"
                  onClick={() => navigate('/dashboard')}
                  disabled={isValidating}
                >
                  Cancel
                </Button>
              </Box>
            </CardContent>
          </Card>
        )}

        {/* Step 2: Review & Confirm */}
        {activeStep === 1 && preflightResult?.isValid && (
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
                  onClick={handleRunBacktest}
                  disabled={isRunning}
                  startIcon={isRunning ? <CircularProgress size={20} /> : <PlayArrowIcon />}
                >
                  {isRunning ? 'Running Backtest...' : 'Run Backtest'}
                </Button>
                <Button
                  variant="outlined"
                  onClick={() => setActiveStep(0)}
                  startIcon={<EditIcon />}
                >
                  Edit Configuration
                </Button>
                <Button
                  variant="outlined"
                  onClick={() => navigate('/dashboard')}
                >
                  Cancel
                </Button>
              </Box>
            </CardContent>
          </Card>
        )}

        {/* Step 3: Results */}
        {activeStep === 2 && runResult && (
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
                    onClick={handleViewResults}
                    startIcon={<VisibilityIcon />}
                  >
                    View Results
                  </Button>
                )}
                <Button
                  variant="outlined"
                  onClick={() => {
                    setActiveStep(0);
                    setRunResult(null);
                    setPreflightResult(null);
                    setFormData({
                      rebalancing_frequency: 'monthly',
                      max_weight: 0.1,
                      min_weight: 0.0,
                      initial_capital: 10000,
                      transaction_costs: 0.001,
                      risk_aversion: 0.5,
                      benchmark_ticker: 'SPY',
                      use_equal_weight_benchmark: true,
                      min_lookback_days: 252,
                      max_lookback_days: 756,
                      signal_combination_method: 'equal_weight',
                      forward_fill_signals: true,
                    });
                  }}
                >
                  Run Another Backtest
                </Button>
                <Button
                  variant="outlined"
                  onClick={() => navigate('/dashboard')}
                >
                  Back to Dashboard
                </Button>
              </Box>
            </CardContent>
          </Card>
        )}
      </Box>
    </LocalizationProvider>
  );
};

export default RunBacktest;
