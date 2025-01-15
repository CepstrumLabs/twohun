import React, { useState, useEffect } from 'react';

const StockList = () => {
  const [stocks, setStocks] = useState([]);

  useEffect(() => {
    const fetchStocks = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/stocks');
        const data = await response.json();
        setStocks(data);
      } catch (error) {
        console.error('Error fetching stocks:', error);
      }
    };

    fetchStocks();
  }, []);

  return (
    <div className="stock-list">
      <h2>Stock Moving Averages</h2>
      <table>
        <thead>
          <tr>
            <th>Ticker</th>
            <th>Company Name</th>
            <th>50-Day MA</th>
            <th>200-Day MA</th>
            <th>Date</th>
          </tr>
        </thead>
        <tbody>
          {stocks.map((stock) => (
            <tr key={stock.id}>
              <td>{stock.ticker}</td>
              <td>{stock.company_name}</td>
              <td>${stock.ma_50.toFixed(2)}</td>
              <td>${stock.ma_200.toFixed(2)}</td>
              <td>{new Date(stock.date).toLocaleDateString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default StockList;
