# Dynamic Signal Columns Implementation

This document explains the implementation of dynamic signal columns in the Portfolio Details Signal Scores tab.

## Problem

The Signal Scores tab was showing hardcoded columns (RSI, SMA, MACD) that no longer exist in the system, causing "Error loading signal data" messages. The system needed to dynamically display the actual signals used for each portfolio.

## Solution

### Backend Changes

#### 1. Updated `get_portfolio_signals` Method

**File**: `backend/services/database_service.py`

**Changes**:
- Removed hardcoded signal names (`rsi`, `sma`, `macd`)
- Added dynamic detection of available signals from database
- Included `available_signals` array in response for frontend use

**Before**:
```python
signal_data = {
    'ticker': ticker,
    'rsi': None,
    'sma': None,
    'macd': None
}
```

**After**:
```python
signal_data = {
    'ticker': ticker,
    'available_signals': available_signals
}
# Add each signal value dynamically
for _, row in ticker_signals.iterrows():
    signal_name = row['signal_name']
    signal_data[signal_name] = row['value']
```

### Frontend Changes

#### 1. Dynamic Table Generation

**File**: `frontend/src/components/tables/PortfolioDetail.tsx`

**Changes**:
- Removed hardcoded column headers
- Added dynamic column generation based on `available_signals`
- Implemented proper error handling and loading states
- Added duplicate signal detection and sorting

**Key Features**:
- **Dynamic Columns**: Table columns are generated from actual signal data
- **Sorted Display**: Signal names are sorted alphabetically for consistency
- **Duplicate Handling**: Removes duplicate signal names with warning
- **Missing Data**: Shows "—" for missing signal values
- **Error States**: Clear error messages and loading indicators

#### 2. Improved User Experience

**Loading State**:
```tsx
{signalLoading ? (
  <Box>
    <Skeleton variant="rectangular" height={200} />
  </Box>
) : // ... rest of component
```

**Error State**:
```tsx
signalError ? (
  <Alert severity="error" sx={{ mb: 2 }}>
    Failed to load signal data. Please try again.
  </Alert>
) : // ... rest of component
```

**Empty State**:
```tsx
availableSignals.length === 0 ? (
  <Alert severity="info">
    This portfolio has no signal scores.
  </Alert>
) : // ... rest of component
```

## Data Flow

1. **Backend**: Queries database for signal data for specific portfolio/date
2. **Backend**: Extracts unique signal names from the data
3. **Backend**: Returns signal data with `available_signals` array
4. **Frontend**: Uses `available_signals` to generate table columns
5. **Frontend**: Renders dynamic table with actual signal values

## Example Response Structure

```json
{
  "signals": [
    {
      "ticker": "AAPL",
      "available_signals": ["SENTIMENT"],
      "SENTIMENT": 0.7234
    },
    {
      "ticker": "MSFT", 
      "available_signals": ["SENTIMENT"],
      "SENTIMENT": -0.4567
    }
  ]
}
```

## Edge Cases Handled

### 1. No Signals Available
- Shows "This portfolio has no signal scores" message
- Graceful handling without errors

### 2. Missing Signal Values
- Shows "—" placeholder for missing values
- Continues rendering other signals

### 3. Duplicate Signal Names
- Removes duplicates using `Set`
- Logs warning to console
- Keeps first occurrence

### 4. Empty Signal Data
- Shows appropriate empty state message
- No table rendered when no data

### 5. API Errors
- Clear error message with retry suggestion
- Maintains existing UI structure

## Backward Compatibility

- **Existing Portfolios**: Will show appropriate empty state if no signals
- **New Portfolios**: Will display actual signals used
- **API Changes**: Backend response includes additional `available_signals` field
- **Frontend**: Gracefully handles both old and new response formats

## Testing

### Backend Testing
```bash
cd backend
python test_portfolio_signals.py
```

### Frontend Testing
1. Open Portfolio Details dialog
2. Navigate to Signal Scores tab
3. Verify dynamic columns appear
4. Check error states by simulating API failures

## Future Enhancements

### 1. Signal Sorting
- Could add custom sorting by signal importance
- Currently sorts alphabetically for consistency

### 2. Signal Metadata
- Could display signal descriptions or ranges
- Currently shows signal names only

### 3. Performance Optimization
- Could cache signal metadata
- Currently queries database each time

### 4. Column Customization
- Could allow users to hide/show columns
- Currently shows all available signals

## Configuration

No configuration required. The system automatically:
- Detects available signals from database
- Generates appropriate table columns
- Handles all edge cases gracefully

## Monitoring

The system logs:
- Duplicate signal name warnings
- Missing signal data
- API errors during signal fetching

## Acceptance Criteria Met

✅ **Dynamic Columns**: Table shows actual signals used for portfolio
✅ **No Hardcoded Names**: Removed all RSI/SMA/MACD references
✅ **Proper Error Handling**: Clear loading, empty, and error states
✅ **Missing Data Handling**: Shows "—" for missing values
✅ **Backward Compatibility**: Works with existing portfolios
✅ **User-Friendly**: Clear messages and intuitive interface
