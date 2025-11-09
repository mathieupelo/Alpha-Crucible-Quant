/**
 * Custom hook for managing backtest configuration state and logic
 */

import { useState } from 'react';
import { useQuery, useMutation } from 'react-query';
import { useNavigate } from 'react-router-dom';
import { backtestApi, universeApi, signalApi } from '@/services/api';
import { BacktestCreateRequest } from '@/types';

export interface PreflightResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  rebalancingDates: string[];
  signalGaps: Array<{ ticker: string; signal: string; date: string }>;
}

export interface NameValidation {
  isValid: boolean;
  message: string;
  isChecking: boolean;
}

export const useBacktestConfig = () => {
  const navigate = useNavigate();
  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState<Partial<BacktestCreateRequest>>({
    start_date: '2024-01-01',
    end_date: '2024-12-31',
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
  const [nameValidation, setNameValidation] = useState<NameValidation>({ 
    isValid: true, 
    message: '', 
    isChecking: false 
  });

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
        setActiveStep(2);
      },
      onError: (error: any) => {
        setRunResult({ 
          success: false, 
          error: error.response?.data?.detail || error.message || 'Failed to create backtest' 
        });
        setIsRunning(false);
        setActiveStep(2);
      },
    }
  );

  const handleInputChange = (field: keyof BacktestCreateRequest, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    if (field === 'name') {
      validateBacktestName(value);
    }
  };

  const validateBacktestName = async (name: string) => {
    setNameValidation({ isValid: true, message: '', isChecking: false });

    if (!name || name.trim() === '') {
      setNameValidation({ isValid: false, message: 'Name is required', isChecking: false });
      return;
    }

    if (name.length > 100) {
      setNameValidation({ isValid: false, message: 'Name must be 100 characters or less', isChecking: false });
      return;
    }

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

      if (!formData.universe_id) {
        errors.push('Universe must be selected');
        return { isValid: false, errors, warnings, rebalancingDates, signalGaps };
      }

      if (formData.start_date && formData.end_date) {
        const startDate = new Date(formData.start_date);
        const endDate = new Date(formData.end_date);
        const availableStartDate = new Date('2020-10-17');
        const availableEndDate = new Date('2025-09-21');
        
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

      const companiesData = await universeApi.getUniverseCompanies(formData.universe_id);
      const tickers = companiesData.companies.map(c => c.main_ticker).filter(Boolean) as string[];

      const validationResults = await universeApi.validateTickers(tickers);
      const invalidTickers = validationResults.filter(r => !r.is_valid);
      if (invalidTickers.length > 0) {
        errors.push(`Invalid tickers found: ${invalidTickers.map(t => t.ticker).join(', ')}`);
      }

      if (formData.start_date && formData.end_date) {
        const startDate = new Date(formData.start_date);
        const endDate = new Date(formData.end_date);
        const frequency = formData.rebalancing_frequency || 'monthly';
        
        const current = new Date(startDate);
        
        if (frequency === 'daily') {
          while (current <= endDate) {
            rebalancingDates.push(current.toISOString().split('T')[0]);
            current.setDate(current.getDate() + 1);
          }
        } else if (frequency === 'weekly') {
          while (current <= endDate) {
            rebalancingDates.push(current.toISOString().split('T')[0]);
            current.setDate(current.getDate() + 7);
          }
        } else if (frequency === 'monthly') {
          while (current <= endDate) {
            rebalancingDates.push(current.toISOString().split('T')[0]);
            current.setMonth(current.getMonth() + 1);
          }
        } else if (frequency === 'quarterly') {
          while (current <= endDate) {
            rebalancingDates.push(current.toISOString().split('T')[0]);
            current.setMonth(current.getMonth() + 3);
          }
        }
      }

      if (!formData.signals || formData.signals.length === 0) {
        errors.push('At least one signal must be selected');
      } else {
        const availableSignals = signalTypesData?.signal_types.map(s => s.signal_id) || [];
        const invalidSignals = formData.signals.filter(s => !availableSignals.includes(s));
        if (invalidSignals.length > 0) {
          errors.push(`Invalid signals: ${invalidSignals.join(', ')}`);
        }
      }

      if (formData.max_weight !== undefined && (formData.max_weight <= 0 || formData.max_weight > 1)) {
        errors.push('Max weight must be between 0 and 1');
      }

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
      navigate(`/backtest?id=${runResult.runId}`);
    }
  };

  const resetForm = () => {
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
  };

  return {
    // State
    activeStep,
    setActiveStep,
    formData,
    preflightResult,
    isRunning,
    isValidating,
    runResult,
    nameValidation,
    universesData,
    universesLoading,
    signalTypesData,
    signalsLoading,
    
    // Actions
    handleInputChange,
    validateForm,
    handlePreflight,
    handleRunBacktest,
    handleViewResults,
    resetForm,
  };
};

