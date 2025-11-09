/**
 * Ticker Bar Component
 * Displays live stock prices in a static bar that flips to show new tickers
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

const TICKERS_PER_VIEW = 4; // Number of tickers to show at once
const FLIP_INTERVAL = 5000; // Flip every 5 seconds

const TickerBar: React.FC = () => {
  const { isDarkMode } = useTheme();
  const [tickerItems, setTickerItems] = useState<TickerItem[]>([]);
  const [isFlipping, setIsFlipping] = useState(false);
  const [displayGroupIndex, setDisplayGroupIndex] = useState(0);
  const [flipKey, setFlipKey] = useState(0); // Stable key that only changes after flip completes

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

  // Fetch companies for both universes
  const { data: movieCoreCompaniesData } = useQuery(
    ['universe-companies', movieCoreUniverse?.id],
    () => universeApi.getUniverseCompanies(movieCoreUniverse!.id),
    {
      enabled: !!movieCoreUniverse?.id,
      staleTime: 5 * 60 * 1000,
      refetchOnWindowFocus: false,
    }
  );

  const { data: gameCoreCompaniesData } = useQuery(
    ['universe-companies', gameCoreUniverse?.id],
    () => universeApi.getUniverseCompanies(gameCoreUniverse!.id),
    {
      enabled: !!gameCoreUniverse?.id,
      staleTime: 5 * 60 * 1000,
      refetchOnWindowFocus: false,
    }
  );

  // Combine all tickers (using main_ticker from companies)
  const allTickers = useMemo(() => {
    const tickers: Array<{ symbol: string; universe: string }> = [];
    
    if (movieCoreCompaniesData) {
      movieCoreCompaniesData.companies.forEach(c => {
        if (c.main_ticker) {
          tickers.push({ symbol: c.main_ticker, universe: 'MovieCore-8' });
        }
      });
    }
    
    if (gameCoreCompaniesData) {
      gameCoreCompaniesData.companies.forEach(c => {
        if (c.main_ticker) {
          tickers.push({ symbol: c.main_ticker, universe: 'GameCore-12' });
        }
      });
    }
    
    return tickers;
  }, [movieCoreCompaniesData, gameCoreCompaniesData]);

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

  // Split tickers into groups for flipping
  const tickerGroups = useMemo(() => {
    if (!tickerItems.length) return [];
    const groups: TickerItem[][] = [];
    for (let i = 0; i < tickerItems.length; i += TICKERS_PER_VIEW) {
      groups.push(tickerItems.slice(i, i + TICKERS_PER_VIEW));
    }
    // If we have multiple groups, make sure we loop back
    return groups.length > 0 ? groups : [];
  }, [tickerItems]);

  // Get groups to display (front and back)
  const frontGroup = useMemo(() => {
    if (!tickerGroups.length) return [];
    return tickerGroups[displayGroupIndex % tickerGroups.length];
  }, [tickerGroups, displayGroupIndex]);

  const backGroup = useMemo(() => {
    if (!tickerGroups.length) return [];
    return tickerGroups[(displayGroupIndex + 1) % tickerGroups.length];
  }, [tickerGroups, displayGroupIndex]);

  // Auto-flip to next group after interval
  useEffect(() => {
    if (tickerGroups.length <= 1) return; // No need to flip if only one group

    const interval = setInterval(() => {
      setIsFlipping(true);
      // Update the display index after flip completes
      setTimeout(() => {
        setDisplayGroupIndex((prev) => (prev + 1) % tickerGroups.length);
        setFlipKey((prev) => prev + 1); // Update key after animation completes
        setIsFlipping(false);
      }, 1200); // After full flip duration
    }, FLIP_INTERVAL);

    return () => clearInterval(interval);
  }, [tickerGroups.length]);

  if (!tickerItems.length || !frontGroup.length) {
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
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        perspective: '1000px', // Enable 3D perspective for flip effect
      }}
    >
      {/* Static container with flip animation */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100%',
          width: '100%',
          position: 'relative',
        }}
      >
        <Box
          sx={{
            position: 'relative',
            width: '100%',
            height: '100%',
            transformStyle: 'preserve-3d',
          }}
        >
          {/* Front side - current group */}
          <motion.div
            key={`front-${flipKey}`}
            animate={{
              rotateX: isFlipping ? 180 : 0,
            }}
            transition={{
              duration: 1.2,
              ease: [0.43, 0.13, 0.23, 0.96],
            }}
            style={{
              position: 'absolute',
              width: '100%',
              height: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '48px',
              backfaceVisibility: 'hidden',
              WebkitBackfaceVisibility: 'hidden',
              transformStyle: 'preserve-3d',
            }}
          >
            {frontGroup.map((item) => {
              const isPositive = (item.dailyChangePercent ?? 0) >= 0;
              const changeColor = isPositive
                ? (isDarkMode ? '#10b981' : '#059669')
                : (isDarkMode ? '#ef4444' : '#dc2626');
              
              return (
                <motion.div
                  key={`${item.symbol}-${item.universe}`}
                  initial={false}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
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

          {/* Back side - next group (initially rotated 180 degrees) */}
          <motion.div
            key={`back-${flipKey}`}
            initial={{ rotateX: 180 }}
            animate={{
              rotateX: isFlipping ? 0 : 180,
            }}
            transition={{
              duration: 1.2,
              ease: [0.43, 0.13, 0.23, 0.96],
            }}
            style={{
              position: 'absolute',
              width: '100%',
              height: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '48px',
              backfaceVisibility: 'hidden',
              WebkitBackfaceVisibility: 'hidden',
              transformStyle: 'preserve-3d',
            }}
          >
            {backGroup.map((item) => {
              const isPositive = (item.dailyChangePercent ?? 0) >= 0;
              const changeColor = isPositive
                ? (isDarkMode ? '#10b981' : '#059669')
                : (isDarkMode ? '#ef4444' : '#dc2626');
              
              return (
                <div
                  key={`${item.symbol}-${item.universe}`}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
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
                </div>
              );
            })}
          </motion.div>
        </Box>
      </Box>
    </Box>
  );
};

export default TickerBar;

