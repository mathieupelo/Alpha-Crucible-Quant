# Repository Cleanup Plan

**Date:** 2024  
**Goal:** Identify everything that can be removed, moved, or simplified to make the codebase cleaner and architecture clearer.

---

## 📊 Executive Summary

### Quick Stats
- **Large files (>1000 lines):** 7 files
- **Duplicate validation functions:** 3 sets
- **Unused/rarely used modules:** 2
- **Duplicate asset directories:** 2
- **Empty/minimal files:** 1
- **Scripts to consolidate:** ~15
- **Root-level docs to move:** 5

---

## 🔴 HIGH PRIORITY - Quick Wins (Low Risk)

### 1. Remove Duplicate Asset Directories
**Issue:** Assets exist in both `frontend/Assets/` and `frontend/public/`
- `frontend/Assets/Images/` duplicates `frontend/public/sectors/`
- `frontend/Assets/videos/` appears unused

**Action:**
- ✅ **Remove:** `frontend/Assets/` directory (use `frontend/public/` only)
- ✅ **Verify:** All imports reference `public/` paths

**Risk:** Low - just asset consolidation  
**Files:**
- `frontend/Assets/Images/gaming.webp` → delete (duplicate)
- `frontend/Assets/Images/movies.png` → delete (duplicate)  
- `frontend/Assets/Images/Sports.png` → delete (duplicate)
- `frontend/Assets/videos/gaming.mp4` → verify usage, then delete if unused

---

### 2. Consolidate Duplicate Validation Functions
**Issue:** Same validation logic exists in multiple places

**Duplicates Found:**
1. `validate_ticker()`:
   - `backend/security/input_validation.py` (API validation, raises HTTPException)
   - `src/data/realtime_fetcher.py` (internal validation, returns bool)
   - `backend/services/ticker_validation_service.py` (service validation, returns Dict)

2. `validate_date_range()`:
   - `backend/security/input_validation.py` (API validation)
   - `src/utils/data_validation.py` (internal validation)

3. `validate_ticker_list()`:
   - `backend/security/input_validation.py` (API validation)
   - `src/utils/data_validation.py` (internal validation)

**Action:**
- ✅ **Keep:** `backend/security/input_validation.py` for API layer (raises HTTPException)
- ✅ **Keep:** `src/utils/data_validation.py` for internal validation (returns bool)
- ⚠️ **Review:** `src/data/realtime_fetcher.py::validate_ticker()` - consider using `src/utils/data_validation.py` instead
- ⚠️ **Review:** `backend/services/ticker_validation_service.py` - ensure it doesn't duplicate API validation

**Risk:** Low - just refactoring imports  
**Files:**
- `src/data/realtime_fetcher.py` (line 455) - refactor to use utils
- `backend/services/ticker_validation_service.py` - verify no duplication

---

### 3. Remove Empty/Minimal Files
**Issue:** Empty or near-empty `__init__.py` files

**Action:**
- ✅ **Remove:** `backend/services/__init__.py` (only contains comment "# Backend services package")
- ✅ **Keep:** Other `__init__.py` files that export symbols

**Risk:** Very Low  
**Files:**
- `backend/services/__init__.py` → delete or add proper exports

---

### 4. Move Root-Level Documentation
**Issue:** Documentation files scattered in root directory

**Action:**
- ✅ **Move to `docs/`:**
  - `ANALYSIS_REPORT.md` → `docs/ANALYSIS_REPORT.md`
  - `DEVELOPMENT_WORKFLOW.md` → `docs/DEVELOPMENT_WORKFLOW.md`
  - `IMPROVEMENTS_SUMMARY.md` → `docs/IMPROVEMENTS_SUMMARY.md`
  - `NEWS_SETUP.md` → `docs/NEWS_SETUP.md`
  - `RUN.md` → `docs/RUN.md`

**Risk:** Low - update any references  
**Files:** 5 markdown files in root

---

## 🟡 MEDIUM PRIORITY - Structural Improvements (Medium Risk)

### 5. Split Large Files

#### 5.1 `src/database/manager.py` (1104 lines) - **GOD MODULE**
**Issue:** Single file handles all database operations (signals, portfolios, backtests, universes, NAV, etc.)

**Action:**
- ✅ **Split into:**
  - `src/database/manager.py` - Core connection and base operations (keep ~200 lines)
  - `src/database/signal_operations.py` - Signal-related operations
  - `src/database/portfolio_operations.py` - Portfolio operations
  - `src/database/backtest_operations.py` - Backtest operations
  - `src/database/universe_operations.py` - Universe operations
  - `src/database/nav_operations.py` - NAV operations

**Risk:** Medium - requires careful import refactoring  
**Files:**
- `src/database/manager.py` → split into 6 files
- Update all imports in: `backend/services/database_service.py`, `src/backtest/engine.py`, etc.

---

#### 5.2 `src/backtest/engine.py` (1313 lines)
**Issue:** Very large backtest engine file

**Action:**
- ✅ **Split into:**
  - `src/backtest/engine.py` - Main engine class (~400 lines)
  - `src/backtest/data_preparation.py` - Data fetching and preparation
  - `src/backtest/portfolio_rebalancing.py` - Rebalancing logic
  - `src/backtest/metrics_calculation.py` - Performance metrics
  - `src/backtest/results_storage.py` - Database storage

**Risk:** Medium - ensure all methods remain accessible  
**Files:**
- `src/backtest/engine.py` → split into 5 files

---

#### 5.3 Frontend Large Files

**5.3.1 `frontend/src/pages/Home.tsx` (2585 lines)** ⚠️ **CRITICAL**
**Action:**
- ✅ **Split into:**
  - `frontend/src/pages/Home.tsx` - Main page component (~200 lines)
  - `frontend/src/components/home/HeroSection.tsx`
  - `frontend/src/components/home/MetricsSection.tsx`
  - `frontend/src/components/home/BacktestHistorySection.tsx`
  - `frontend/src/components/home/NewsSection.tsx`
  - `frontend/src/hooks/useHomeData.ts` - Data fetching logic

**Risk:** Medium - large refactor  
**Files:** 1 file → 6 files

---

**5.3.2 `frontend/src/pages/NewsDeepDive.tsx` (1399 lines)**
**Action:**
- ✅ **Split into:**
  - `frontend/src/pages/NewsDeepDive.tsx` - Main page (~200 lines)
  - `frontend/src/components/news/NewsFilters.tsx`
  - `frontend/src/components/news/NewsList.tsx`
  - `frontend/src/components/news/NewsDetail.tsx`
  - `frontend/src/hooks/useNewsData.ts`

**Risk:** Medium  
**Files:** 1 file → 5 files

---

**5.3.3 `frontend/src/pages/BacktestManager.tsx` (1237 lines)**
**Action:**
- ✅ **Split into:**
  - `frontend/src/pages/BacktestManager.tsx` - Main page (~200 lines)
  - `frontend/src/components/backtests/BacktestList.tsx`
  - `frontend/src/components/backtests/BacktestFilters.tsx`
  - `frontend/src/components/backtests/BacktestActions.tsx`
  - `frontend/src/hooks/useBacktests.ts`

**Risk:** Medium  
**Files:** 1 file → 5 files

---

**5.3.4 `frontend/src/pages/RunBacktest.tsx` (1057 lines)**
**Action:**
- ✅ **Split into:**
  - `frontend/src/pages/RunBacktest.tsx` - Main page (~200 lines)
  - `frontend/src/components/backtests/BacktestConfigForm.tsx`
  - `frontend/src/components/backtests/UniverseSelector.tsx`
  - `frontend/src/components/backtests/SignalSelector.tsx`
  - `frontend/src/hooks/useBacktestConfig.ts`

**Risk:** Medium  
**Files:** 1 file → 5 files

---

**5.3.5 `frontend/src/App.tsx` (394 lines)**
**Action:**
- ✅ **Split into:**
  - `frontend/src/App.tsx` - Main app (~100 lines)
  - `frontend/src/theme/theme.ts` - Theme configuration
  - `frontend/src/providers/AppProviders.tsx` - QueryClient, Theme providers

**Risk:** Low  
**Files:** 1 file → 3 files

---

### 6. Consolidate Scripts Directory
**Issue:** 30+ scripts, many with overlapping functionality

**Action:**
- ✅ **Group by category:**
  - `scripts/dev/` - Development scripts
    - `dev_all.bat`, `dev_backend.bat`, `dev_frontend.bat`, `dev_docker.bat`
  - `scripts/deploy/` - Deployment scripts
    - `deploy.bat`, `deploy.sh`, `rebuild_docker_no_cache.bat`
  - `scripts/ops/` - Operational scripts
    - `restart_all.bat`, `restart_backend.bat`, `full_restart.bat`, `full_restart_with_docker.bat`
  - `scripts/ngrok/` - Ngrok-related scripts
    - `start_ngrok.bat`, `kill_ngrok.bat`, `check_ngrok.bat`, `prepare_and_start_ngrok_final.bat`, `setup_ngrok.py`
  - `scripts/setup/` - Setup scripts
    - `setup_database.py`, `setup_dev.py`, `setup_ngrok.py`
  - `scripts/test/` - Test scripts
    - `test_db_connection.bat`, `test_imports.py`, `test_openai_key.py`, `verify_connectivity.bat`
  - `scripts/troubleshoot/` - Troubleshooting scripts
    - `check_and_fix_iis.bat`, `fix_frontend_cache.bat`, `fix_nginx_ips_v2.bat`, `kill_port_3000.bat`
    - `CACHE_TROUBLESHOOTING.md`, `FIX_PORT_3000.md`
  - `scripts/utils/` - Utility scripts
    - `cleanup_all.bat`, `clear_all_cache.bat`, `quick_start.bat`, `run_backtest.py`, `migrate_to_signals_table.py`

**Risk:** Low - just reorganization  
**Files:** 30+ scripts → organized into 7 subdirectories

---

## 🟠 LOW PRIORITY - Architectural Cleanup (Higher Risk)

### 7. Review Unused/Rarely Used Modules

#### 7.1 `src/data/validation.py` (437 lines)
**Issue:** Only used in `scripts/run_backtest.py` (example script)

**Action:**
- ⚠️ **Decision needed:** 
  - Option A: Remove if truly unused in production code
  - Option B: Keep if it's useful for data quality checks
  - Option C: Move to `src/utils/` if it's a utility

**Risk:** Low if removing, Medium if refactoring  
**Files:**
- `src/data/validation.py` - verify usage, then remove or move

---

#### 7.2 `src/data/realtime_fetcher.py` vs `src/utils/price_fetcher.py`
**Issue:** Two similar modules for fetching price data

**Current usage:**
- `src/utils/price_fetcher.py` wraps `src/data/realtime_fetcher.py`
- `src/data/realtime_fetcher.py` is the underlying implementation

**Action:**
- ⚠️ **Review:** Consider consolidating or clarifying the relationship
- ✅ **Keep both** if they serve different purposes (real-time vs historical)
- ⚠️ **Refactor** if there's significant overlap

**Risk:** Medium - requires understanding usage patterns  
**Files:**
- `src/data/realtime_fetcher.py` (546 lines)
- `src/utils/price_fetcher.py` (262 lines)

---

### 8. Feature Boundary Organization

#### 8.1 Backend API Structure
**Current:** `backend/api/` has all endpoints in flat structure

**Action:**
- ✅ **Consider grouping by feature:**
  - `backend/api/v1/backtests/` - Backtest endpoints
  - `backend/api/v1/portfolios/` - Portfolio endpoints
  - `backend/api/v1/signals/` - Signal endpoints
  - `backend/api/v1/universes/` - Universe endpoints
  - `backend/api/v1/market/` - Market data endpoints
  - `backend/api/v1/news/` - News endpoints

**Risk:** Medium - requires route updates  
**Files:** 7 API files → organized structure

---

#### 8.2 Frontend Component Organization
**Current:** Components organized by type (cards, charts, tables, etc.)

**Action:**
- ✅ **Consider feature-based organization:**
  - `frontend/src/components/backtests/` - All backtest-related components
  - `frontend/src/components/portfolios/` - Portfolio components
  - `frontend/src/components/news/` - News components (already exists)
  - `frontend/src/components/common/` - Shared components (keep)

**Risk:** Medium - requires import updates  
**Files:** Reorganize component structure

---

## ⚠️ RISKY ITEMS - Require Explicit Approval

### 9. Remove Unused Exports/Imports
**Issue:** May have unused imports that could break if removed

**Action:**
- ⚠️ **Use tooling:** Run `pylint`, `flake8`, or `unimport` to detect unused imports
- ⚠️ **Manual review:** Check TypeScript files with `ts-unused-exports`
- ⚠️ **Test thoroughly:** After removing, run full test suite

**Risk:** High - may break if imports are used dynamically  
**Files:** All Python and TypeScript files

---

### 10. Consolidate Requirements Files
**Issue:** Two requirements files:
- `requirements.txt` (root)
- `backend/requirements.txt`

**Action:**
- ⚠️ **Review:** Determine if both are needed
- ⚠️ **Consolidate:** If possible, use single requirements file
- ⚠️ **Document:** Clarify which file is for what purpose

**Risk:** Medium - may affect deployment  
**Files:**
- `requirements.txt`
- `backend/requirements.txt`

---

## 📋 Implementation Plan

### Phase 1: Quick Wins (1-2 PRs)
1. Remove duplicate asset directories
2. Move root-level documentation
3. Remove empty `__init__.py`
4. Consolidate validation function usage

### Phase 2: Structural Improvements (3-5 PRs)
5. Split `src/database/manager.py`
6. Split `src/backtest/engine.py`
7. Split large frontend pages (one PR per page)
8. Reorganize scripts directory

### Phase 3: Architectural Cleanup (2-3 PRs)
9. Review and consolidate `src/data/` modules
10. Reorganize backend API structure
11. Reorganize frontend components by feature

### Phase 4: Polish (1 PR)
12. Remove unused imports (with tooling)
13. Consolidate requirements files

---

## ✅ Checklist Before Starting

- [ ] Create backup branch
- [ ] Run full test suite to establish baseline
- [ ] Document current import patterns
- [ ] Get approval for risky items
- [ ] Plan PR sequence

---

## 📝 Notes

- **No behavior changes** without explicit approval
- **No new dependencies** to be added
- **Small PRs** - one logical change per PR
- **Test after each change** - don't batch risky changes

---

**Next Step:** Review this plan and approve specific items before implementation begins.

