import axios from 'axios';

export const fetchStockHistory = async (symbol: string, startDate: string, endDate: string) => {
  const response = await axios.get(`http://localhost:8000/stocks/history/${symbol}`, {
    params: {
      start_date: startDate,
      end_date: endDate
    }
  });

  return response.data;
};
