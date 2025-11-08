/**
 * Backtest Configuration Form Component
 * Handles the form for configuring backtest parameters
 */

import React from 'react';
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
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  CircularProgress,
  FormHelperText,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { BacktestCreateRequest } from '@/types';
import { useTheme } from '@/contexts/ThemeContext';
import { PreflightResult, NameValidation } from '@/hooks/useBacktestConfig';

interface BacktestConfigFormProps {
  formData: Partial<BacktestCreateRequest>;
  nameValidation: NameValidation;
  preflightResult: PreflightResult | null;
  isValidating: boolean;
  universesData?: { universes: Array<{ id: number; name: string; ticker_count: number }> };
  universesLoading: boolean;
  signalTypesData?: { signal_types: Array<{ signal_id: string; name: string }> };
  signalsLoading: boolean;
  onInputChange: (field: keyof BacktestCreateRequest, value: any) => void;
  onValidate: () => void;
  onCancel: () => void;
  canProceed: boolean;
}

export const BacktestConfigForm: React.FC<BacktestConfigFormProps> = ({
  formData,
  nameValidation,
  preflightResult,
  isValidating,
  universesData,
  universesLoading,
  signalTypesData,
  signalsLoading,
  onInputChange,
  onValidate,
  onCancel,
  canProceed,
}) => {
  const { isDarkMode } = useTheme();

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
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
                onChange={(e) => onInputChange('name', e.target.value)}
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
                <InputLabel 
                  sx={{
                    color: isDarkMode ? '#94a3b8' : '#64748b',
                    '&.Mui-focused': {
                      color: isDarkMode ? '#2563eb' : '#1d4ed8',
                    }
                  }}
                >
                  Universe
                </InputLabel>
                <Select
                  value={formData.universe_id || ''}
                  onChange={(e) => onInputChange('universe_id', e.target.value)}
                  disabled={universesLoading}
                  sx={{
                    '& .MuiSelect-select': {
                      py: 2,
                    },
                    background: isDarkMode
                      ? 'linear-gradient(145deg, #1e293b 0%, #334155 100%)'
                      : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
                    '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: isDarkMode ? 'rgba(148, 163, 184, 0.3)' : 'rgba(148, 163, 184, 0.4)',
                    },
                    '&:hover .MuiOutlinedInput-notchedOutline': {
                      borderColor: isDarkMode ? '#2563eb' : '#1d4ed8',
                    },
                    '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                      borderColor: isDarkMode ? '#2563eb' : '#1d4ed8',
                    },
                  }}
                  MenuProps={{
                    PaperProps: {
                      sx: {
                        background: isDarkMode
                          ? 'linear-gradient(145deg, #1e293b 0%, #334155 100%)'
                          : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
                        border: isDarkMode
                          ? '1px solid rgba(148, 163, 184, 0.3)'
                          : '1px solid rgba(148, 163, 184, 0.4)',
                        boxShadow: isDarkMode
                          ? '0 8px 32px 0 rgba(0, 0, 0, 0.5), 0 4px 16px 0 rgba(0, 0, 0, 0.4)'
                          : '0 8px 32px 0 rgba(0, 0, 0, 0.2), 0 4px 16px 0 rgba(0, 0, 0, 0.15)',
                        '& .MuiMenuItem-root': {
                          color: isDarkMode ? '#e2e8f0' : '#1e293b',
                          '&:hover': {
                            backgroundColor: isDarkMode ? 'rgba(37, 99, 235, 0.1)' : 'rgba(37, 99, 235, 0.05)',
                          },
                          '&.Mui-selected': {
                            backgroundColor: isDarkMode ? 'rgba(37, 99, 235, 0.2)' : 'rgba(37, 99, 235, 0.1)',
                            '&:hover': {
                              backgroundColor: isDarkMode ? 'rgba(37, 99, 235, 0.3)' : 'rgba(37, 99, 235, 0.15)',
                            },
                          },
                        },
                      },
                    },
                  }}
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
                onChange={(date) => onInputChange('start_date', date?.toISOString().split('T')[0])}
                slotProps={{ 
                  textField: { 
                    fullWidth: true, 
                    required: true,
                    sx: {
                      '& .MuiOutlinedInput-root': {
                        background: isDarkMode
                          ? 'linear-gradient(145deg, #1e293b 0%, #334155 100%)'
                          : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
                        '& .MuiOutlinedInput-notchedOutline': {
                          borderColor: isDarkMode ? 'rgba(148, 163, 184, 0.3)' : 'rgba(148, 163, 184, 0.4)',
                        },
                        '&:hover .MuiOutlinedInput-notchedOutline': {
                          borderColor: isDarkMode ? '#2563eb' : '#1d4ed8',
                        },
                        '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                          borderColor: isDarkMode ? '#2563eb' : '#1d4ed8',
                        },
                      },
                      '& .MuiInputLabel-root': {
                        color: isDarkMode ? '#94a3b8' : '#64748b',
                        '&.Mui-focused': {
                          color: isDarkMode ? '#2563eb' : '#1d4ed8',
                        }
                      },
                    }
                  },
                }}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <DatePicker
                label="End Date"
                value={formData.end_date ? new Date(formData.end_date) : null}
                onChange={(date) => onInputChange('end_date', date?.toISOString().split('T')[0])}
                slotProps={{ 
                  textField: { 
                    fullWidth: true, 
                    required: true,
                    sx: {
                      '& .MuiOutlinedInput-root': {
                        background: isDarkMode
                          ? 'linear-gradient(145deg, #1e293b 0%, #334155 100%)'
                          : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
                        '& .MuiOutlinedInput-notchedOutline': {
                          borderColor: isDarkMode ? 'rgba(148, 163, 184, 0.3)' : 'rgba(148, 163, 184, 0.4)',
                        },
                        '&:hover .MuiOutlinedInput-notchedOutline': {
                          borderColor: isDarkMode ? '#2563eb' : '#1d4ed8',
                        },
                        '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                          borderColor: isDarkMode ? '#2563eb' : '#1d4ed8',
                        },
                      },
                      '& .MuiInputLabel-root': {
                        color: isDarkMode ? '#94a3b8' : '#64748b',
                        '&.Mui-focused': {
                          color: isDarkMode ? '#2563eb' : '#1d4ed8',
                        }
                      },
                    }
                  },
                }}
                minDate={formData.start_date ? new Date(formData.start_date) : undefined}
              />
            </Grid>

            {/* Rebalancing Frequency */}
            <Grid item xs={12} md={6}>
              <FormControl fullWidth required>
                <InputLabel 
                  sx={{
                    color: isDarkMode ? '#94a3b8' : '#64748b',
                    '&.Mui-focused': {
                      color: isDarkMode ? '#2563eb' : '#1d4ed8',
                    }
                  }}
                >
                  Rebalancing Frequency
                </InputLabel>
                <Select
                  value={formData.rebalancing_frequency || 'monthly'}
                  onChange={(e) => onInputChange('rebalancing_frequency', e.target.value)}
                  sx={{
                    '& .MuiSelect-select': {
                      py: 2,
                    },
                    background: isDarkMode
                      ? 'linear-gradient(145deg, #1e293b 0%, #334155 100%)'
                      : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
                    '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: isDarkMode ? 'rgba(148, 163, 184, 0.3)' : 'rgba(148, 163, 184, 0.4)',
                    },
                    '&:hover .MuiOutlinedInput-notchedOutline': {
                      borderColor: isDarkMode ? '#2563eb' : '#1d4ed8',
                    },
                    '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                      borderColor: isDarkMode ? '#2563eb' : '#1d4ed8',
                    },
                  }}
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
                onChange={(e) => onInputChange('max_weight', parseFloat(e.target.value))}
                inputProps={{ min: 0, max: 1, step: 0.01 }}
                required
                helperText="Maximum weight for any single position (0-1)"
              />
            </Grid>

            {/* Signals Selection */}
            <Grid item xs={12}>
              <FormControl fullWidth required>
                <InputLabel 
                  sx={{
                    color: isDarkMode ? '#94a3b8' : '#64748b',
                    '&.Mui-focused': {
                      color: isDarkMode ? '#2563eb' : '#1d4ed8',
                    }
                  }}
                >
                  Signals
                </InputLabel>
                <Select
                  multiple
                  value={formData.signals || []}
                  onChange={(e) => onInputChange('signals', e.target.value)}
                  disabled={signalsLoading}
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {(selected as string[]).map((value) => (
                        <Chip key={value} label={value} size="small" />
                      ))}
                    </Box>
                  )}
                  sx={{
                    '& .MuiSelect-select': {
                      py: 2,
                    },
                    background: isDarkMode
                      ? 'linear-gradient(145deg, #1e293b 0%, #334155 100%)'
                      : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
                    '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: isDarkMode ? 'rgba(148, 163, 184, 0.3)' : 'rgba(148, 163, 184, 0.4)',
                    },
                    '&:hover .MuiOutlinedInput-notchedOutline': {
                      borderColor: isDarkMode ? '#2563eb' : '#1d4ed8',
                    },
                    '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                      borderColor: isDarkMode ? '#2563eb' : '#1d4ed8',
                    },
                  }}
                  MenuProps={{
                    PaperProps: {
                      sx: {
                        background: isDarkMode
                          ? 'linear-gradient(145deg, #1e293b 0%, #334155 100%)'
                          : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
                        border: isDarkMode
                          ? '1px solid rgba(148, 163, 184, 0.3)'
                          : '1px solid rgba(148, 163, 184, 0.4)',
                        boxShadow: isDarkMode
                          ? '0 8px 32px 0 rgba(0, 0, 0, 0.5), 0 4px 16px 0 rgba(0, 0, 0, 0.4)'
                          : '0 8px 32px 0 rgba(0, 0, 0, 0.2), 0 4px 16px 0 rgba(0, 0, 0, 0.15)',
                        '& .MuiMenuItem-root': {
                          color: isDarkMode ? '#e2e8f0' : '#1e293b',
                          '&:hover': {
                            backgroundColor: isDarkMode ? 'rgba(37, 99, 235, 0.1)' : 'rgba(37, 99, 235, 0.05)',
                          },
                          '&.Mui-selected': {
                            backgroundColor: isDarkMode ? 'rgba(37, 99, 235, 0.2)' : 'rgba(37, 99, 235, 0.1)',
                            '&:hover': {
                              backgroundColor: isDarkMode ? 'rgba(37, 99, 235, 0.3)' : 'rgba(37, 99, 235, 0.15)',
                            },
                          },
                        },
                      },
                    },
                  }}
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
              onClick={onValidate}
              disabled={!canProceed || isValidating}
              startIcon={isValidating ? <CircularProgress size={20} /> : <CheckCircleIcon />}
            >
              {isValidating ? 'Validating...' : 'Validate Configuration'}
            </Button>
            <Button
              variant="outlined"
              onClick={onCancel}
              disabled={isValidating}
            >
              Cancel
            </Button>
          </Box>
        </CardContent>
      </Card>
    </LocalizationProvider>
  );
};

