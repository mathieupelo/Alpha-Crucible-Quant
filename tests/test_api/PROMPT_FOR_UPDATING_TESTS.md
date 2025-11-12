# Detailed Prompt for Updating API Tests When Code Changes

Use this prompt when you modify API endpoints, add new endpoints, change request/response models, or modify authentication logic.

---

## Prompt Template

```
I've made changes to the API codebase. Please update the API tests in `tests/test_api/` to reflect these changes.

## Changes Made

[Describe the specific changes you made, for example:]
- Added a new endpoint: POST /api/universes/{id}/companies/batch
- Modified the response model for GET /api/backtests to include a new field 'status'
- Changed authentication from API key to JWT tokens
- Updated the error response format for validation errors
- Added pagination to GET /api/signals endpoint
- Removed the DELETE /api/portfolios/{id} endpoint

## Specific Details

[Provide any specific details needed, for example:]
- The new batch endpoint accepts a list of tickers and returns a list of company responses
- The status field can be 'running', 'completed', or 'failed'
- JWT tokens should be in the Authorization header as "Bearer <token>"
- Validation errors now return 422 status code with a 'errors' array field
- Pagination uses 'page' and 'limit' query parameters (not 'size')

## Test Requirements

[Specify what you want tested, for example:]
- Add tests for the new batch endpoint including success and error cases
- Update existing backtest tests to verify the new 'status' field
- Update all authentication tests to use JWT instead of API key
- Add tests for pagination edge cases (page 0, negative page, etc.)
- Remove tests for the deleted endpoint

## Database Considerations

[If relevant, mention database changes:]
- The new endpoint creates records in a new 'universe_companies_batch' table
- Make sure tests clean up this new table data
- The status field is stored in the 'backtests' table

## Mocking Requirements

[If external services are involved:]
- The new endpoint calls an external API - mock it with responses: {...}
- Update yfinance mocks to return new data structure: {...}
```

---

## Example Usage

### Example 1: Adding a New Endpoint

```
I've made changes to the API codebase. Please update the API tests in `tests/test_api/` to reflect these changes.

## Changes Made

- Added a new endpoint: GET /api/backtests/{run_id}/performance
- This endpoint returns detailed performance metrics including drawdown periods

## Specific Details

- The endpoint returns a JSON object with:
  - 'metrics': object with sharpe_ratio, max_drawdown, etc.
  - 'drawdown_periods': array of objects with start_date, end_date, depth
- Returns 404 if backtest doesn't exist
- Requires authentication

## Test Requirements

- Add a new test class TestBacktestPerformance in test_api_backtests.py
- Test successful retrieval of performance data
- Test 404 when backtest doesn't exist
- Test authentication requirement
- Verify response structure matches expected format

## Database Considerations

- The data comes from existing backtest_metrics table
- No new tables created
- Use existing test_universe fixture to create a backtest for testing
```

### Example 2: Changing Authentication

```
I've made changes to the API codebase. Please update the API tests in `tests/test_api/` to reflect these changes.

## Changes Made

- Changed authentication from API key to JWT tokens
- Updated main.py to use JWT verification instead of API key verification

## Specific Details

- JWT tokens are provided in Authorization header as "Bearer <token>"
- Tokens are verified using a secret key from environment variable JWT_SECRET
- Invalid tokens return 401 Unauthorized
- Missing tokens return 403 Forbidden

## Test Requirements

- Update conftest.py to use JWT tokens instead of API keys
- Update authenticated_client fixture to generate valid JWT tokens
- Update unauthenticated_client fixture to not include tokens
- Update all authentication test assertions to expect 401 for invalid tokens
- Add tests for expired tokens, malformed tokens, etc.

## Database Considerations

- No database changes
- Authentication is handled in middleware
```

### Example 3: Modifying Response Models

```
I've made changes to the API codebase. Please update the API tests in `tests/test_api/` to reflect these changes.

## Changes Made

- Modified BacktestResponse model to include new fields: 'status' and 'error_message'
- Updated GET /api/backtests/{run_id} to return these new fields

## Specific Details

- 'status' field: string enum ('pending', 'running', 'completed', 'failed')
- 'error_message' field: optional string, only present if status is 'failed'
- All existing backtests will have status='completed' by default

## Test Requirements

- Update test_get_backtest_by_id to verify new fields are present
- Add test for backtest with failed status and error_message
- Update test assertions to check status field values
- Ensure backward compatibility (tests should still pass with old data)

## Database Considerations

- New columns added to 'backtests' table: status, error_message
- Existing records have status='completed' and error_message=NULL
- No cleanup changes needed
```

---

## What the AI Will Do

When you provide this prompt, the AI will:

1. **Analyze the changes** - Understand what was modified
2. **Update existing tests** - Modify tests that are affected by the changes
3. **Add new tests** - Create tests for new endpoints/features
4. **Remove obsolete tests** - Delete tests for removed endpoints
5. **Update fixtures** - Modify conftest.py if needed for new authentication, mocks, etc.
6. **Update cleanup logic** - Ensure test data cleanup handles new tables/fields
7. **Verify test structure** - Ensure tests follow the same patterns as existing tests
8. **Run tests** - Execute tests to verify they work correctly

## Best Practices

1. **Be specific** - Provide exact endpoint paths, field names, status codes
2. **Include examples** - Show example request/response JSON if helpful
3. **Mention edge cases** - If you want specific edge cases tested
4. **Database changes** - Always mention if new tables/columns are added
5. **Breaking changes** - Clearly mark any breaking changes that require test updates

## Common Scenarios

### Adding a New Endpoint
- Specify the HTTP method, path, request body, response format
- Mention if it requires authentication
- Specify what database tables it uses

### Modifying an Existing Endpoint
- Specify which endpoint changed
- List what changed (request params, response fields, behavior)
- Mention if it's backward compatible

### Changing Authentication
- Specify the new authentication method
- Provide how to generate valid tokens/credentials
- Mention if any endpoints are now public/private

### Database Schema Changes
- List new tables/columns
- Mention if existing data needs migration
- Specify cleanup requirements for new tables

---

## Quick Reference

**Test File Locations:**
- `tests/test_api/conftest.py` - Shared fixtures
- `tests/test_api/test_api_*.py` - Endpoint-specific tests

**Key Fixtures:**
- `authenticated_client` - Client with valid auth
- `unauthenticated_client` - Client without auth
- `test_universe` - Test universe with tickers
- `mock_yfinance` - Mocked yfinance
- `mock_openai` - Mocked OpenAI

**Test Patterns:**
- Authentication tests check for 401/403 on unauthenticated requests
- CRUD tests verify create, read, update, delete operations
- Error tests verify 404, 400, 500 responses
- Cleanup is automatic via `cleanup_test_data` fixture

