import axios from 'axios';

const BACKEND_BASE_URL = 'http://localhost:8000';

export const fetchStockHistory = async (symbol: string, range: string) => {
  try {
    const response = await axios.get(`${BACKEND_BASE_URL}/stock/${symbol}`, {
      params: { range }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching stock history:', error);
    throw error;
  }
};
