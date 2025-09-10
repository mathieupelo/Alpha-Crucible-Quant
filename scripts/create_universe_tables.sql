-- Create universes table
CREATE TABLE IF NOT EXISTS universes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create universe_tickers table
CREATE TABLE IF NOT EXISTS universe_tickers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    universe_id INT NOT NULL,
    ticker VARCHAR(50) NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (universe_id) REFERENCES universes(id) ON DELETE CASCADE,
    UNIQUE KEY unique_universe_ticker (universe_id, ticker)
);

-- Create indexes for better performance
CREATE INDEX idx_universe_tickers_universe_id ON universe_tickers(universe_id);
CREATE INDEX idx_universe_tickers_ticker ON universe_tickers(ticker);
