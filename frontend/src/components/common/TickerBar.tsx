/**
 * Ticker Bar Component
 * Displays live stock prices in a scrolling ticker bar with fade animations
 */

import React, { useState, useEffect, useMemo } from 'react';
import { Box, Typography } from '@mui/material';
import { motion } from 'framer-motion';
import { useQuery } from 'react-query';
import { useTheme } from '@/contexts/ThemeContext';
import { universeApi, marketApi } from '@/services/api';

interface TickerItem {
  symbol: string;
  price: number | null;
  dailyChange: number | null;
  dailyChangePercent: number | null;
  universe: string;
}

const TickerBar: React.FC = () => {
  const { isDarkMode } = useTheme();
  const [tickerItems, setTickerItems] = useState<TickerItem[]>([]);

  // Fetch universes
  const { data: universesData } = useQuery(
    'universes-for-ticker-bar',
    () => universeApi.getUniverses(),
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
      refetchOnWindowFocus: false,
    }
  );

  // Find MovieCore-8 and GameCore-12 universes
  const movieCoreUniverse = useMemo(() => {
    if (!universesData) return null;
    return universesData.universes.find(u => 
      u.name.includes('MovieCore-8') || u.name.includes('MC-8')
    );
  }, [universesData]);

  const gameCoreUniverse = useMemo(() => {
    if (!universesData) return null;
    return universesData.universes.find(u => 
      u.name.includes('GameCore-12') || u.name.includes('GC-12')
    );
  }, [universesData]);

  // Fetch tickers for both universes
  const { data: movieCoreTickersData } = useQuery(
    ['universe-tickers', movieCoreUniverse?.id],
    () => universeApi.getUniverseTickers(movieCoreUniverse!.id),
    {
      enabled: !!movieCoreUniverse?.id,
      staleTime: 5 * 60 * 1000,
      refetchOnWindowFocus: false,
    }
  );

  const { data: gameCoreTickersData } = useQuery(
    ['universe-tickers', gameCoreUniverse?.id],
    () => universeApi.getUniverseTickers(gameCoreUniverse!.id),
    {
      enabled: !!gameCoreUniverse?.id,
      staleTime: 5 * 60 * 1000,
      refetchOnWindowFocus: false,
    }
  );

  // Combine all tickers
  const allTickers = useMemo(() => {
    const tickers: Array<{ symbol: string; universe: string }> = [];
    
    if (movieCoreTickersData) {
      movieCoreTickersData.tickers.forEach(t => {
        tickers.push({ symbol: t.ticker, universe: 'MovieCore-8' });
      });
    }
    
    if (gameCoreTickersData) {
      gameCoreTickersData.tickers.forEach(t => {
        tickers.push({ symbol: t.ticker, universe: 'GameCore-12' });
      });
    }
    
    return tickers;
  }, [movieCoreTickersData, gameCoreTickersData]);

  // Fetch live prices for all tickers
  const { data: pricesData } = useQuery(
    ['live-prices', allTickers.map(t => t.symbol).join(',')],
    () => marketApi.getLivePricesBatch(allTickers.map(t => t.symbol)),
    {
      enabled: allTickers.length > 0,
      refetchInterval: 30000, // Refresh every 30 seconds
      staleTime: 15000, // Consider stale after 15 seconds
      refetchOnWindowFocus: true,
    }
  );

  // Combine ticker data with prices
  useEffect(() => {
    if (!pricesData || !allTickers.length) return;

    const items: TickerItem[] = [];
    
    // Add MovieCore-8 tickers
    allTickers
      .filter(t => t.universe === 'MovieCore-8')
      .forEach(ticker => {
        const priceData = pricesData.results.find(r => r.symbol === ticker.symbol);
        if (priceData) {
          items.push({
            symbol: ticker.symbol,
            price: priceData.price,
            dailyChange: priceData.daily_change,
            dailyChangePercent: priceData.daily_change_percent,
            universe: ticker.universe,
          });
        }
      });
    
    // Add GameCore-12 tickers (no separator)
    allTickers
      .filter(t => t.universe === 'GameCore-12')
      .forEach(ticker => {
        const priceData = pricesData.results.find(r => r.symbol === ticker.symbol);
        if (priceData) {
          items.push({
            symbol: ticker.symbol,
            price: priceData.price,
            dailyChange: priceData.daily_change,
            dailyChangePercent: priceData.daily_change_percent,
            universe: ticker.universe,
          });
        }
      });

    setTickerItems(items);
  }, [pricesData, allTickers]);

  // Duplicate items multiple times for seamless infinite loop
  const duplicatedItems = useMemo(() => {
    if (!tickerItems.length) return [];
    // Create 3 copies to ensure seamless scrolling
    return [...tickerItems, ...tickerItems, ...tickerItems];
  }, [tickerItems]);
  
  // Calculate approximate width per item (symbol + price + change)
  const itemWidth = 300; // Width including gaps (ticker + info spacing + bigger gap between tickers)
  const totalWidth = tickerItems.length > 0 ? tickerItems.length * itemWidth : 0;

  if (!tickerItems.length || totalWidth === 0) {
    return null; // Don't show anything if no data
  }

  return (
    <Box
      sx={{
        position: 'relative',
        height: 40,
        overflow: 'hidden',
        background: 'transparent',
        zIndex: 1000,
      }}
    >
      {/* Gradient masks for stronger fade effect */}
      <Box
        sx={{
          position: 'absolute',
          left: 0,
          top: 0,
          bottom: 0,
          width: 120,
          background: isDarkMode
            ? 'linear-gradient(to right, rgba(30, 41, 59, 1) 0%, rgba(30, 41, 59, 0.95) 30%, rgba(30, 41, 59, 0.8) 60%, rgba(30, 41, 59, 0.3) 90%, rgba(30, 41, 59, 0) 100%)'
            : 'linear-gradient(to right, rgba(255, 255, 255, 1) 0%, rgba(255, 255, 255, 0.95) 30%, rgba(255, 255, 255, 0.8) 60%, rgba(255, 255, 255, 0.3) 90%, rgba(255, 255, 255, 0) 100%)',
          zIndex: 2,
          pointerEvents: 'none',
        }}
      />
      <Box
        sx={{
          position: 'absolute',
          right: 0,
          top: 0,
          bottom: 0,
          width: 120,
          background: isDarkMode
            ? 'linear-gradient(to left, rgba(30, 41, 59, 1) 0%, rgba(30, 41, 59, 0.95) 30%, rgba(30, 41, 59, 0.8) 60%, rgba(30, 41, 59, 0.3) 90%, rgba(30, 41, 59, 0) 100%)'
            : 'linear-gradient(to left, rgba(255, 255, 255, 1) 0%, rgba(255, 255, 255, 0.95) 30%, rgba(255, 255, 255, 0.8) 60%, rgba(255, 255, 255, 0.3) 90%, rgba(255, 255, 255, 0) 100%)',
          zIndex: 2,
          pointerEvents: 'none',
        }}
      />

      {/* Scrolling container */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          height: '100%',
          whiteSpace: 'nowrap',
          overflow: 'hidden',
        }}
      >
        <motion.div
          animate={{
            x: [0, -totalWidth], // Move by one set of items to create seamless loop
          }}
          transition={{
            duration: 180, // Slower scrolling (180s per loop)
            repeat: Infinity,
            ease: 'linear',
          }}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '48px', // Bigger spacing between tickers
            paddingLeft: '120px', // Start after fade area
            willChange: 'transform',
          }}
        >
          {duplicatedItems.map((item, index) => {
              const isPositive = (item.dailyChangePercent ?? 0) >= 0;
              const changeColor = isPositive
                ? (isDarkMode ? '#10b981' : '#059669')
                : (isDarkMode ? '#ef4444' : '#dc2626');

              // Create unique key that includes the item symbol and its position in the loop
              // This helps with animation but we'll use index for now to maintain order
              const uniqueKey = `${item.symbol}-${item.universe}-${index}`;
              
              return (
                <motion.div
                  key={uniqueKey}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.8, ease: 'easeOut' }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px', // Less space between ticker symbol and its info
                    minWidth: '140px',
                  }}
                >
                  <Typography
                    variant="body2"
                    sx={{
                      fontWeight: 700,
                      fontSize: '0.875rem',
                      color: isDarkMode ? '#cbd5e1' : '#334155',
                      minWidth: '50px',
                    }}
                  >
                    {item.symbol}
                  </Typography>
                  
                  {item.price !== null ? (
                    <>
                      <Typography
                        variant="body2"
                        sx={{
                          fontWeight: 600,
                          fontSize: '0.875rem',
                          color: isDarkMode ? '#f8fafc' : '#0f172a',
                          minWidth: '60px',
                        }}
                      >
                        ${item.price.toFixed(2)}
                      </Typography>
                      <Typography
                        variant="body2"
                        sx={{
                          fontWeight: 600,
                          fontSize: '0.875rem',
                          color: changeColor,
                          minWidth: '70px',
                        }}
                      >
                        {isPositive ? '+' : ''}
                        {item.dailyChangePercent?.toFixed(2)}%
                      </Typography>
                    </>
                  ) : (
                    <Typography
                      variant="body2"
                      sx={{
                        fontWeight: 400,
                        fontSize: '0.75rem',
                        color: 'text.secondary',
                        fontStyle: 'italic',
                      }}
                    >
                      Loading...
                    </Typography>
                  )}
                </motion.div>
              );
            })}
        </motion.div>
      </Box>
    </Box>
  );
};

export default TickerBar;

