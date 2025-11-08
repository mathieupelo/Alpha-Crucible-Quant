/**
 * Run Backtest Page
 * Allows users to configure and run backtests with preflight checks
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Stepper,
  Step,
  StepLabel,
} from '@mui/material';

import Logo from '@/components/common/Logo';
import { useBacktestConfig } from '@/hooks/useBacktestConfig';
import { BacktestConfigForm } from '@/components/backtests/BacktestConfigForm';
import { PreflightReview } from '@/components/backtests/PreflightReview';
import { BacktestResults } from '@/components/backtests/BacktestResults';

const RunBacktest: React.FC = () => {
  const navigate = useNavigate();
  
  const {
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
    handleInputChange,
    validateForm,
    handlePreflight,
    handleRunBacktest,
    handleViewResults,
    resetForm,
  } = useBacktestConfig();

  const steps = [
    'Configure Backtest',
    'Review & Confirm',
    'Execute & Results'
  ];

  return (
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
        <BacktestConfigForm
          formData={formData}
          nameValidation={nameValidation}
          preflightResult={preflightResult}
          isValidating={isValidating}
          universesData={universesData}
          universesLoading={universesLoading}
          signalTypesData={signalTypesData}
          signalsLoading={signalsLoading}
          onInputChange={handleInputChange}
          onValidate={handlePreflight}
          onCancel={() => navigate('/backtest')}
          canProceed={validateForm()}
        />
        )}

        {/* Step 2: Review & Confirm */}
        {activeStep === 1 && preflightResult?.isValid && (
        <PreflightReview
          formData={formData}
          preflightResult={preflightResult}
          universesData={universesData}
          isRunning={isRunning}
          onRun={handleRunBacktest}
          onEdit={() => setActiveStep(0)}
          onCancel={() => navigate('/backtest')}
        />
        )}

        {/* Step 3: Results */}
        {activeStep === 2 && runResult && (
        <BacktestResults
          runResult={runResult}
          onViewResults={handleViewResults}
          onRunAnother={resetForm}
          onCancel={() => navigate('/backtest')}
        />
        )}
      </Box>
  );
};

export default RunBacktest;
