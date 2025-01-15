const RocDisplay = ({ roc }) => {
  // Add null/undefined check
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

export default RocDisplay;