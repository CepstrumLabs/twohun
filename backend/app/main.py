from fastapi import FastAPI, HTTPException, Query, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, inspect, text, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError, DisconnectionError
from sqlalchemy.pool import QueuePool
from .models.stock import Base, Stock
from .services import stock_service
import os
from contextlib import asynccontextmanager, contextmanager
import logging
import datetime
import traceback
import sys
import time
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import correct config based on environment
if os.getenv('ENV') == 'prod':
    from .config.prod import ProdConfig as Config
    logger.info("=== Starting FastAPI in PRODUCTION mode ===")
else:
    from .config.dev import DevConfig as Config
    logger.info("=== Starting FastAPI in DEVELOPMENT mode ===")

logger.info(f"CORS_ORIGINS: {Config.CORS_ORIGINS}")
logger.info(f"DEBUG mode: {Config.DEBUG}")

app = FastAPI(debug=Config.DEBUG)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("="*50)
    logger.info("Starting FastAPI application...")
    logger.info("="*50)
    
    try:
        # Log database configuration (without sensitive info)
        logger.info("Database configuration loaded")
        logger.info(f"Database host: {Config.DATABASE_URL.split('@')[-1].split('/')[0]}")
        
        # Initialize database engine and session
        logger.info("Creating database engine...")
        engine = create_engine(
            Config.DATABASE_URL,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_pre_ping=True,
            pool_recycle=1800,
        )
        
        logger.info("Creating SessionLocal...")
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Store in app state
        app.state.engine = engine
        app.state.SessionLocal = SessionLocal
        
        # Try to establish initial connection
        logger.info("Testing database connection...")
        with engine.connect() as conn:
            # Start a transaction
            with conn.begin():
                conn.execute(text("SELECT 1"))
                logger.info("Database connection successful")
                
                # Create tables
                logger.info("Initializing database tables...")
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS stocks (
                        id SERIAL PRIMARY KEY,
                        ticker VARCHAR,
                        company_name VARCHAR,
                        ma_50 FLOAT,
                        ma_200 FLOAT,
                        date DATE,
                        price FLOAT,
                        roc_50 FLOAT,
                        roc_200 FLOAT,
                        signal VARCHAR,
                        roc_50_history FLOAT[],
                        roc_200_history FLOAT[]
                    );
                    
                    CREATE INDEX IF NOT EXISTS ix_stocks_ticker_date 
                    ON stocks(ticker, date);
                """))
                # No need for explicit commit - transaction will handle it
                logger.info("Database tables created successfully")
            
    except Exception as e:
        logger.error("="*50)
        logger.error("CRITICAL: Application startup failed")
        logger.error(f"Error: {str(e)}")
        logger.error(traceback.format_exc())
        logger.error("="*50)
        raise

    logger.info("Application startup completed successfully")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down application...")
    if hasattr(app.state, "engine"):
        app.state.engine.dispose()
        logger.info("Database engine disposed")

# Move these to helper functions
def get_db_session():
    if not hasattr(app.state, "SessionLocal"):
        raise RuntimeError("Database not initialized")
    db = app.state.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_connection():
    if not hasattr(app.state, "engine"):
        raise RuntimeError("Database engine not initialized")
    conn = app.state.engine.connect()
    try:
        yield conn
    finally:
        conn.close()

@app.get("/api/stocks")
async def get_stocks():
    with get_db_session() as db:
        stocks = stock_service.get_recent_stock_data(db)
        return stocks

@app.post("/api/stocks/{ticker}")
async def add_stock(
    ticker: str,
    days: int = Query(default=7, description="Number of days of history to fetch")
):
    with get_db_session() as db:
        new_entries = stock_service.fetch_stock_data(ticker, db, days)
        return {
            "message": f"Added {len(new_entries)} new entries for {ticker}",
            "entries": new_entries
        }

# Database check function
async def check_database():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        return True
    except Exception as e:
        logger.error(f"Database check failed: {str(e)}")
        return False

# Health check endpoint
@app.get("/health")
async def health_check():
    try:
        logger.info("Health check: attempting database connection")
        
        for attempt in range(3):
            try:
                with app.state.engine.connect() as conn:
                    with conn.begin():
                        result = conn.execute(text("SELECT 1"))
                        result.fetchone()
                        logger.info("Health check: database connection successful")
                        break
            except Exception as e:
                if attempt == 2:  # Last attempt
                    raise e
                logger.warning(f"Database connection attempt {attempt + 1} failed, retrying...")
                await asyncio.sleep(1)
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
                "timestamp": datetime.datetime.now().isoformat()
            }
        )

@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        # Get full traceback
        exc_type, exc_value, exc_traceback = sys.exc_info()
        
        # Format the traceback
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        tb_text = ''.join(tb_lines)
        
        # Log the full error
        logger.error(f"=== Unhandled Exception ===")
        logger.error(f"URL: {request.url}")
        logger.error(f"Method: {request.method}")
        logger.error(f"Headers: {request.headers}")
        logger.error(f"Exception: {str(e)}")
        logger.error(f"Traceback:\n{tb_text}")
        logger.error("="*50)
        
        # Return error response
        return JSONResponse(
            status_code=500,
            content={
                "detail": {
                    "error": str(e),
                    "type": exc_type.__name__,
                    "path": str(request.url),
                    "method": request.method,
                    "timestamp": datetime.datetime.now().isoformat()
                }
            }
        )

# Add error handlers for specific exceptions
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    logger.error(f"URL: {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": {
                "error": exc.detail,
                "path": str(request.url),
                "method": request.method,
                "timestamp": datetime.datetime.now().isoformat()
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # Get full traceback
    exc_type, exc_value, exc_traceback = sys.exc_info()
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    tb_text = ''.join(tb_lines)
    
    logger.error(f"=== General Exception ===")
    logger.error(f"URL: {request.url}")
    logger.error(f"Method: {request.method}")
    logger.error(f"Exception: {str(exc)}")
    logger.error(f"Traceback:\n{tb_text}")
    logger.error("="*50)
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": {
                "error": str(exc),
                "type": exc_type.__name__,
                "path": str(request.url),
                "method": request.method,
                "timestamp": datetime.datetime.now().isoformat()
            }
        }
    )

@app.get("/test-error")
async def test_error():
    raise Exception("Test error to check logging")
