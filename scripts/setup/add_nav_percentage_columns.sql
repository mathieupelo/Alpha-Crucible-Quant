-- Migration script to add return_pct and benchmark_return_pct columns to backtest_nav table
-- Run this script if you get an error about missing columns

-- Add return_pct column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'backtest_nav' 
        AND column_name = 'return_pct'
    ) THEN
        ALTER TABLE backtest_nav ADD COLUMN return_pct FLOAT DEFAULT NULL;
        RAISE NOTICE 'Added return_pct column to backtest_nav table';
    ELSE
        RAISE NOTICE 'return_pct column already exists';
    END IF;
END $$;

-- Add benchmark_return_pct column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'backtest_nav' 
        AND column_name = 'benchmark_return_pct'
    ) THEN
        ALTER TABLE backtest_nav ADD COLUMN benchmark_return_pct FLOAT DEFAULT NULL;
        RAISE NOTICE 'Added benchmark_return_pct column to backtest_nav table';
    ELSE
        RAISE NOTICE 'benchmark_return_pct column already exists';
    END IF;
END $$;

-- Optional: Migrate existing data to calculate return_pct from nav values
-- This calculates return_pct for existing records based on their first NAV value
DO $$
DECLARE
    run_rec RECORD;
    nav_rec RECORD;
    baseline_nav FLOAT;
    baseline_benchmark_nav FLOAT;
    return_pct_val FLOAT;
    benchmark_return_pct_val FLOAT;
BEGIN
    -- For each unique run_id, calculate return_pct
    FOR run_rec IN SELECT DISTINCT run_id FROM backtest_nav LOOP
        -- Get baseline NAV (first NAV value for this run_id)
        SELECT nav INTO baseline_nav 
        FROM backtest_nav 
        WHERE run_id = run_rec.run_id 
        ORDER BY date ASC 
        LIMIT 1;
        
        -- Get baseline benchmark NAV if available
        SELECT benchmark_nav INTO baseline_benchmark_nav 
        FROM backtest_nav 
        WHERE run_id = run_rec.run_id 
        AND benchmark_nav IS NOT NULL 
        AND benchmark_nav > 0
        ORDER BY date ASC 
        LIMIT 1;
        
        -- Use baseline_nav as fallback for benchmark if not available
        IF baseline_benchmark_nav IS NULL OR baseline_benchmark_nav <= 0 THEN
            baseline_benchmark_nav := baseline_nav;
        END IF;
        
        -- Update all records for this run_id
        FOR nav_rec IN 
            SELECT date, nav, benchmark_nav 
            FROM backtest_nav 
            WHERE run_id = run_rec.run_id
        LOOP
            -- Calculate return_pct: (nav - baseline) / baseline
            IF baseline_nav > 0 THEN
                return_pct_val := (nav_rec.nav - baseline_nav) / baseline_nav;
            ELSE
                return_pct_val := 0.0;
            END IF;
            
            -- Calculate benchmark_return_pct if benchmark_nav exists
            benchmark_return_pct_val := NULL;
            IF nav_rec.benchmark_nav IS NOT NULL AND nav_rec.benchmark_nav > 0 AND baseline_benchmark_nav > 0 THEN
                benchmark_return_pct_val := (nav_rec.benchmark_nav - baseline_benchmark_nav) / baseline_benchmark_nav;
            END IF;
            
            -- Update the record
            UPDATE backtest_nav 
            SET return_pct = return_pct_val,
                benchmark_return_pct = benchmark_return_pct_val
            WHERE run_id = run_rec.run_id AND date = nav_rec.date;
        END LOOP;
    END LOOP;
    
    RAISE NOTICE 'Migrated existing NAV data to percentage format';
END $$;

