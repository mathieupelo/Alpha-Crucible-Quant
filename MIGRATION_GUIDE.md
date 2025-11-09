# Varrock Schema Migration Guide

## Overview

This guide explains how to migrate from the old ticker-based system to the new company-based Varrock schema.

## Migration Steps

### 1. Run Schema Migration

Add `company_uid` columns to existing tables:

```bash
python scripts/migrate_add_company_uid_columns.py
```

This script:
- Adds `company_uid VARCHAR(36)` to `signal_raw`, `scores_combined`, and `portfolio_positions`
- Creates foreign key constraints to `varrock.companies`
- Creates indexes on `company_uid` columns

### 2. Run Data Migration

Populate `company_uid` values from existing tickers:

```bash
python scripts/migrate_to_company_uid.py
```

This script:
- Resolves all tickers in existing records to `company_uid` via `varrock.tickers`
- Updates all records with their corresponding `company_uid`
- Logs any tickers that don't exist in Varrock schema

### 3. Validate Migration

Verify that all records have been migrated:

```bash
python scripts/validate_company_migration.py
```

This script checks:
- All records have `company_uid` populated
- All `company_uid` values reference valid companies
- Reports any missing or invalid records

## What Changed

### Database Schema

**New Columns:**
- `signal_raw.company_uid` - Links signals to companies
- `scores_combined.company_uid` - Links scores to companies
- `portfolio_positions.company_uid` - Links positions to companies

**New Table:**
- `universe_companies` - Links universes to companies (replaces `universe_tickers`)

### API Endpoints

**Removed:**
- `GET /api/universes/{id}/tickers`
- `PUT /api/universes/{id}/tickers`
- `POST /api/universes/{id}/tickers`
- `DELETE /api/universes/{id}/tickers/{ticker}`

**Added:**
- `GET /api/universes/{id}/companies` - Get companies with info
- `PUT /api/universes/{id}/companies` - Update companies (accepts tickers)
- `POST /api/universes/{id}/companies` - Add company (accepts ticker)
- `DELETE /api/universes/{id}/companies/{company_uid}` - Remove company

### Response Format

All responses now include company information:
- `company_uid` - Unique company identifier
- `company_name` - Company name from Varrock schema
- `main_ticker` - Primary ticker symbol
- `all_tickers` - Array of all tickers for the company

### Frontend Changes

- UniverseDetail: Shows companies with expandable ticker list
- UniverseManager: Shows company count instead of ticker count
- PortfolioDetail: Uses main tickers from companies
- All components use company-based API methods

## Backward Compatibility

The system maintains backward compatibility:

1. **Ticker columns preserved**: All `ticker` columns remain in tables for reference
2. **Automatic resolution**: Ticker inputs are automatically resolved to `company_uid`
3. **Fallback queries**: If `company_uid` is missing, queries fall back to ticker-based filtering

## Troubleshooting

### Missing company_uid values

If validation shows missing `company_uid` values:

1. Check if tickers exist in `varrock.tickers`:
   ```sql
   SELECT ticker FROM varrock.tickers WHERE ticker = 'YOUR_TICKER';
   ```

2. If ticker doesn't exist, add it to a universe first (it will be created automatically)

3. Re-run migration:
   ```bash
   python scripts/migrate_to_company_uid.py
   ```

### Invalid company_uid references

If validation shows invalid `company_uid` references:

1. Check for orphaned records:
   ```sql
   SELECT * FROM signal_raw sr
   WHERE sr.company_uid IS NOT NULL
   AND NOT EXISTS (
       SELECT 1 FROM varrock.companies c 
       WHERE c.company_uid = sr.company_uid
   );
   ```

2. These should be cleaned up or the `company_uid` set to NULL

## Testing

Run the integration test:

```bash
python scripts/test_company_integration.py
```

This verifies:
- All imports work correctly
- DatabaseManager has required methods
- Models have `company_uid` fields

## Rollback

If you need to rollback:

1. The `ticker` columns are still present and functional
2. Old endpoints can be restored from git history
3. Data migration is non-destructive (only adds `company_uid`, doesn't remove `ticker`)

However, note that:
- New records will automatically populate `company_uid`
- Frontend components expect company-based responses
- Full rollback would require reverting all code changes

