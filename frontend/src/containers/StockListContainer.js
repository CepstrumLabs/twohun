import { useState, useEffect } from 'react';
import StockList from '../components/StockList';

const StockListContainer = () => {
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchStocks = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/stocks');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setStocks(data);
    } catch (error) {
      console.error('Error fetching stocks:', error);
      // You might want to add error handling UI here
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStocks();
    // Optional: Set up polling to refresh data periodically
    const interval = setInterval(fetchStocks, 5 * 60 * 1000); // Every 5 minutes
    
    return () => clearInterval(interval);
  }, []);

  return <StockList stocks={stocks} loading={loading} />;
};

export default StockListContainer; 