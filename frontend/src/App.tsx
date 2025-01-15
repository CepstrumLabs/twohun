import React from 'react';
import { ConfigProvider, Button } from 'antd';
import theme from './theme/themeConfig';

const App: React.FC = () => {
  return (
    <ConfigProvider theme={theme}>
      <div style={{ padding: '20px' }}>
        <Button type="primary">Test Button</Button>
      </div>
    </ConfigProvider>
  );
}

export default App; 