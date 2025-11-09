# Varrock Schema Implementation

## Overview

The Varrock schema has been implemented in the `alpha-crucible-cloud-db` Supabase PostgreSQL database to store company and ticker information with proper relationships and validation.

## Schema Structure

### Tables Created

1. **varrock.companies** - Main company table
   - `company_uid` (VARCHAR(36) PRIMARY KEY) - UUID identifier
   - `created_at`, `updated_at` - Timestamps

2. **varrock.company_info** - Company details (one-to-one with companies)
   - `company_info_uid` (VARCHAR(36) PRIMARY KEY)
   - `company_uid` (VARCHAR(36) UNIQUE, FK to companies)
   - All yfinance fields (name, country, sector, industry, etc.)
   - `data_source`, `last_updated` - Metadata

3. **varrock.tickers** - Ticker symbols (one-to-many with companies)
   - `ticker_uid` (VARCHAR(36) PRIMARY KEY)
   - `company_uid` (VARCHAR(36), FK to companies)
   - `ticker`, `market`, `exchange`, `currency`
   - `is_in_yfinance` (BOOLEAN DEFAULT FALSE) - Validation status
   - `is_main_ticker` (BOOLEAN DEFAULT FALSE) - Main ticker flag
   - `is_active`, `ticker_type`, `yfinance_symbol`
   - `first_seen_date`, `last_verified_date` - Tracking dates

4. **varrock.company_info_history** - Versioned company info
   - Same fields as company_info plus `version_number`
   - Tracks historical changes

5. **universe_companies** - Links universes to companies (replaces universe_tickers)
   - `id` (SERIAL PRIMARY KEY)
   - `universe_id` (INT, FK to universes)
   - `company_uid` (VARCHAR(36), FK to varrock.companies)
   - `added_at` - Timestamp

## Key Features

### Main Ticker Logic
- Priority: NYSE > NASDAQ > First created (by created_at)
- Enforced via partial unique index
- Automatically determined when tickers are added

### Ticker Validation
- `is_in_yfinance` field tracks validation status
- Defaults to FALSE, set to TRUE when validated
- `last_verified_date` tracks when validation occurred
- Validation happens automatically when tickers are created

### Data Relationships
- One company can have multiple tickers
- One company has one company_info record
- Company info changes are tracked in company_info_history
- Universes link to companies (not directly to tickers)

## Setup Instructions

### 1. Create Varrock Schema

```bash
cd Alpha-Crucible-Quant
python scripts/setup_varrock_schema.py
```

This will:
- Create the `varrock` schema
- Create all 4 tables (companies, company_info, tickers, company_info_history)
- Create indexes and constraints
- Set up update triggers

### 2. Create universe_companies Table

The `universe_companies` table is created automatically by the migration script, or you can run:

```sql
CREATE TABLE IF NOT EXISTS universe_companies (
    id SERIAL PRIMARY KEY,
    universe_id INT NOT NULL,
    company_uid VARCHAR(36) NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_universe_company UNIQUE (universe_id, company_uid),
    FOREIGN KEY (universe_id) REFERENCES universes(id) ON DELETE CASCADE,
    FOREIGN KEY (company_uid) REFERENCES varrock.companies(company_uid) ON DELETE CASCADE
);
```

### 3. Migrate Existing Data

```bash
python scripts/migrate_to_varrock.py
```

This will:
- Create the `universe_companies` table
- For each ticker in `universe_tickers`:
  - Validate ticker with yfinance
  - Create company, company_info, and ticker records
  - Determine main ticker (NYSE/NASDAQ priority)
  - Create `universe_companies` entry

## Testing

### Run Test Script

```bash
python scripts/test_varrock_schema.py
```

This will test:
- Schema existence
- Company creation and retrieval
- Ticker validation with yfinance
- Ticker storage and main ticker determination
- Company info storage
- Universe companies table existence

### Manual Testing

1. **Test Company Creation:**
```python
from database import DatabaseManager
db = DatabaseManager()
db.connect()
company_uid = db.create_company()
print(f"Created company: {company_uid}")
```

2. **Test Ticker Validation:**
```python
is_valid = db.validate_ticker_with_yfinance("AAPL")
print(f"AAPL is valid: {is_valid}")
```

3. **Test Main Ticker Determination:**
```python
main_ticker_uid = db.determine_main_ticker(company_uid)
main_ticker = db.get_main_ticker(company_uid)
print(f"Main ticker: {main_ticker.ticker}")
```

## API Endpoints

### New Endpoints (Varrock Schema)

- `GET /api/universes/{universe_id}/companies` - Get all companies for a universe
- `PUT /api/universes/{universe_id}/companies` - Update companies (accepts tickers, auto-resolves)
- `POST /api/universes/{universe_id}/companies?ticker=XXX` - Add company (accepts ticker)
- `DELETE /api/universes/{universe_id}/companies/{company_uid}` - Remove company

### Legacy Endpoints (Still Available)

- `GET /api/universes/{universe_id}/tickers` - Get tickers (backward compatibility)
- `PUT /api/universes/{universe_id}/tickers` - Update tickers
- `POST /api/universes/{universe_id}/tickers?ticker=XXX` - Add ticker
- `DELETE /api/universes/{universe_id}/tickers/{ticker}` - Remove ticker

## Database Manager Methods

### Company Operations
- `create_company(company_uid=None)` - Create new company
- `get_company(company_uid)` - Get company by UID
- `get_companies_by_ticker(ticker)` - Find companies by ticker

### Company Info Operations
- `store_company_info(company_info)` - Store/update company info
- `get_company_info(company_uid)` - Get current company info
- `store_company_info_history(company_info)` - Store historical version

### Ticker Operations
- `store_ticker(ticker)` - Insert/update ticker (auto-validates)
- `get_tickers_by_company(company_uid)` - Get all tickers for company
- `get_main_ticker(company_uid)` - Get main ticker
- `set_main_ticker(company_uid, ticker_uid)` - Set main ticker
- `determine_main_ticker(company_uid)` - Auto-determine main ticker
- `validate_ticker_with_yfinance(ticker)` - Validate and update is_in_yfinance
- `validate_tickers_batch(tickers)` - Batch validate

### Universe Company Operations
- `store_universe_company(universe_company)` - Add company to universe
- `store_universe_companies(companies)` - Batch add companies
- `get_universe_companies(universe_id)` - Get companies with main tickers
- `delete_universe_company(universe_id, company_uid)` - Remove company
- `delete_all_universe_companies(universe_id)` - Remove all companies

## Migration Notes

- The `universe_tickers` table is kept for backward compatibility
- New code should use `universe_companies` endpoints
- Old endpoints still work but will eventually be deprecated
- Migration script preserves all existing data

## Error Handling

- Ticker validation failures are logged but don't stop processing
- Missing yfinance data is handled gracefully (fields set to NULL)
- Database connection errors are properly handled with retries
- Foreign key constraints ensure data integrity

## Performance Considerations

- Indexes created on frequently queried columns
- Partial unique index ensures only one main ticker per company
- LEFT JOINs used to handle missing company_info gracefully
- Batch operations available for bulk inserts

## Next Steps

1. Run `setup_varrock_schema.py` to create the schema
2. Run `migrate_to_varrock.py` to migrate existing data
3. Update frontend UI to use new `/companies` endpoints (optional)
4. Test all functionality with `test_varrock_schema.py`

