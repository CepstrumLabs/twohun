import React, { useEffect, useState } from 'react';
import { Table, Space, message } from 'antd';

function StockList({ stocks }) {
  const [stockData, setStockData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStocks = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/stocks');
        if (!response.ok) {
          throw new Error('Failed to fetch stocks');
        }
        const data = await response.json();
        setStockData(data);
      } catch (error) {
        console.error('Error fetching stocks:', error);
        message.error('Failed to load stocks');
      } finally {
        setLoading(false);
      }
    };

    fetchStocks();
  }, []);

  const columns = [
    {
      title: 'Ticker',
      dataIndex: 'ticker',
      key: 'ticker',
    },
    {
      title: 'Company Name',
      dataIndex: 'company_name',
      key: 'company_name',
    },
    {
      title: 'Price',
      dataIndex: 'price',
      key: 'price',
      render: (price) => `$${price.toFixed(2)}`,
    },
    {
      title: 'MA 50',
      dataIndex: 'ma_50',
      key: 'ma_50',
      render: (ma) => ma?.toFixed(2) || 'N/A',
    },
    {
      title: 'MA 200',
      dataIndex: 'ma_200',
      key: 'ma_200',
      render: (ma) => ma?.toFixed(2) || 'N/A',
    },
    {
      title: 'Date',
      dataIndex: 'date',
      key: 'date',
    },
  ];

  return (
    <Table 
      dataSource={stockData} 
      columns={columns} 
      rowKey="id"
      pagination={{ pageSize: 10 }}
      loading={loading}
    />
  );
}

export default StockList;
