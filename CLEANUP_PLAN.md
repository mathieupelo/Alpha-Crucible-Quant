# Repository Cleanup Plan

**Date:** 2024 (Updated)  
**Goal:** Identify everything that can be removed, moved, or simplified to make the codebase cleaner and architecture clearer.

---

## 📊 Executive Summary

### Quick Stats
- **Large files (>1000 lines):** ~5 files (frontend pages + backtest engine)
- **Duplicate validation functions:** 3 sets
- **Unused/rarely used modules:** 1 (`src/data/validation.py` - only in example script)
- **Duplicate asset directories:** ✅ **ALREADY CLEANED** (no `frontend/Assets/` found)
- **Empty/minimal files:** 0 (all `__init__.py` files have proper exports)
- **Scripts to consolidate:** Already well-organized in subdirectories
- **Root-level docs to move:** 0 (all docs already in `docs/` directory)
- **Unused imports:** `backend/main.py` imports `List` from typing (verify usage)

### ✅ Already Completed
- ✅ Database manager refactored to use mixins (`src/database/manager.py` uses operation mixins)
- ✅ Assets consolidated to `frontend/public/` only
- ✅ Scripts organized into logical subdirectories
- ✅ Documentation organized in `docs/` directory

---

## 🔴 HIGH PRIORITY - Quick Wins (Low Risk)

### 1. Remove Unused Import in `backend/main.py`
**Issue:** `from typing import List` imported but may not be used

**Action:**
- ⚠️ **Verify:** Check if `List` is actually used in `backend/main.py`
- ✅ **Remove:** If unused, remove the import

**Risk:** Very Low  
**Files:**
- `backend/main.py` (line 16) - remove unused `List` import

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

### 3. Review `src/data/validation.py` Usage
**Issue:** `src/data/validation.py` (437 lines) only used in `scripts/utils/run_backtest.py` (example script)

**Action:**
- ⚠️ **Decision needed:** 
  - Option A: Remove if truly unused in production code
  - Option B: Keep if it's useful for data quality checks (it's a comprehensive validator)
  - Option C: Move to `src/utils/` if it's a utility (but `src/utils/data_validation.py` already exists)

**Recommendation:** Keep for now - it's a comprehensive validator used in example scripts. Consider consolidating with `src/utils/data_validation.py` if there's overlap.

**Risk:** Low if keeping, Medium if refactoring  
**Files:**
- `src/data/validation.py` - verify usage, then decide

---

## 🟡 MEDIUM PRIORITY - Structural Improvements (Medium Risk)

### 5. Split Large Files

#### 5.1 `src/database/manager.py` - ✅ **ALREADY REFACTORED**
**Status:** ✅ **COMPLETED** - Already uses mixin pattern!

**Current Structure:**
- `src/database/manager.py` - Core connection and base operations (~226 lines)
- `src/database/signal_operations.py` - Signal-related operations (mixin)
- `src/database/portfolio_operations.py` - Portfolio operations (mixin)
- `src/database/backtest_operations.py` - Backtest operations (mixin)
- `src/database/universe_operations.py` - Universe operations (mixin)
- `src/database/score_operations.py` - Score operations (mixin)

**Action:** ✅ No action needed - architecture is clean!

---

#### 5.2 `src/backtest/engine.py` (~1328 lines)
**Issue:** Very large backtest engine file, but already partially modularized

**Current Structure:**
- ✅ `src/backtest/data_preparation.py` - Already exists
- ✅ `src/backtest/portfolio_rebalancing.py` - Already exists
- ✅ `src/backtest/metrics_calculation.py` - Already exists
- ✅ `src/backtest/results_storage.py` - Already exists
- ✅ `src/backtest/simulation.py` - Already exists

**Action:**
- ⚠️ **Review:** `src/backtest/engine.py` still has ~1328 lines
- ✅ **Consider:** Move remaining helper methods to appropriate modules
- ✅ **Target:** Reduce `engine.py` to ~400-500 lines (orchestration only)

**Risk:** Medium - ensure all methods remain accessible  
**Files:**
- `src/backtest/engine.py` - refactor to use helper modules more extensively

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
**Status:** ✅ **ALREADY WELL-ORGANIZED**

**Current Structure:**
- ✅ `scripts/dev/` - Development scripts
- ✅ `scripts/deploy/` - Deployment scripts
- ✅ `scripts/ops/` - Operational scripts
- ✅ `scripts/ngrok/` - Ngrok-related scripts
- ✅ `scripts/setup/` - Setup scripts
- ✅ `scripts/test/` - Test scripts
- ✅ `scripts/troubleshoot/` - Troubleshooting scripts
- ✅ `scripts/utils/` - Utility scripts

**Action:** ✅ No action needed - scripts are already well-organized!

---

## 🟠 LOW PRIORITY - Architectural Cleanup (Higher Risk)

### 7. Review Price Fetcher Modules

#### 7.1 `src/data/realtime_fetcher.py` vs `src/utils/price_fetcher.py`
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
**Issue:** Two requirements files with different purposes:
- `requirements.txt` (root) - Core library dependencies (plotting, testing, dev tools)
- `backend/requirements.txt` - Backend-specific dependencies (FastAPI, database, ML)

**Current State:**
- ✅ Both files serve distinct purposes
- ✅ Root `requirements.txt` is for `src/` directory (core quant library)
- ✅ `backend/requirements.txt` is for FastAPI backend

**Action:**
- ✅ **Keep both** - They serve different purposes
- ⚠️ **Document:** Add comment in root `requirements.txt` explaining the split (already has comment)
- ⚠️ **Consider:** Rename root `requirements.txt` to `requirements-core.txt` or `requirements-src.txt` for clarity

**Risk:** Low - just documentation/clarification  
**Files:**
- `requirements.txt` - Add/improve documentation
- `backend/requirements.txt` - Already clear

---

## 📋 Implementation Plan

### Phase 1: Quick Wins (1-2 PRs)
1. Remove unused `List` import from `backend/main.py`
2. Consolidate validation function usage (refactor `src/data/realtime_fetcher.py` to use utils)
3. Review and document `src/data/validation.py` usage decision

### Phase 2: Structural Improvements (3-5 PRs)
5. ✅ `src/database/manager.py` - Already refactored (no action needed)
6. Further refactor `src/backtest/engine.py` to reduce size
7. Split large frontend pages (one PR per page):
   - `frontend/src/pages/Home.tsx` (~2585 lines) ⚠️ **CRITICAL**
   - `frontend/src/pages/NewsDeepDive.tsx` (~1399 lines)
   - `frontend/src/pages/BacktestManager.tsx` (~1237 lines)
   - `frontend/src/pages/RunBacktest.tsx` (~1057 lines)
8. ✅ Scripts directory - Already well-organized (no action needed)

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

---

## 📝 Summary of Findings

### ✅ Good News - Already Clean
1. **Database Architecture:** `src/database/manager.py` already uses mixin pattern - well architected!
2. **Assets:** No duplicate asset directories found - already consolidated
3. **Scripts:** Already well-organized into logical subdirectories
4. **Documentation:** All docs already in `docs/` directory
5. **Init Files:** All `__init__.py` files have proper exports

### 🔴 Priority Actions (Low Risk)
1. **Remove unused import:** `backend/main.py` - verify and remove `List` from typing if unused
2. **Consolidate validation:** Refactor `src/data/realtime_fetcher.py` to use `src/utils/data_validation.py`
3. **Document decision:** Review `src/data/validation.py` usage and document decision

### 🟡 Medium Priority (Medium Risk)
1. **Large frontend pages:** Split 4 large page components (Home.tsx is critical at ~2585 lines)
2. **Backtest engine:** Further modularize `src/backtest/engine.py` (currently ~1328 lines)

### 🟠 Low Priority (Higher Risk)
1. **API structure:** Consider versioning and feature-based organization
2. **Component organization:** Consider feature-based component structure
3. **Requirements files:** Document the split between root and backend requirements

### ⚠️ Risky Items (Require Approval)
1. **Unused imports:** Use tooling to detect and remove (test thoroughly)
2. **Requirements consolidation:** Keep both files but improve documentation

---

## 🎯 Recommended PR Sequence

### PR 1: Quick Wins (Low Risk)
- Remove unused `List` import from `backend/main.py`
- Document `src/data/validation.py` decision

### PR 2: Validation Consolidation (Low Risk)
- Refactor `src/data/realtime_fetcher.py` to use `src/utils/data_validation.py`

### PR 3-6: Frontend Page Splits (Medium Risk, One Per PR)
- PR 3: Split `Home.tsx` (largest, most critical)
- PR 4: Split `NewsDeepDive.tsx`
- PR 5: Split `BacktestManager.tsx`
- PR 6: Split `RunBacktest.tsx`

### PR 7: Backtest Engine Refactor (Medium Risk)
- Further modularize `src/backtest/engine.py`

### PR 8+: Architectural Improvements (Higher Risk, Requires Approval)
- API structure reorganization
- Component organization changes
- Unused import cleanup (with tooling)

