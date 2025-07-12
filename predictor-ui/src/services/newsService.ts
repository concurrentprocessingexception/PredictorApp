import axios from 'axios';

const BACKEND_BASE_URL = 'http://localhost:8000';

export const fetchNews = async (symbol: string) => {
  try {
    const response = await axios.get(`${BACKEND_BASE_URL}/news/${symbol}`);
    return response.data; // already includes sentiment and top 10
  } catch (error) {
    console.error('Error fetching news from backend:', error);
    return [];
  }
};
