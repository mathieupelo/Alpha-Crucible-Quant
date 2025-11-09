"""
Ticker Management API Routes

FastAPI routes for managing tickers in the Varrock schema.
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional, Dict, Any
import logging
import uuid
import pandas as pd
from datetime import date, datetime

from security.input_validation import validate_ticker, sanitize_string
from models import ErrorResponse, SuccessResponse
from services.database_service import DatabaseService
from services.ticker_validation_service import TickerValidationService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
db_service = DatabaseService()
ticker_validator = TickerValidationService(
    timeout=15,
    max_retries=3,
    base_delay=2.0
)

# Valid markets list
VALID_MARKETS = [
    "NYSE", "NASDAQ", "NMS", "NGM", "NCM", "NYSEARCA", "NYSEAMERICAN", "BATS", 
    "OTC", "OTCQX", "OTCQB", "OTCBB", "PINK",
    "TSX", "TSXV", "CSE", "NEO",
    "LSE", "AIM", "Euronext", "FWB", "XETRA", "SWX", "SIX", "STO", "HEL", 
    "CPH", "VTX", "MCE", "BRU", "AMS", "LIS", "WSE",
    "TSE", "JPX", "JASDAQ",
    "KRX", "KOSPI", "KOSDAQ",
    "SSE", "SZSE", "HKEX", "HKSE", "TPE", "TWSE", "TPEx",
    "SGX", "SET", "IDX", "PSE", "MYX", "BURSA",
    "NSEI", "BSE", "MSEI",
    "ASX", "NZX",
    "JSE", "TASE", "DFM", "ADX", "MSM", "QSE", "BHB", "KSE", "Tadawul",
    "BMV", "B3", "BOVESPA", "BCBA", "BVL", "BVC",
    "MOEX", "MICEX", "KASE",
    "ADR", "OTC", "OTCQX", "OTCQB", "OTCBB", "PINK"
]


@router.get("/tickers/fetch-info")
async def fetch_ticker_info(ticker: str = Query(..., description="Ticker symbol to fetch info for")):
    """
    Fetch ticker information from yfinance without saving to database.
    Returns information for user to review before accepting.
    """
    try:
        # Validate ticker format
        validated_ticker = validate_ticker(ticker)
        
        # Fetch info from yfinance
        yf_ticker = ticker_validator.validate_ticker(validated_ticker)
        
        if not yf_ticker.get('is_valid'):
            raise HTTPException(
                status_code=404,
                detail=yf_ticker.get('error_message', 'Ticker not found in yfinance')
            )
        
        # Get detailed info from yfinance
        import yfinance as yf
        ticker_obj = yf.Ticker(validated_ticker)
        info = ticker_obj.info
        
        # Extract relevant information
        ticker_info = {
            'ticker': validated_ticker,
            'company_name': info.get('longName') or info.get('shortName') or info.get('name'),
            'short_name': info.get('shortName'),
            'sector': info.get('sector'),
            'industry': info.get('industry'),
            'market_cap': info.get('marketCap'),
            'currency': info.get('currency'),
            'exchange': info.get('exchange'),
            'country': info.get('country'),
            'website': info.get('website'),
            'description': info.get('longBusinessSummary'),
            'employees': info.get('fullTimeEmployees'),
            'founded_year': info.get('foundedYear'),
            'city': info.get('city'),
            'state': info.get('state'),
            'address': info.get('address1'),
            'phone': info.get('phone'),
        }
        
        return ticker_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching ticker info for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tickers/create")
async def create_ticker(
    ticker: str = Body(..., description="Ticker symbol"),
    yfinance_info: Optional[Dict[str, Any]] = Body(None, description="YFinance info (if already fetched)")
):
    """
    Create a new ticker and company in the database.
    If yfinance_info is provided, uses that; otherwise fetches from yfinance.
    """
    try:
        if not db_service.ensure_connection():
            raise HTTPException(status_code=503, detail="Database service unavailable")
        
        # Validate ticker format
        validated_ticker = validate_ticker(ticker)
        
        # Check if ticker already exists
        db_manager = db_service.db_manager
        existing_query = """
        SELECT company_uid FROM varrock.tickers WHERE ticker = %s LIMIT 1
        """
        existing_df = db_manager.execute_query(existing_query, (validated_ticker,))
        if not existing_df.empty:
            raise HTTPException(
                status_code=400,
                detail=f"Ticker {validated_ticker} already exists in database"
            )
        
        # Fetch info from yfinance if not provided
        if not yfinance_info:
            yf_result = ticker_validator.validate_ticker(validated_ticker)
            if not yf_result.get('is_valid'):
                raise HTTPException(
                    status_code=404,
                    detail=yf_result.get('error_message', 'Ticker not found in yfinance')
                )
            
            import yfinance as yf
            ticker_obj = yf.Ticker(validated_ticker)
            yfinance_info = ticker_obj.info
        
        # Create company
        company_uid = str(uuid.uuid4())
        create_company_query = """
        INSERT INTO varrock.companies (company_uid, created_at, updated_at)
        VALUES (%s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """
        db_manager.execute_insert(create_company_query, (company_uid,))
        
        # Create ticker record
        ticker_uid = str(uuid.uuid4())
        exchange = yfinance_info.get('exchange')
        market = exchange  # Use exchange as market initially
        
        ticker_insert_query = """
        INSERT INTO varrock.tickers (
            ticker_uid, company_uid, ticker, market, exchange, currency,
            is_in_yfinance, is_main_ticker, is_active, yfinance_symbol,
            first_seen_date, last_verified_date, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        """
        db_manager.execute_insert(
            ticker_insert_query,
            (
                ticker_uid, company_uid, validated_ticker, market, exchange,
                yfinance_info.get('currency'), True, True, True, validated_ticker,
                date.today(), date.today()
            )
        )
        
        # Create company info
        company_info_uid = str(uuid.uuid4())
        company_info_query = """
        INSERT INTO varrock.company_info (
            company_info_uid, company_uid, name, full_name, short_name,
            country, city, state, hq_address, phone, website,
            sector, industry, market_cap, currency, exchange,
            description, long_business_summary, employees, founded_year,
            data_source, last_updated
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        """
        db_manager.execute_insert(
            company_info_query,
            (
                company_info_uid, company_uid,
                yfinance_info.get('longName') or yfinance_info.get('shortName') or yfinance_info.get('name'),
                yfinance_info.get('longName'),
                yfinance_info.get('shortName'),
                yfinance_info.get('country'),
                yfinance_info.get('city'),
                yfinance_info.get('state'),
                yfinance_info.get('address1'),
                yfinance_info.get('phone'),
                yfinance_info.get('website'),
                yfinance_info.get('sector'),
                yfinance_info.get('industry'),
                yfinance_info.get('marketCap'),
                yfinance_info.get('currency'),
                exchange,
                yfinance_info.get('longBusinessSummary'),
                yfinance_info.get('longBusinessSummary'),
                yfinance_info.get('fullTimeEmployees'),
                yfinance_info.get('foundedYear'),
                'yfinance'
            )
        )
        
        return SuccessResponse(message=f"Ticker {validated_ticker} created successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating ticker {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tickers/add-alternative")
async def add_alternative_ticker(
    company_uid: str = Body(..., description="Company UID to add ticker to"),
    ticker: str = Body(..., description="Alternative ticker symbol"),
    market: str = Body(..., description="Market for the ticker")
):
    """
    Add an alternative ticker to an existing company.
    """
    try:
        if not db_service.ensure_connection():
            raise HTTPException(status_code=503, detail="Database service unavailable")
        
        # Validate inputs
        validated_ticker = validate_ticker(ticker)
        validated_market = market.strip().upper()
        
        if validated_market not in VALID_MARKETS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid market. Must be one of: {', '.join(VALID_MARKETS)}"
            )
        
        db_manager = db_service.db_manager
        
        # Verify company exists
        company_query = """
        SELECT company_uid FROM varrock.companies WHERE company_uid = %s
        """
        company_df = db_manager.execute_query(company_query, (company_uid,))
        if company_df.empty:
            raise HTTPException(status_code=404, detail=f"Company {company_uid} not found")
        
        # Check if ticker already exists
        existing_query = """
        SELECT ticker_uid FROM varrock.tickers WHERE ticker = %s AND market = %s
        """
        existing_df = db_manager.execute_query(existing_query, (validated_ticker, validated_market))
        if not existing_df.empty:
            raise HTTPException(
                status_code=400,
                detail=f"Ticker {validated_ticker} with market {validated_market} already exists"
            )
        
        # Get company info for validation display
        company_info_query = """
        SELECT name, main_ticker.ticker as main_ticker
        FROM varrock.company_info ci
        LEFT JOIN varrock.companies c ON ci.company_uid = c.company_uid
        LEFT JOIN LATERAL (
            SELECT ticker FROM varrock.tickers
            WHERE company_uid = c.company_uid AND is_main_ticker = TRUE
            LIMIT 1
        ) main_ticker ON TRUE
        WHERE ci.company_uid = %s
        """
        company_info_df = db_manager.execute_query(company_info_query, (company_uid,))
        
        if company_info_df.empty:
            raise HTTPException(status_code=404, detail=f"Company info for {company_uid} not found")
        
        company_info = company_info_df.iloc[0]
        
        # Create alternative ticker
        ticker_uid = str(uuid.uuid4())
        ticker_insert_query = """
        INSERT INTO varrock.tickers (
            ticker_uid, company_uid, ticker, market, exchange, currency,
            is_in_yfinance, is_main_ticker, is_active, yfinance_symbol,
            first_seen_date, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        """
        db_manager.execute_insert(
            ticker_insert_query,
            (
                ticker_uid, company_uid, validated_ticker, validated_market,
                validated_market, None, False, False, True, validated_ticker,
                date.today()
            )
        )
        
        return {
            "message": f"Alternative ticker {validated_ticker} added successfully",
            "company_uid": company_uid,
            "company_name": company_info.get('name'),
            "main_ticker": company_info.get('main_ticker'),
            "new_ticker": validated_ticker,
            "market": validated_market
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding alternative ticker {ticker} to company {company_uid}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tickers/company/{company_uid}")
async def get_company_info(company_uid: str):
    """
    Get company information for validation when adding alternative ticker.
    """
    try:
        if not db_service.ensure_connection():
            raise HTTPException(status_code=503, detail="Database service unavailable")
        
        db_manager = db_service.db_manager
        
        query = """
        SELECT 
            c.company_uid,
            ci.name as company_name,
            ci.sector,
            ci.industry,
            ci.country,
            ci.currency,
            ci.exchange,
            ARRAY_AGG(t.ticker ORDER BY t.is_main_ticker DESC, t.created_at) FILTER (WHERE t.ticker IS NOT NULL) as all_tickers,
            (SELECT ticker FROM varrock.tickers WHERE company_uid = c.company_uid AND is_main_ticker = TRUE LIMIT 1) as main_ticker
        FROM varrock.companies c
        LEFT JOIN varrock.company_info ci ON c.company_uid = ci.company_uid
        LEFT JOIN varrock.tickers t ON c.company_uid = t.company_uid
        WHERE c.company_uid = %s
        GROUP BY c.company_uid, ci.name, ci.sector, ci.industry, ci.country, ci.currency, ci.exchange
        """
        
        result_df = db_manager.execute_query(query, (company_uid,))
        
        if result_df.empty:
            raise HTTPException(status_code=404, detail=f"Company {company_uid} not found")
        
        row = result_df.iloc[0]
        
        # Handle array field
        all_tickers = row.get('all_tickers', [])
        if isinstance(all_tickers, str):
            import re
            all_tickers = re.findall(r'"([^"]+)"', all_tickers) if all_tickers else []
        elif all_tickers is None:
            all_tickers = []
        
        return {
            "company_uid": str(row['company_uid']),
            "company_name": str(row['company_name']) if row.get('company_name') else None,
            "sector": str(row['sector']) if row.get('sector') else None,
            "industry": str(row['industry']) if row.get('industry') else None,
            "country": str(row['country']) if row.get('country') else None,
            "currency": str(row['currency']) if row.get('currency') else None,
            "exchange": str(row['exchange']) if row.get('exchange') else None,
            "main_ticker": str(row['main_ticker']) if row.get('main_ticker') else None,
            "all_tickers": all_tickers if isinstance(all_tickers, list) else list(all_tickers)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting company info for {company_uid}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tickers/all")
async def get_all_tickers(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size")
):
    """
    Get all tickers in the database with company information.
    """
    try:
        if not db_service.ensure_connection():
            raise HTTPException(status_code=503, detail="Database service unavailable")
        
        db_manager = db_service.db_manager
        
        # Get total count
        try:
            count_query = """
            SELECT COUNT(DISTINCT c.company_uid) as total
            FROM varrock.companies c
            """
            count_df = db_manager.execute_query(count_query)
            if count_df.empty or len(count_df) == 0:
                total = 0
            else:
                total = int(count_df.iloc[0]['total'])
        except Exception as e:
            logger.error(f"Error getting count: {e}")
            total = 0
        
        # Get paginated results
        offset = (page - 1) * size
        query = """
        SELECT DISTINCT
            c.company_uid,
            ci.name as company_name,
            ci.sector,
            ci.industry,
            ci.country,
            ci.currency,
            ci.exchange,
            ci.market_cap,
            (SELECT ticker FROM varrock.tickers WHERE company_uid = c.company_uid AND is_main_ticker = TRUE LIMIT 1) as main_ticker
        FROM varrock.companies c
        LEFT JOIN varrock.company_info ci ON c.company_uid = ci.company_uid
        ORDER BY ci.name NULLS LAST, main_ticker NULLS LAST
        LIMIT %s OFFSET %s
        """
        
        try:
            result_df = db_manager.execute_query(query, (size, offset))
        except Exception as e:
            logger.error(f"Error executing main query: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")
        
        # Get detailed ticker info for each company
        companies = []
        if result_df.empty:
            # Return empty result if no companies found
            return {
                "companies": [],
                "total": total,
                "page": page,
                "size": size
            }
        
        for _, row in result_df.iterrows():
            company_uid = str(row['company_uid'])
            
            # Get all tickers with details for this company
            try:
                tickers_query = """
                SELECT 
                    ticker,
                    market,
                    exchange,
                    is_main_ticker,
                    is_active,
                    is_in_yfinance
                FROM varrock.tickers
                WHERE company_uid = %s
                ORDER BY is_main_ticker DESC, created_at
                """
                tickers_df = db_manager.execute_query(tickers_query, (company_uid,))
            except Exception as e:
                logger.warning(f"Error getting tickers for company {company_uid}: {e}")
                tickers_df = pd.DataFrame()
            
            tickers = []
            if not tickers_df.empty:
                for _, ticker_row in tickers_df.iterrows():
                    tickers.append({
                        "ticker": str(ticker_row['ticker']),
                        "market": str(ticker_row['market']) if ticker_row.get('market') else None,
                        "exchange": str(ticker_row['exchange']) if ticker_row.get('exchange') else None,
                        "is_main_ticker": bool(ticker_row.get('is_main_ticker', False)),
                        "is_active": bool(ticker_row.get('is_active', True)),
                        "is_in_yfinance": bool(ticker_row.get('is_in_yfinance', False))
                    })
            
            companies.append({
                "company_uid": company_uid,
                "company_name": str(row['company_name']) if pd.notna(row.get('company_name')) else None,
                "sector": str(row['sector']) if pd.notna(row.get('sector')) else None,
                "industry": str(row['industry']) if pd.notna(row.get('industry')) else None,
                "country": str(row['country']) if pd.notna(row.get('country')) else None,
                "currency": str(row['currency']) if pd.notna(row.get('currency')) else None,
                "exchange": str(row['exchange']) if pd.notna(row.get('exchange')) else None,
                "market_cap": float(row['market_cap']) if pd.notna(row.get('market_cap')) else None,
                "main_ticker": str(row['main_ticker']) if pd.notna(row.get('main_ticker')) else None,
                "tickers": tickers
            })
        
        return {
            "companies": companies,
            "total": total,
            "page": page,
            "size": size
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting all tickers: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting all tickers: {str(e)}")


@router.get("/tickers/search")
async def search_companies(
    query: str = Query(..., description="Search query (company name or ticker)"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results")
):
    """
    Search for companies by name or ticker.
    """
    try:
        if not db_service.ensure_connection():
            raise HTTPException(status_code=503, detail="Database service unavailable")
        
        db_manager = db_service.db_manager
        
        search_query = """
        SELECT DISTINCT
            c.company_uid,
            ci.name as company_name,
            (SELECT ticker FROM varrock.tickers WHERE company_uid = c.company_uid AND is_main_ticker = TRUE LIMIT 1) as main_ticker
        FROM varrock.companies c
        LEFT JOIN varrock.company_info ci ON c.company_uid = ci.company_uid
        LEFT JOIN varrock.tickers t ON c.company_uid = t.company_uid
        WHERE 
            LOWER(ci.name) LIKE LOWER(%s) OR
            LOWER(t.ticker) LIKE LOWER(%s)
        ORDER BY ci.name NULLS LAST
        LIMIT %s
        """
        
        search_pattern = f"%{query}%"
        result_df = db_manager.execute_query(search_query, (search_pattern, search_pattern, limit))
        
        results = []
        for _, row in result_df.iterrows():
            results.append({
                "company_uid": str(row['company_uid']),
                "company_name": str(row['company_name']) if row.get('company_name') else None,
                "main_ticker": str(row['main_ticker']) if row.get('main_ticker') else None
            })
        
        return {"results": results, "total": len(results)}
        
    except Exception as e:
        logger.error(f"Error searching companies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

