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
  } = useQuery(
    ['portfolio-scores', portfolio.id],
    () => portfolioApi.getPortfolioScores(portfolio.id),
    {
      enabled: !!portfolio.id,
    }
  );

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

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
          <Typography variant="h6">
            Portfolio Details - {portfolio.asof_date}
          </Typography>
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
                  Cash Allocation
                </Typography>
                <Typography variant="h6">
                  ${portfolio.cash.toFixed(2)}
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
            <Tab label="Positions" />
            <Tab label="Signal Scores" />
            <Tab label="Combined Scores" />
          </Tabs>
        </Box>

        {/* Positions Tab */}
        <TabPanel value={tabValue} index={0}>
          <Typography variant="h6" gutterBottom>
            Portfolio Positions
          </Typography>
          {portfolioLoading ? (
            <Box>
              {[...Array(5)].map((_, index) => (
                <Skeleton key={index} variant="rectangular" height={60} sx={{ mb: 1 }} />
              ))}
            </Box>
          ) : (
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Ticker</TableCell>
                    <TableCell align="right">Weight</TableCell>
                    <TableCell align="right">Price Used</TableCell>
                    <TableCell align="right">Value</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {portfolioDetails?.positions?.map((position: Position) => (
                    <TableRow key={position.id}>
                      <TableCell>
                        <Typography variant="body1" sx={{ fontWeight: 500 }}>
                          {position.ticker}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Chip
                          label={`${(position.weight * 100).toFixed(1)}%`}
                          color={getWeightColor(position.weight)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="right">
                        ${position.price_used.toFixed(2)}
                      </TableCell>
                      <TableCell align="right">
                        ${(position.weight * 10000).toFixed(2)}
                      </TableCell>
                    </TableRow>
                  ))}
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
            Signal scores for each stock at this portfolio date. Values range from -1 to 1.
          </Alert>
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Ticker</TableCell>
                  <TableCell align="right">RSI</TableCell>
                  <TableCell align="right">SMA</TableCell>
                  <TableCell align="right">MACD</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {signalLoading ? (
                  <TableRow>
                    <TableCell colSpan={4} align="center">
                      <Skeleton variant="text" width="100%" />
                    </TableCell>
                  </TableRow>
                ) : signalError ? (
                  <TableRow>
                    <TableCell colSpan={4} align="center">
                      <Typography variant="body2" color="error">
                        Error loading signal data
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : signalData?.signals && signalData.signals.length > 0 ? (
                  signalData.signals.map((signal: any, index: number) => (
                    <TableRow key={index}>
                      <TableCell>{signal.ticker}</TableCell>
                      <TableCell align="right">
                        {signal.rsi !== null ? signal.rsi.toFixed(4) : 'N/A'}
                      </TableCell>
                      <TableCell align="right">
                        {signal.sma !== null ? signal.sma.toFixed(4) : 'N/A'}
                      </TableCell>
                      <TableCell align="right">
                        {signal.macd !== null ? signal.macd.toFixed(4) : 'N/A'}
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={4} align="center">
                      <Typography variant="body2" color="text.secondary">
                        No signal data available for this portfolio
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        {/* Combined Scores Tab */}
        <TabPanel value={tabValue} index={2}>
          <Typography variant="h6" gutterBottom>
            Combined Scores
          </Typography>
          <Alert severity="info" sx={{ mb: 2 }}>
            Combined signal scores for each stock using the equal-weight method.
          </Alert>
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Ticker</TableCell>
                  <TableCell align="right">Combined Score</TableCell>
                  <TableCell align="right">Method</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {scoreLoading ? (
                  <TableRow>
                    <TableCell colSpan={3} align="center">
                      <Skeleton variant="text" width="100%" />
                    </TableCell>
                  </TableRow>
                ) : scoreError ? (
                  <TableRow>
                    <TableCell colSpan={3} align="center">
                      <Typography variant="body2" color="error">
                        Error loading score data
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : scoreData?.scores && scoreData.scores.length > 0 ? (
                  scoreData.scores.map((score: any, index: number) => (
                    <TableRow key={index}>
                      <TableCell>{score.ticker}</TableCell>
                      <TableCell align="right">
                        {score.combined_score !== null ? score.combined_score.toFixed(4) : 'N/A'}
                      </TableCell>
                      <TableCell align="right">{score.method}</TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={3} align="center">
                      <Typography variant="body2" color="text.secondary">
                        No combined score data available for this portfolio
                      </Typography>
                    </TableCell>
                  </TableRow>
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

