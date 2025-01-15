import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.stock import Stock

def fetch_stock_data(ticker: str, session: Session, days: int = 7):
    """
    Fetch stock data from Yahoo Finance and store daily entries.
    Returns newly created entries.
    """
    try:
        # Get stock data
        stock = yf.Ticker(ticker)
        
        # Get historical data for calculating MAs
        end_date = datetime.now()
        start_date = end_date - timedelta(days=200)  # Need 200 days for MA calculation
        hist = stock.history(start=start_date, end=end_date)
        
        # Get company name once
        company_name = stock.info.get('longName', '')
        
        # Process last n days of data
        recent_data = hist.tail(days)
        
        new_entries = []
        for date, row in recent_data.iterrows():
            # Calculate MAs for this date using all historical data
            ma_50 = hist['Close'].rolling(window=90).mean().loc[date]
            ma_200 = hist['Close'].rolling(window=300).mean().loc[date]
            
            # Check if entry already exists
            existing = session.query(Stock).filter(
                Stock.ticker == ticker,
                Stock.date == date.date()
            ).first()
            
            if not existing:
                new_entry = Stock(
                    ticker=ticker,
                    company_name=company_name,
                    ma_50=float(ma_50),
                    ma_200=float(ma_200),
                    date=date.date(),
                    price=float(row['Close'])
                )
                new_entries.append(new_entry)
        
        if new_entries:
            session.add_all(new_entries)
            session.commit()
            
        return new_entries
        
    except Exception as e:
        session.rollback()
        raise Exception(f"Error fetching data for {ticker}: {str(e)}")

def get_recent_stock_data(session: Session, days: int = 7):
    """
    Retrieve recent stock data from database.
    Returns data for the specified number of days.
    """
    threshold_date = datetime.now().date() - timedelta(days=days)
    
    stocks = session.query(Stock)\
        .filter(Stock.date >= threshold_date)\
        .order_by(Stock.ticker, Stock.date.desc())\
        .all()
    
    return stocks 