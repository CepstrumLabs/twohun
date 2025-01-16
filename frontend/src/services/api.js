import API_URL from '../config/api';

export const fetchStocks = async () => {
  const response = await fetch(`${API_URL}/api/stocks`);
  return response.json();
}; 