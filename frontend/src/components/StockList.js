import { Table, Typography, Card } from 'antd';
import SparklineChart from './SparklineChart';
const { Text, Title } = Typography;

const StockList = ({ stocks, loading }) => {
  const lastUpdated = stocks?.[0]?.date;

  // Format the date nicely
  const formattedDate = lastUpdated ? new Date(lastUpdated).toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }) : 'Not available';

  const RocDisplay = ({ roc }) => {
    if (roc === null || roc === undefined) {
      return <span>N/A</span>;
    }

    const value = parseFloat(roc);
    const isPositive = value > 0;
    const color = isPositive ? 'green' : value < 0 ? 'red' : 'gray';

    return (
      <span style={{ color }}>
        {isPositive ? '+' : ''}{value.toFixed(2)}%
      </span>
    );
  };

  const columns = [
    {
      title: 'Ticker',
      dataIndex: 'ticker',
      key: 'ticker',
      render: (text) => <Text strong>{text}</Text>,
    },
    {
      title: 'Company',
      dataIndex: 'company_name',
      key: 'company_name',
    },
    {
      title: 'Price',
      dataIndex: 'price',
      key: 'price',
      render: (value) => <Text>$ {value?.toFixed(2)}</Text>,
    },
    {
      title: '50 MA',
      dataIndex: 'ma_50',
      key: 'ma_50',
      render: (value) => <Text>$ {value?.toFixed(2)}</Text>,
    },
    {
      title: '50 MA ROC',
      dataIndex: 'roc_50',
      key: 'roc_50',
      render: (value, record) => (
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <RocDisplay roc={value ?? null} />
          <SparklineChart 
            data={record.roc_50_history} 
            color={value > 0 ? 'green' : 'red'} 
          />
        </div>
      ),
      sorter: (a, b) => a.roc_50 - b.roc_50,
    },
    {
      title: '200 MA',
      dataIndex: 'ma_200',
      key: 'ma_200',
      render: (value) => <Text>$ {value?.toFixed(2)}</Text>,
    },
    {
      title: '200 MA ROC',
      dataIndex: 'roc_200',
      key: 'roc_200',
      render: (value, record) => (
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <RocDisplay roc={value ?? null} />
          <SparklineChart 
            data={record.roc_200_history} 
            color={value > 0 ? 'green' : 'red'} 
          />
        </div>
      ),
      sorter: (a, b) => a.roc_200 - b.roc_200,
    },
    {
      title: 'Signal',
      dataIndex: 'signal',
      key: 'signal',
      render: (signal) => {
        let color = 'default';
        switch (signal) {
          case 'GOLDEN_CROSS':
          case 'BULLISH':
            color = '#52c41a';
            break;
          case 'DEATH_CROSS':
          case 'BEARISH':
            color = '#f5222d';
            break;
          default:
            color = '#8c8c8c';
        }
        return <Text strong style={{ color }}>{signal}</Text>;
      },
      filters: [
        { text: 'Golden Cross', value: 'GOLDEN_CROSS' },
        { text: 'Death Cross', value: 'DEATH_CROSS' },
        { text: 'Bullish', value: 'BULLISH' },
        { text: 'Bearish', value: 'BEARISH' },
        { text: 'Neutral', value: 'NEUTRAL' },
      ],
      onFilter: (value, record) => record.signal === value,
    },
  ];

  return (
    <Card>
      <Title level={2}>Stock Market Analysis</Title>
      <Text type="secondary" style={{ display: 'block', marginBottom: '20px' }}>
        Last Updated: {lastUpdated}
      </Text>
      <Table 
        columns={columns} 
        dataSource={stocks} 
        loading={loading}
        rowKey="ticker"
        pagination={false}
      />
    </Card>
  );
};

export default StockList;
