from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from .models.stock import Base, Stock
from .services import stock_service
import os
from contextlib import asynccontextmanager
import logging
import datetime

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
engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("="*50)
    logger.info("Starting FastAPI application...")
    logger.info("="*50)
    
    with engine.begin() as conn:
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
async def get_stocks():
    db = SessionLocal()
    try:
        stocks = stock_service.get_recent_stock_data(db)
        return stocks
    finally:
        db.close()

@app.post("/api/stocks/{ticker}")
async def add_stock(
    ticker: str,
    days: int = Query(default=7, description="Number of days of history to fetch")
):
    db = SessionLocal()
    try:
        new_entries = stock_service.fetch_stock_data(ticker, db, days)
        return {
            "message": f"Added {len(new_entries)} new entries for {ticker}",
            "entries": new_entries
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@app.get("/health")
async def health_check():
    try:
        # Print connection details for debugging
        logging.info(f"Attempting to connect to database with URL: {Config.DATABASE_URL}")
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        return {
            "status": "healthy",
            "database": "connected",
            "database_url": Config.DATABASE_URL.replace(
                Config.DATABASE_URL.split("@")[0], "***"
            ),  # Hide credentials
            "timestamp": datetime.datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
                "timestamp": datetime.datetime.now().isoformat()
            }
        )
