/**
 * Main App Component for Alpha Crucible Quant Dashboard
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Box } from '@mui/material';

import Home from '@/pages/Home';
import BacktestManager from '@/pages/BacktestManager';
import UniverseManager from '@/pages/UniverseManager';
import UniverseDetail from '@/pages/UniverseDetail';
import RunBacktest from '@/pages/RunBacktest';
import NewsDeepDive from '@/pages/NewsDeepDive';
import TickerManager from '@/pages/TickerManager';
import Layout from '@/components/common/Layout';
import { AppProviders } from '@/providers/AppProviders';

const App: React.FC = () => {
  return (
    <AppProviders>
      <Router>
        <Box sx={{ minHeight: '100vh' }}>
          <Layout>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/backtest" element={<BacktestManager />} />
              <Route path="/run-backtest" element={<RunBacktest />} />
              <Route path="/universes" element={<UniverseManager />} />
              <Route path="/universes/:id" element={<UniverseDetail />} />
              <Route path="/news-deep-dive" element={<NewsDeepDive />} />
              <Route path="/tickers" element={<TickerManager />} />
            </Routes>
          </Layout>
        </Box>
      </Router>
    </AppProviders>
  );
};

export default App;
