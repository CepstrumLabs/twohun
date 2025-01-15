from sqlalchemy import Column, Integer, String, Float, Date, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Stock(Base):
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True)
    company_name = Column(String)
    ma_50 = Column(Float)
    ma_200 = Column(Float)
    date = Column(Date)
    price = Column(Float)
    roc_50 = Column(Float)
    roc_200 = Column(Float)
    signal = Column(String)

    # Create composite index for ticker and date
    __table_args__ = (
        Index('ix_stocks_ticker_date', 'ticker', 'date', unique=True),
    )
