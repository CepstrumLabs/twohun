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

# Database configuration
logger.info(f"Database URL: {Config.DATABASE_URL}")
engine = create_engine(
    Config.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_pre_ping=True,  # Enable connection health checks
    pool_recycle=1800,   # Recycle connections after 30 minutes
)
logger.info("Database engine created")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
logger.info("SessionLocal created")

# Add engine event listeners
@event.listens_for(engine, 'connect')
def connect(dbapi_connection, connection_record):
    logger.info("New database connection established")

@event.listens_for(engine, 'checkout')
def checkout(dbapi_connection, connection_record, connection_proxy):
    logger.info("Database connection checked out from pool")

@event.listens_for(engine, 'checkin')
def checkin(dbapi_connection, connection_record):
    logger.info("Database connection returned to pool")

# Simplified retry decorator
def retry_on_db_error(max_retries=3, delay=1):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (OperationalError, DisconnectionError) as e:
                    last_error = e
                    logger.warning(f"Database error (attempt {attempt + 1}/{max_retries}): {str(e)}")
                    if attempt + 1 < max_retries:
                        await asyncio.sleep(delay)  # Use asyncio.sleep instead of time.sleep
                        logger.info(f"Retrying database connection...")
            logger.error(f"All database connection attempts failed: {str(last_error)}")
            raise HTTPException(
                status_code=503,
                detail={
                    "status": "unhealthy",
                    "database": "disconnected",
                    "error": str(last_error),
                    "timestamp": datetime.datetime.now().isoformat()
                }
            )
        return wrapper
    return decorator

# Context manager for database sessions
@contextmanager
def get_db_session():
    db = SessionLocal()
    try:
        logger.debug("Database session created")
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        logger.debug("Database session closed")
        db.close()

# Context manager for raw connections
@contextmanager
def get_db_connection():
    conn = engine.connect()
    try:
        logger.debug("Database connection created")
        yield conn
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise
    finally:
        logger.debug("Database connection closed")
        conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("="*50)
    logger.info("Starting FastAPI application...")
    logger.info("="*50)
    
    with get_db_connection() as conn:
        # Create table if not exists using SQL directly
        logger.info("Initializing database...")
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
        conn.commit()
        logger.info("Database tables created successfully")
    
    yield
    
    logger.info("Shutting down FastAPI application...")
    # Close any remaining connections in the pool
    engine.dispose()
    logger.info("All database connections closed")

app = FastAPI(debug=Config.DEBUG, lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/stocks")
@retry_on_db_error(max_retries=3, delay=1)
async def get_stocks():
    with get_db_session() as db:
        stocks = stock_service.get_recent_stock_data(db)
        return stocks

@app.post("/api/stocks/{ticker}")
@retry_on_db_error(max_retries=3, delay=1)
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
                with get_db_connection() as conn:
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
        raise HTTPException(status_code=503, detail=str(e))

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
