import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.stock import Stock
from sqlalchemy import func, and_

def fetch_stock_data(ticker: str, session: Session, days: int = 30):
    """
    Fetch stock data from Yahoo Finance and store daily entries.
    Returns newly created entries.
    """
    try:
        # Get historical data
        hist = yf.download(ticker, period="1y")  # Get 1 year of data for better history
        if hist.empty:
            raise Exception(f"No data found for {ticker}")
        
        company_name = yf.Ticker(ticker).info.get('longName', ticker)
        recent_data = hist.tail(days)  # Get last 30 days
        new_entries = []
        
        # Calculate moving averages for the entire dataset
        hist['MA50'] = hist['Close'].rolling(window=50).mean()
        hist['MA200'] = hist['Close'].rolling(window=200).mean()
        
        # Calculate ROC for the entire dataset
        roc_50_values = []
        roc_200_values = []
        
        # Calculate daily ROC values for the entire year
        for i in range(1, len(hist)):
            today_ma50 = hist['MA50'].iloc[i]
            today_ma200 = hist['MA200'].iloc[i]
            prev_ma50 = hist['MA50'].iloc[i-1]
            prev_ma200 = hist['MA200'].iloc[i-1]
            
            if not (pd.isna(today_ma50) or pd.isna(prev_ma50)):
                roc_50 = ((today_ma50 - prev_ma50) / prev_ma50) * 100
                roc_50_values.append(float(roc_50))
            
            if not (pd.isna(today_ma200) or pd.isna(prev_ma200)):
                roc_200 = ((today_ma200 - prev_ma200) / prev_ma200) * 100
                roc_200_values.append(float(roc_200))
        
        # Process recent data for database entries
        for date, row in recent_data.iterrows():
            ma_50 = hist['MA50'].loc[date]
            ma_200 = hist['MA200'].loc[date]
            
            # Get the most recent ROC values
            current_roc_50 = roc_50_values[-1] if roc_50_values else 0
            current_roc_200 = roc_200_values[-1] if roc_200_values else 0
            
            # Get last 30 days of ROC history
            roc_50_history = roc_50_values[-30:]
            roc_200_history = roc_200_values[-30:]
            
            # Determine signal
            signal = 'NEUTRAL'
            if ma_50 > ma_200:
                if hist['MA50'].shift(1).loc[date] <= hist['MA200'].shift(1).loc[date]:
                    signal = 'GOLDEN_CROSS'
                else:
                    signal = 'BULLISH'
            elif ma_50 < ma_200:
                if hist['MA50'].shift(1).loc[date] >= hist['MA200'].shift(1).loc[date]:
                    signal = 'DEATH_CROSS'
                else:
                    signal = 'BEARISH'
            
            new_entry = Stock(
                ticker=ticker,
                company_name=company_name,
                ma_50=float(ma_50),
                ma_200=float(ma_200),
                date=date.date(),
                price=float(row['Close']),
                roc_50=float(current_roc_50),
                roc_200=float(current_roc_200),
                signal=signal,
                roc_50_history=roc_50_history,
                roc_200_history=roc_200_history
            )
            new_entries.append(new_entry)
        
        # Bulk insert new entries
        if new_entries:
            session.bulk_save_objects(new_entries)
            session.commit()
            return f"Added {len(new_entries)} entries for {ticker}"
        
        return f"No new data for {ticker}"
        
    except Exception as e:
        session.rollback()
        raise Exception(f"Error processing {ticker}: {str(e)}")

def get_recent_stock_data(session: Session):
    """
    Retrieve only the most recent stock data from database for each ticker.
    Returns only the latest data point for each stock, ensuring uniqueness.
    """
    # Subquery to get the latest date for each ticker
    latest_dates = session.query(
        Stock.ticker,
        func.max(Stock.date).label('max_date')
    ).group_by(Stock.ticker).subquery()

    # Join with original table to get full records and ensure uniqueness
    stocks = session.query(Stock).distinct(Stock.ticker).join(
        latest_dates,
        and_(
            Stock.ticker == latest_dates.c.ticker,
            Stock.date == latest_dates.c.max_date
        )
    ).all()
    
    return stocks 