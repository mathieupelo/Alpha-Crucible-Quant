/**
 * Portfolio Detail Component
 * Displays detailed information about a specific portfolio
 */

import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Alert,
  Skeleton,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Close as CloseIcon,
} from '@mui/icons-material';
import { useQuery } from 'react-query';

import { portfolioApi } from '@/services/api';
import { Portfolio, Position } from '@/types';

interface PortfolioDetailProps {
  portfolio: Portfolio;
  onClose: () => void;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index, ...other }) => {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`portfolio-tabpanel-${index}`}
      aria-labelledby={`portfolio-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
};

const PortfolioDetail: React.FC<PortfolioDetailProps> = ({ portfolio, onClose }) => {
  const [tabValue, setTabValue] = useState(0);

  // Fetch detailed portfolio data
  const {
    data: portfolioDetails,
    isLoading: portfolioLoading,
    error: portfolioError,
  } = useQuery(
    ['portfolio-details', portfolio.id],
    () => portfolioApi.getPortfolio(portfolio.id),
    {
      enabled: !!portfolio.id,
    }
  );

  // Fetch signal scores data
  const {
    data: signalData,
    isLoading: signalLoading,
    error: signalError,
  } = useQuery(
    ['portfolio-signals', portfolio.id],
    () => portfolioApi.getPortfolioSignals(portfolio.id),
    {
      enabled: !!portfolio.id,
    }
  );

  // Fetch combined scores data
  const {
    data: scoreData,
    isLoading: scoreLoading,
    error: scoreError,
    refetch: refetchScores,
  } = useQuery(
    ['portfolio-scores', portfolio.id],
    () => {
      console.log(`Fetching combined scores for portfolio ${portfolio.id}`);
      return portfolioApi.getPortfolioScores(portfolio.id);
    },
    {
      enabled: !!portfolio.id,
      retry: 2,
      retryDelay: 1000,
      onSuccess: (data) => {
        console.log('Combined scores loaded successfully:', data);
      },
      onError: (error) => {
        console.error('Error loading combined scores:', error);
      },
    }
  );

  // Fetch universe tickers data
  const {
    data: universeTickersData,
    isLoading: universeTickersLoading,
  } = useQuery(
    ['portfolio-universe-tickers', portfolio.id],
    () => portfolioApi.getPortfolioUniverseTickers(portfolio.id),
    {
      enabled: !!portfolio.id,
    }
  );

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // Use universe tickers as the master list for all tabs
  const universeTickers = universeTickersData?.tickers || [];
  
  // Sort the universe tickers for consistent display
  const allTickers = universeTickers.sort();
  
  // Note: Now we show ALL tickers from the universe, not just those with positions
  // This allows users to see the complete universe context

  const getWeightColor = (weight: number): 'success' | 'error' | 'default' => {
    if (weight > 0.1) return 'success';
    if (weight < 0.01) return 'error';
    return 'default';
  };

  if (portfolioError) {
    return (
      <Dialog open={true} onClose={onClose} maxWidth="md" fullWidth>
        <DialogTitle>Portfolio Details</DialogTitle>
        <DialogContent>
          <Alert severity="error">
            Failed to load portfolio details. Please try again.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Close</Button>
        </DialogActions>
      </Dialog>
    );
  }

  return (
    <Dialog open={true} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography variant="h6">
              Portfolio Details - {portfolio.asof_date}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Universe: {portfolio.universe_name || 'Unknown'}
            </Typography>
          </Box>
          <Button
            startIcon={<CloseIcon />}
            onClick={onClose}
            size="small"
          >
            Close
          </Button>
        </Box>
      </DialogTitle>
      
      <DialogContent dividers>
        {/* Portfolio Summary */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Method
                </Typography>
                <Typography variant="h6">
                  {portfolio.method}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Portfolio Value
                </Typography>
                <Typography variant="h6">
                  ${portfolio.total_value?.toFixed(2) || 'N/A'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Positions
                </Typography>
                <Typography variant="h6">
                  {portfolio.position_count || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Portfolio ID
                </Typography>
                <Typography variant="h6">
                  #{portfolio.id}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Tabs for different views */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
          <Tabs value={tabValue} onChange={handleTabChange}>
            <Tab label="Weights" />
            <Tab label="Signal Scores" />
            <Tab label="Combined Scores" />
          </Tabs>
        </Box>

        {/* Weights Tab */}
        <TabPanel value={tabValue} index={0}>
          <Typography variant="h6" gutterBottom>
            Portfolio Weights
          </Typography>
          <Alert severity="info" sx={{ mb: 2 }}>
            Portfolio weights for all tickers in the universe. Tickers without allocations show 0% weight.
          </Alert>
          {portfolioLoading || universeTickersLoading ? (
            <Box>
              {[...Array(5)].map((_, index) => (
                <Skeleton key={index} variant="rectangular" height={60} sx={{ mb: 1 }} />
              ))}
            </Box>
          ) : (
            <TableContainer component={Paper} variant="outlined" sx={{ maxHeight: 400, overflow: 'auto' }}>
              <Table stickyHeader>
                <TableHead>
                  <TableRow>
                    <TableCell>Ticker</TableCell>
                    <TableCell align="right">Weight</TableCell>
                    <TableCell align="right">Price Used</TableCell>
                    <TableCell align="right">Value</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {allTickers.map((ticker) => {
                    // Find position data for this ticker
                    const position = portfolioDetails?.positions?.find((pos: Position) => pos.ticker === ticker);
                    
                    return (
                      <TableRow key={ticker}>
                        <TableCell>
                          <Typography variant="body1" sx={{ fontWeight: 500 }}>
                            {ticker}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Chip
                            label={position ? `${(position.weight * 100).toFixed(1)}%` : '0.0%'}
                            color={position ? getWeightColor(position.weight) : 'default'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="right">
                          {position ? `$${position.price_used.toFixed(2)}` : '—'}
                        </TableCell>
                        <TableCell align="right">
                          {position ? `$${(position.weight * 10000).toFixed(2)}` : '$0.00'}
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </TabPanel>

        {/* Signal Scores Tab */}
        <TabPanel value={tabValue} index={1}>
          <Typography variant="h6" gutterBottom>
            Signal Scores
          </Typography>
          <Alert severity="info" sx={{ mb: 2 }}>
            Signal scores for all tickers in the universe. Values typically range from -1 to 1 (depending on the signal).
            Missing scores are shown as —.
          </Alert>
          {signalLoading || universeTickersLoading ? (
            <Box>
              <Skeleton variant="rectangular" height={200} />
            </Box>
          ) : signalError ? (
            <Alert severity="error" sx={{ mb: 2 }}>
              Failed to load signal data. Please try again.
            </Alert>
          ) : signalData?.signals && signalData.signals.length > 0 ? (
            (() => {
              // Get available signals from the first signal data entry
              const availableSignals = (signalData.signals[0]?.available_signals || []) as string[];
              
              // Handle case where no signals are available
              if (availableSignals.length === 0) {
                return (
                  <TableContainer component={Paper} variant="outlined" sx={{ maxHeight: 400, overflow: 'auto' }}>
                    <Table stickyHeader>
                      <TableHead>
                        <TableRow>
                          <TableCell>Ticker</TableCell>
                          <TableCell align="right">Signal Scores</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {allTickers.map((ticker) => (
                          <TableRow key={ticker}>
                            <TableCell>
                              <Typography variant="body1" sx={{ fontWeight: 500 }}>
                                {ticker}
                              </Typography>
                            </TableCell>
                            <TableCell align="right">
                              —
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                );
              }
              
              // Remove duplicates and sort signals
              const uniqueSignals = [...new Set(availableSignals)];
              const sortedSignals = uniqueSignals.sort();
              
              // Log warning if duplicates were found
              if (uniqueSignals.length !== availableSignals.length) {
                console.warn('Duplicate signal names found in portfolio data');
              }
              
              return (
                <TableContainer component={Paper} variant="outlined" sx={{ maxHeight: 400, overflow: 'auto' }}>
                  <Table stickyHeader>
                    <TableHead>
                      <TableRow>
                        <TableCell>Ticker</TableCell>
                        {sortedSignals.map((signalName) => (
                          <TableCell key={signalName} align="right">
                            {signalName}
                          </TableCell>
                        ))}
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {allTickers.map((ticker) => {
                        // Find signal data for this ticker
                        const tickerSignalData = signalData.signals.find((signal: any) => signal.ticker === ticker);
                        
                        return (
                          <TableRow key={ticker}>
                            <TableCell>
                              <Typography variant="body1" sx={{ fontWeight: 500 }}>
                                {ticker}
                              </Typography>
                            </TableCell>
                            {sortedSignals.map((signalName) => (
                              <TableCell key={signalName} align="right">
                                {tickerSignalData && (tickerSignalData as any)[signalName] !== null && (tickerSignalData as any)[signalName] !== undefined 
                                  ? Number((tickerSignalData as any)[signalName]).toFixed(4) 
                                  : '—'
                                }
                              </TableCell>
                            ))}
                          </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                </TableContainer>
              );
            })()
          ) : (
            // Show all universe tickers even if no signal data
            <TableContainer component={Paper} variant="outlined" sx={{ maxHeight: 400, overflow: 'auto' }}>
              <Table stickyHeader>
                <TableHead>
                  <TableRow>
                    <TableCell>Ticker</TableCell>
                    <TableCell align="right">Signal Scores</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {allTickers.map((ticker) => (
                    <TableRow key={ticker}>
                      <TableCell>
                        <Typography variant="body1" sx={{ fontWeight: 500 }}>
                          {ticker}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        —
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </TabPanel>

        {/* Combined Scores Tab */}
        <TabPanel value={tabValue} index={2}>
          <Typography variant="h6" gutterBottom>
            Combined Scores
          </Typography>
          <Alert severity="info" sx={{ mb: 2 }}>
            Combined signal scores for all tickers in the universe using the equal-weight method. 
            Missing scores are shown as —.
          </Alert>
          <TableContainer component={Paper} variant="outlined" sx={{ maxHeight: 400, overflow: 'auto' }}>
            <Table stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell>Ticker</TableCell>
                  <TableCell align="right">Combined Score</TableCell>
                  <TableCell align="right">Method</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {scoreLoading || universeTickersLoading ? (
                  <TableRow>
                    <TableCell colSpan={3} align="center">
                      <Skeleton variant="text" width="100%" />
                    </TableCell>
                  </TableRow>
                ) : scoreError ? (
                  <TableRow>
                    <TableCell colSpan={3} align="center">
                      <Box sx={{ py: 2 }}>
                        <Typography variant="body2" color="error" gutterBottom>
                          Error loading score data
                        </Typography>
                        <Button 
                          variant="outlined" 
                          size="small" 
                          onClick={() => refetchScores()}
                          sx={{ mt: 1 }}
                        >
                          Retry
                        </Button>
                      </Box>
                    </TableCell>
                  </TableRow>
                ) : scoreData?.scores && scoreData.scores.length > 0 ? (
                  allTickers.map((ticker) => {
                    // Find combined score data for this ticker
                    const tickerScoreData = scoreData.scores.find((score: any) => score.ticker === ticker);
                    
                    return (
                      <TableRow key={ticker}>
                        <TableCell>
                          <Typography variant="body1" sx={{ fontWeight: 500 }}>
                            {ticker}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          {tickerScoreData && tickerScoreData.combined_score !== null && tickerScoreData.combined_score !== undefined 
                            ? Number(tickerScoreData.combined_score).toFixed(4) 
                            : '—'
                          }
                        </TableCell>
                        <TableCell align="right">
                          <Chip 
                            label={tickerScoreData?.method || '—'} 
                            size="small" 
                            variant="outlined"
                          />
                        </TableCell>
                      </TableRow>
                    );
                  })
                ) : (
                  // Show all universe tickers even if no score data
                  allTickers.map((ticker) => (
                    <TableRow key={ticker}>
                      <TableCell>
                        <Typography variant="body1" sx={{ fontWeight: 500 }}>
                          {ticker}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        —
                      </TableCell>
                      <TableCell align="right">
                        <Chip 
                          label="—" 
                          size="small" 
                          variant="outlined"
                        />
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default PortfolioDetail;

