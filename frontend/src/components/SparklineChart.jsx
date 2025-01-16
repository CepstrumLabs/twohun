import { Sparklines, SparklinesCurve } from 'react-sparklines';
import { Tooltip } from 'antd';

const SparklineChart = ({ data, color = "#1677ff", height = 30, width = 100 }) => {
  console.log('Sparkline data:', data); // Debug log
  
  if (!data || data.length === 0) {
    return <span>No data</span>;
  }

  const tooltipText = `Shows ROC trend over last ${data.length} days`;
  const stats = `Min: ${Math.min(...data).toFixed(2)}% Max: ${Math.max(...data).toFixed(2)}%`;

  return (
    <Tooltip title={
      <div>
        <div>{tooltipText}</div>
        <div>{stats}</div>
      </div>
    }>
      <div style={{ width: width, height: height }}>
        <Sparklines data={data} width={width} height={height} margin={5}>
          <SparklinesCurve style={{ fill: "none", strokeWidth: 1 }} color={color} />
        </Sparklines>
      </div>
    </Tooltip>
  );
};

export default SparklineChart; 