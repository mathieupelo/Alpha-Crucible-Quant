/**
 * Ticker Manager Page
 * Manage all tickers in the database
 */

import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Autocomplete,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Grid,
  CircularProgress,
  Pagination,
  Skeleton,
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';

import { tickerApi } from '@/services/api';
import { TickerInfo, CompanyInfo, CompanySearchResult } from '@/types';
import Logo from '@/components/common/Logo';
import { useTheme } from '@/contexts/ThemeContext';

// Valid markets list
const VALID_MARKETS = [
  'NYSE', 'NASDAQ', 'NMS', 'NGM', 'NCM', 'NYSEARCA', 'NYSEAMERICAN', 'BATS',
  'OTC', 'OTCQX', 'OTCQB', 'OTCBB', 'PINK',
  'TSX', 'TSXV', 'CSE', 'NEO',
  'LSE', 'AIM', 'Euronext', 'FWB', 'XETRA', 'SWX', 'SIX', 'STO', 'HEL',
  'CPH', 'VTX', 'MCE', 'BRU', 'AMS', 'LIS', 'WSE',
  'TSE', 'JPX', 'JASDAQ',
  'KRX', 'KOSPI', 'KOSDAQ',
  'SSE', 'SZSE', 'HKEX', 'HKSE', 'TPE', 'TWSE', 'TPEx',
  'SGX', 'SET', 'IDX', 'PSE', 'MYX', 'BURSA',
  'NSEI', 'BSE', 'MSEI',
  'ASX', 'NZX',
  'JSE', 'TASE', 'DFM', 'ADX', 'MSM', 'QSE', 'BHB', 'KSE', 'Tadawul',
  'BMV', 'B3', 'BOVESPA', 'BCBA', 'BVL', 'BVC',
  'MOEX', 'MICEX', 'KASE',
  'ADR', 'OTC', 'OTCQX', 'OTCQB', 'OTCBB', 'PINK'
];

const TickerManager: React.FC = () => {
  const { isDarkMode } = useTheme();
  const queryClient = useQueryClient();

  // State for new ticker section
  const [newTicker, setNewTicker] = useState('');
  const [fetchedTickerInfo, setFetchedTickerInfo] = useState<TickerInfo | null>(null);
  const [fetchingTicker, setFetchingTicker] = useState(false);
  const [newTickerError, setNewTickerError] = useState<string | null>(null);
  const [reviewDialogOpen, setReviewDialogOpen] = useState(false);

  // State for alternative ticker section
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<CompanySearchResult[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<CompanySearchResult | null>(null);
  const [companyInfo, setCompanyInfo] = useState<CompanyInfo | null>(null);
  const [alternativeTicker, setAlternativeTicker] = useState('');
  const [selectedMarket, setSelectedMarket] = useState('');
  const [alternativeTickerError, setAlternativeTickerError] = useState<string | null>(null);

  // State for all tickers section
  const [page, setPage] = useState(1);
  const pageSize = 20;

  // State for delete dialog
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [companyToDelete, setCompanyToDelete] = useState<{ company_uid: string; company_name: string | null; main_ticker: string | null } | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [checkingDependencies, setCheckingDependencies] = useState(false);
  const [dependencies, setDependencies] = useState<{ [key: string]: number } | null>(null);

  // Fetch all tickers
  const {
    data: tickersData,
    isLoading: loadingTickers,
    error: tickersError,
  } = useQuery(
    ['tickers', page],
    () => tickerApi.getAllTickers(page, pageSize),
    { keepPreviousData: true }
  );

  // Search companies mutation
  const searchCompaniesMutation = useMutation(
    (query: string) => tickerApi.searchCompanies(query, 10),
    {
      onSuccess: (data) => {
        setSearchResults(data.results);
      },
      onError: (error: any) => {
        setAlternativeTickerError(error.response?.data?.detail || 'Failed to search companies');
      },
    }
  );

  // Fetch company info mutation
  const fetchCompanyInfoMutation = useMutation(
    (companyUid: string) => tickerApi.getCompanyInfo(companyUid),
    {
      onSuccess: (data) => {
        setCompanyInfo(data);
      },
      onError: (error: any) => {
        setAlternativeTickerError(error.response?.data?.detail || 'Failed to fetch company info');
      },
    }
  );

  // Create ticker mutation
  const createTickerMutation = useMutation(
    ({ ticker, yfinanceInfo }: { ticker: string; yfinanceInfo?: TickerInfo }) =>
      tickerApi.createTicker(ticker, yfinanceInfo),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('tickers');
        setReviewDialogOpen(false);
        setFetchedTickerInfo(null);
        setNewTicker('');
        setNewTickerError(null);
      },
      onError: (error: any) => {
        setNewTickerError(error.response?.data?.detail || 'Failed to create ticker');
      },
    }
  );

  // Add alternative ticker mutation
  const addAlternativeTickerMutation = useMutation(
    ({ companyUid, ticker, market }: { companyUid: string; ticker: string; market: string }) =>
      tickerApi.addAlternativeTicker(companyUid, ticker, market),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('tickers');
        setSelectedCompany(null);
        setCompanyInfo(null);
        setAlternativeTicker('');
        setSelectedMarket('');
        setSearchQuery('');
        setSearchResults([]);
        setAlternativeTickerError(null);
      },
      onError: (error: any) => {
        setAlternativeTickerError(error.response?.data?.detail || 'Failed to add alternative ticker');
      },
    }
  );

  // Delete company mutation
  const deleteCompanyMutation = useMutation(
    (companyUid: string) => tickerApi.deleteCompany(companyUid),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('tickers');
        setDeleteDialogOpen(false);
        setCompanyToDelete(null);
        setDeleteError(null);
        setDependencies(null);
      },
      onError: (error: any) => {
        setDeleteError(error.response?.data?.detail || 'Failed to delete company');
      },
    }
  );

  // Handle delete button click
  const handleDeleteClick = async (company: { company_uid: string; company_name?: string | null; main_ticker?: string | null }) => {
    setCompanyToDelete({
      company_uid: company.company_uid,
      company_name: company.company_name ?? null,
      main_ticker: company.main_ticker ?? null
    });
    setDeleteError(null);
    setDependencies(null);
    setCheckingDependencies(true);
    setDeleteDialogOpen(true);

    try {
      const deps = await tickerApi.checkCompanyDependencies(company.company_uid);
      setDependencies(deps.dependencies);
    } catch (error: any) {
      setDeleteError(error.response?.data?.detail || 'Failed to check dependencies');
    } finally {
      setCheckingDependencies(false);
    }
  };

  // Handle confirm delete
  const handleConfirmDelete = () => {
    if (!companyToDelete) return;
    
    if (dependencies && Object.values(dependencies).some(count => count > 0)) {
      setDeleteError('Cannot delete: company has dependencies. Please remove references first.');
      return;
    }

    deleteCompanyMutation.mutate(companyToDelete.company_uid);
  };

  // Fetch ticker info from yfinance
  const handleFetchTickerInfo = async () => {
    if (!newTicker.trim()) {
      setNewTickerError('Please enter a ticker symbol');
      return;
    }

    setFetchingTicker(true);
    setNewTickerError(null);
    setFetchedTickerInfo(null);

    try {
      const info = await tickerApi.fetchTickerInfo(newTicker.trim().toUpperCase());
      setFetchedTickerInfo(info);
      setReviewDialogOpen(true);
    } catch (error: any) {
      setNewTickerError(error.response?.data?.detail || 'Failed to fetch ticker information');
    } finally {
      setFetchingTicker(false);
    }
  };

  // Handle create ticker
  const handleCreateTicker = () => {
    if (!fetchedTickerInfo) return;
    createTickerMutation.mutate({
      ticker: fetchedTickerInfo.ticker,
      yfinanceInfo: fetchedTickerInfo,
    });
  };

  // Handle search companies
  const handleSearchCompanies = () => {
    if (!searchQuery.trim()) {
      setAlternativeTickerError('Please enter a search query');
      return;
    }
    searchCompaniesMutation.mutate(searchQuery.trim());
  };

  // Handle select company
  const handleSelectCompany = async (company: CompanySearchResult) => {
    setSelectedCompany(company);
    setAlternativeTickerError(null);
    fetchCompanyInfoMutation.mutate(company.company_uid);
  };

  // Handle add alternative ticker
  const handleAddAlternativeTicker = () => {
    if (!selectedCompany) {
      setAlternativeTickerError('Please select a company');
      return;
    }
    if (!alternativeTicker.trim()) {
      setAlternativeTickerError('Please enter a ticker symbol');
      return;
    }
    if (!selectedMarket) {
      setAlternativeTickerError('Please select a market');
      return;
    }

    addAlternativeTickerMutation.mutate({
      companyUid: selectedCompany.company_uid,
      ticker: alternativeTicker.trim().toUpperCase(),
      market: selectedMarket,
    });
  };

  const formatMarketCap = (marketCap?: number) => {
    if (!marketCap) return 'N/A';
    if (marketCap >= 1e12) return `$${(marketCap / 1e12).toFixed(2)}T`;
    if (marketCap >= 1e9) return `$${(marketCap / 1e9).toFixed(2)}B`;
    if (marketCap >= 1e6) return `$${(marketCap / 1e6).toFixed(2)}M`;
    return `$${marketCap.toFixed(2)}`;
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2 }}>
        <Logo size="medium" showText={false} clickable={true} />
        <Typography variant="h4" component="h1" sx={{ fontWeight: 700 }}>
          Ticker Manager
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Add New Ticker Section */}
        <Grid item xs={12} md={6}>
          <Card
            sx={{
              height: '100%',
              background: isDarkMode
                ? 'linear-gradient(145deg, #1e293b 0%, #334155 100%)'
                : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
            }}
          >
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
                Add New Ticker
              </Typography>

              {newTickerError && (
                <Alert severity="error" sx={{ mb: 2 }} onClose={() => setNewTickerError(null)}>
                  {newTickerError}
                </Alert>
              )}

              <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                <TextField
                  fullWidth
                  label="Ticker Symbol"
                  value={newTicker}
                  onChange={(e) => setNewTicker(e.target.value.toUpperCase())}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      handleFetchTickerInfo();
                    }
                  }}
                  placeholder="e.g., AAPL"
                  disabled={fetchingTicker}
                />
                <Button
                  variant="contained"
                  onClick={handleFetchTickerInfo}
                  disabled={fetchingTicker || !newTicker.trim()}
                  startIcon={fetchingTicker ? <CircularProgress size={20} /> : <SearchIcon />}
                  sx={{
                    background: isDarkMode
                      ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
                      : 'linear-gradient(135deg, #059669 0%, #047857 100%)',
                    '&:hover': {
                      background: isDarkMode
                        ? 'linear-gradient(135deg, #059669 0%, #047857 100%)'
                        : 'linear-gradient(135deg, #047857 0%, #065f46 100%)',
                    },
                  }}
                >
                  {fetchingTicker ? 'Fetching...' : 'Fetch Info'}
                </Button>
              </Box>

              <Typography variant="body2" color="text.secondary">
                Enter a ticker symbol to fetch information from yfinance. Review the information
                before adding it to the database.
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Add Alternative Ticker Section */}
        <Grid item xs={12} md={6}>
          <Card
            sx={{
              height: '100%',
              background: isDarkMode
                ? 'linear-gradient(145deg, #1e293b 0%, #334155 100%)'
                : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
            }}
          >
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
                Add Alternative Ticker
              </Typography>

              {alternativeTickerError && (
                <Alert
                  severity="error"
                  sx={{ mb: 2 }}
                  onClose={() => setAlternativeTickerError(null)}
                >
                  {alternativeTickerError}
                </Alert>
              )}

              <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                <TextField
                  fullWidth
                  label="Search Company"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      handleSearchCompanies();
                    }
                  }}
                  placeholder="Search by company name or ticker"
                  disabled={searchCompaniesMutation.isLoading}
                />
                <Button
                  variant="outlined"
                  onClick={handleSearchCompanies}
                  disabled={searchCompaniesMutation.isLoading || !searchQuery.trim()}
                  startIcon={
                    searchCompaniesMutation.isLoading ? (
                      <CircularProgress size={20} />
                    ) : (
                      <SearchIcon />
                    )
                  }
                >
                  Search
                </Button>
              </Box>

              {searchResults.length > 0 && (
                <Autocomplete
                  options={searchResults}
                  getOptionLabel={(option) =>
                    `${option.company_name || 'Unknown'} (${option.main_ticker || 'N/A'})`
                  }
                  value={selectedCompany}
                  onChange={(_, newValue) => {
                    if (newValue) {
                      handleSelectCompany(newValue);
                    }
                  }}
                  renderInput={(params) => (
                    <TextField {...params} label="Select Company" margin="normal" />
                  )}
                  sx={{ mb: 2 }}
                />
              )}

              {companyInfo && (
                <Box sx={{ mb: 2, p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Company: {companyInfo.company_name || 'N/A'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Main Ticker: {companyInfo.main_ticker || 'N/A'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Sector: {companyInfo.sector || 'N/A'} | Industry: {companyInfo.industry || 'N/A'}
                  </Typography>
                </Box>
              )}

              {selectedCompany && (
                <>
                  <TextField
                    fullWidth
                    label="Alternative Ticker"
                    value={alternativeTicker}
                    onChange={(e) => setAlternativeTicker(e.target.value.toUpperCase())}
                    placeholder="e.g., AAPL"
                    sx={{ mb: 2 }}
                  />
                  <FormControl fullWidth sx={{ mb: 2 }}>
                    <InputLabel>Market</InputLabel>
                    <Select
                      value={selectedMarket}
                      onChange={(e) => setSelectedMarket(e.target.value)}
                      label="Market"
                    >
                      {VALID_MARKETS.map((market) => (
                        <MenuItem key={market} value={market}>
                          {market}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  <Button
                    variant="contained"
                    fullWidth
                    onClick={handleAddAlternativeTicker}
                    disabled={addAlternativeTickerMutation.isLoading || !alternativeTicker.trim() || !selectedMarket}
                    startIcon={
                      addAlternativeTickerMutation.isLoading ? (
                        <CircularProgress size={20} />
                      ) : (
                        <AddIcon />
                      )
                    }
                    sx={{
                      background: isDarkMode
                        ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
                        : 'linear-gradient(135deg, #059669 0%, #047857 100%)',
                      '&:hover': {
                        background: isDarkMode
                          ? 'linear-gradient(135deg, #059669 0%, #047857 100%)'
                          : 'linear-gradient(135deg, #047857 0%, #065f46 100%)',
                      },
                    }}
                  >
                    {addAlternativeTickerMutation.isLoading ? 'Adding...' : 'Add Alternative Ticker'}
                  </Button>
                </>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* All Tickers Section */}
        <Grid item xs={12}>
          <Card
            sx={{
              background: isDarkMode
                ? 'linear-gradient(145deg, #1e293b 0%, #334155 100%)'
                : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
            }}
          >
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
                All Tickers in Database
              </Typography>

              {tickersError ? (
                <Alert severity="error" sx={{ mb: 2 }}>
                  Failed to load tickers. Please try again.
                </Alert>
              ) : null}

              {loadingTickers ? (
                <Box>
                  {[...Array(5)].map((_, i) => (
                    <Skeleton key={i} variant="rectangular" height={60} sx={{ mb: 1 }} />
                  ))}
                </Box>
              ) : (
                <>
                  <TableContainer component={Paper} sx={{ maxHeight: 600 }}>
                    <Table stickyHeader>
                      <TableHead
                        sx={{
                          '& .MuiTableCell-head': {
                            backgroundColor: isDarkMode
                              ? '#1e293b'
                              : '#ffffff',
                            position: 'sticky',
                            top: 0,
                            zIndex: 10,
                            fontWeight: 600,
                            borderBottom: `2px solid ${isDarkMode ? 'rgba(148, 163, 184, 0.3)' : 'rgba(148, 163, 184, 0.2)'}`,
                          },
                        }}
                      >
                        <TableRow>
                          <TableCell>Company Name</TableCell>
                          <TableCell>Main Ticker</TableCell>
                          <TableCell>All Tickers</TableCell>
                          <TableCell>Sector</TableCell>
                          <TableCell>Industry</TableCell>
                          <TableCell>Country</TableCell>
                          <TableCell>Market Cap</TableCell>
                          <TableCell>Currency</TableCell>
                          <TableCell>Actions</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {tickersData?.companies.map((company) => (
                          <TableRow key={company.company_uid} hover>
                            <TableCell>{company.company_name || 'N/A'}</TableCell>
                            <TableCell>
                              <Chip
                                label={company.main_ticker || 'N/A'}
                                size="small"
                                color="primary"
                                variant="outlined"
                              />
                            </TableCell>
                            <TableCell>
                              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                {company.tickers.map((t, idx) => (
                                  <Chip
                                    key={idx}
                                    label={`${t.ticker}${t.market ? ` (${t.market})` : ''}`}
                                    size="small"
                                    color={t.is_main_ticker ? 'primary' : 'default'}
                                    variant={t.is_main_ticker ? 'filled' : 'outlined'}
                                  />
                                ))}
                              </Box>
                            </TableCell>
                            <TableCell>{company.sector || 'N/A'}</TableCell>
                            <TableCell>{company.industry || 'N/A'}</TableCell>
                            <TableCell>{company.country || 'N/A'}</TableCell>
                            <TableCell>{formatMarketCap(company.market_cap)}</TableCell>
                            <TableCell>{company.currency || 'N/A'}</TableCell>
                            <TableCell>
                              <Button
                                variant="text"
                                color="error"
                                size="small"
                                onClick={() => handleDeleteClick({
                                  company_uid: company.company_uid,
                                  company_name: company.company_name ?? null,
                                  main_ticker: company.main_ticker ?? null
                                })}
                                sx={{
                                  minWidth: 'auto',
                                  padding: '4px',
                                  '&:hover': {
                                    backgroundColor: 'error.light',
                                    color: 'error.contrastText',
                                  },
                                }}
                              >
                                <DeleteIcon fontSize="small" />
                              </Button>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>

                  {tickersData && tickersData.total > 0 && (
                    <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
                      <Pagination
                        count={Math.ceil(tickersData.total / pageSize)}
                        page={page}
                        onChange={(_, newPage) => setPage(newPage)}
                        color="primary"
                      />
                    </Box>
                  )}

                  {tickersData?.companies.length === 0 && (
                    <Box sx={{ textAlign: 'center', py: 4 }}>
                      <Typography variant="body1" color="text.secondary">
                        No tickers found in the database.
                      </Typography>
                    </Box>
                  )}
                </>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Review Dialog for New Ticker */}
      <Dialog
        open={reviewDialogOpen}
        onClose={() => setReviewDialogOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            background: isDarkMode
              ? 'linear-gradient(145deg, #1e293b 0%, #334155 100%)'
              : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
          },
        }}
      >
        <DialogTitle>Review Ticker Information</DialogTitle>
        <DialogContent>
          {fetchedTickerInfo && (
            <Box>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Ticker
                  </Typography>
                  <Typography variant="body1">{fetchedTickerInfo.ticker}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Company Name
                  </Typography>
                  <Typography variant="body1">
                    {fetchedTickerInfo.company_name || 'N/A'}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Sector
                  </Typography>
                  <Typography variant="body1">{fetchedTickerInfo.sector || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Industry
                  </Typography>
                  <Typography variant="body1">{fetchedTickerInfo.industry || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Exchange
                  </Typography>
                  <Typography variant="body1">{fetchedTickerInfo.exchange || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Country
                  </Typography>
                  <Typography variant="body1">{fetchedTickerInfo.country || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Market Cap
                  </Typography>
                  <Typography variant="body1">
                    {formatMarketCap(fetchedTickerInfo.market_cap)}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Currency
                  </Typography>
                  <Typography variant="body1">{fetchedTickerInfo.currency || 'N/A'}</Typography>
                </Grid>
                {fetchedTickerInfo.description && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Description
                    </Typography>
                    <Typography variant="body2" sx={{ maxHeight: 150, overflow: 'auto' }}>
                      {fetchedTickerInfo.description}
                    </Typography>
                  </Grid>
                )}
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setReviewDialogOpen(false)} startIcon={<CancelIcon />}>
            Cancel
          </Button>
          <Button
            onClick={handleCreateTicker}
            variant="contained"
            disabled={createTickerMutation.isLoading}
            startIcon={
              createTickerMutation.isLoading ? (
                <CircularProgress size={20} />
              ) : (
                <CheckCircleIcon />
              )
            }
            sx={{
              background: isDarkMode
                ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
                : 'linear-gradient(135deg, #059669 0%, #047857 100%)',
              '&:hover': {
                background: isDarkMode
                  ? 'linear-gradient(135deg, #059669 0%, #047857 100%)'
                  : 'linear-gradient(135deg, #047857 0%, #065f46 100%)',
              },
            }}
          >
            {createTickerMutation.isLoading ? 'Creating...' : 'Accept & Add'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => {
          setDeleteDialogOpen(false);
          setCompanyToDelete(null);
          setDeleteError(null);
          setDependencies(null);
        }}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            background: isDarkMode
              ? 'linear-gradient(145deg, #1e293b 0%, #334155 100%)'
              : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
          },
        }}
      >
        <DialogTitle>Delete Company</DialogTitle>
        <DialogContent>
          {checkingDependencies ? (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, py: 2 }}>
              <CircularProgress size={24} />
              <Typography>Checking dependencies...</Typography>
            </Box>
          ) : (
            <>
              <Typography variant="body1" sx={{ mb: 2 }}>
                Are you sure you want to delete{' '}
                <strong>{companyToDelete?.company_name || companyToDelete?.main_ticker || 'this company'}</strong>?
              </Typography>
              
              {companyToDelete?.main_ticker && (
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Main Ticker: <strong>{companyToDelete.main_ticker}</strong>
                </Typography>
              )}

              {deleteError && (
                <Alert severity="error" sx={{ mb: 2 }} onClose={() => setDeleteError(null)}>
                  {deleteError}
                </Alert>
              )}

              {dependencies && Object.values(dependencies).some(count => count > 0) && (
                <Alert severity="warning" sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Cannot delete: This company is referenced in:
                  </Typography>
                  <Box component="ul" sx={{ margin: 0, paddingLeft: 2 }}>
                    {dependencies.universe_companies > 0 && (
                      <li>{dependencies.universe_companies} universe(s)</li>
                    )}
                    {dependencies.signal_raw > 0 && (
                      <li>{dependencies.signal_raw} signal(s)</li>
                    )}
                    {dependencies.scores_combined > 0 && (
                      <li>{dependencies.scores_combined} score(s)</li>
                    )}
                    {dependencies.portfolio_positions > 0 && (
                      <li>{dependencies.portfolio_positions} portfolio position(s)</li>
                    )}
                  </Box>
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    Please remove these references first before deleting.
                  </Typography>
                </Alert>
              )}

              {dependencies && Object.values(dependencies).every(count => count === 0) && (
                <Alert severity="info" sx={{ mb: 2 }}>
                  This will permanently delete the company and all its tickers from the database.
                  This action cannot be undone.
                </Alert>
              )}
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setDeleteDialogOpen(false);
              setCompanyToDelete(null);
              setDeleteError(null);
              setDependencies(null);
            }}
            startIcon={<CancelIcon />}
          >
            Cancel
          </Button>
          <Button
            onClick={handleConfirmDelete}
            variant="contained"
            color="error"
            disabled={
              checkingDependencies ||
              deleteCompanyMutation.isLoading ||
              (dependencies !== null && Object.values(dependencies).some(count => count > 0))
            }
            startIcon={
              deleteCompanyMutation.isLoading ? (
                <CircularProgress size={20} />
              ) : (
                <DeleteIcon />
              )
            }
            sx={{
              background: isDarkMode
                ? 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)'
                : 'linear-gradient(135deg, #dc2626 0%, #b91c1c 100%)',
              '&:hover': {
                background: isDarkMode
                  ? 'linear-gradient(135deg, #dc2626 0%, #b91c1c 100%)'
                  : 'linear-gradient(135deg, #b91c1c 0%, #991b1b 100%)',
              },
            }}
          >
            {deleteCompanyMutation.isLoading ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TickerManager;

