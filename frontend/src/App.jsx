import { useState, useEffect } from 'react';
import StockListContainer from './containers/StockListContainer';

function App() {
  const [currentDate, setCurrentDate] = useState('');

  useEffect(() => {
    const date = new Date();
    const formattedDate = date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
    setCurrentDate(formattedDate);
  }, []);

  return (
    <div>
      <h1>TwoHun</h1>
      <h3>{currentDate}</h3>
      <StockListContainer />
    </div>
  );
}

export default App;
