from ..services import stock_service
from ..config.tickers import POPULAR_TICKERS
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import os
import sys
import time

# Import correct config based on environment
if os.getenv('ENV') == 'prod':
    from ..config.prod import ProdConfig as Config
else:
    from ..config.dev import DevConfig as Config

def populate_stocks():
    # Create database connection
    engine = create_engine(Config.DATABASE_URL)
    session = Session(engine)
    
    try:
        print("Starting to populate stock data...")
        for ticker in POPULAR_TICKERS:
            try:
                print(f"Fetching data for {ticker}...")
                result = stock_service.fetch_stock_data(ticker, session)
                print(f"Successfully added {ticker}: {result}")
                # Sleep to avoid hitting API rate limits
                time.sleep(1)
            except Exception as e:
                print(f"Error processing {ticker}: {str(e)}")
                continue
                
        print("Finished populating stock data!")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)
    finally:
        session.close()

if __name__ == "__main__":
    populate_stocks() 