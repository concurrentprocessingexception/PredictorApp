import axios from "axios";

const API_BASE = "http://localhost:8000";

export const getForecastHistory = async (
  symbol: string,
  model: string,
  horizon?: number
) => {

  const res = await axios.get(
    `${API_BASE}/forecast/history/${symbol}`,
    {
      params: {
        model: model,
        horizon: horizon,
      },
    }
  );

  return res.data;
};