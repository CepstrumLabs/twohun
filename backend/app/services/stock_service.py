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
        start_date = end_date - timedelta(days=600)  # Need 200 days for MA calculation
        hist = stock.history(start=start_date, end=end_date)
        
        # Get company name once
        company_name = stock.info.get('longName', '')
        
        # Process last n days of data
        recent_data = hist.tail(days)
        
        new_entries = []
        current_data = None  # Initialize outside the loop
        
        # Get the most recent date in our data
        most_recent_date = recent_data.index[-1].date()
        
        for date, row in recent_data.iterrows():
            # Calculate MAs and signals
            ma_50 = hist['Close'].rolling(window=50).mean().loc[date]
            ma_200 = hist['Close'].rolling(window=200).mean().loc[date]
            
            # Get previous day's MAs for crossover detection and ROC
            prev_date = date - pd.Timedelta(days=1)
            if prev_date in hist.index:
                prev_ma_50 = hist['Close'].rolling(window=50).mean().loc[prev_date]
                prev_ma_200 = hist['Close'].rolling(window=200).mean().loc[prev_date]
                
                # Calculate Rate of Change (as percentage)
                roc_50 = ((ma_50 - prev_ma_50) / prev_ma_50) * 100
                roc_200 = ((ma_200 - prev_ma_200) / prev_ma_200) * 100
                
                # Determine signal
                signal = 'NEUTRAL'
                if ma_50 > ma_200 and prev_ma_50 <= prev_ma_200:
                    signal = 'GOLDEN_CROSS'
                elif ma_50 < ma_200 and prev_ma_50 >= prev_ma_200:
                    signal = 'DEATH_CROSS'
                elif ma_50 > ma_200:
                    signal = 'BULLISH'
                elif ma_50 < ma_200:
                    signal = 'BEARISH'
            else:
                signal = 'NEUTRAL'
                roc_50 = 0
                roc_200 = 0
            
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
            
            # Store the most recent day's data
            if date.date() == most_recent_date:
                current_data = {
                    'ticker': ticker,
                    'company_name': company_name,
                    'ma_50': float(ma_50),
                    'ma_200': float(ma_200),
                    'price': float(row['Close']),
                    'date': date.date()
                }
        
        if new_entries:
            session.add_all(new_entries)
            session.commit()
            
        return current_data  # Return only the most recent data
        
    except Exception as e:
        session.rollback()
        raise Exception(f"Error fetching data for {ticker}: {str(e)}")

def get_recent_stock_data(session: Session):
    """
    Retrieve only the most recent stock data from database for each ticker.
    Returns only the latest data point for each stock.
    """
    # Use row_number() window function to get the latest record for each ticker
    stocks = session.query(Stock).from_self().distinct(
        Stock.ticker
    ).order_by(
        Stock.ticker,
        Stock.date.desc()
    ).all()
    
    return stocks 