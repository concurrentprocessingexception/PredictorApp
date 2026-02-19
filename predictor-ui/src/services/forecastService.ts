import axios from "axios";

const API_BASE = "http://localhost:8000";

export interface ForecastPoint {
  date: string;
  prediction: number;
  lower: number;
  upper: number;
}

export async function fetchStockForecast(
  symbol: string,
  horizon: number = 30,
  interval: string = "1d"
): Promise<ForecastPoint[]> {
  const response = await axios.get(
    `${API_BASE}/forecast/${symbol}`,
    {
      params: { horizon, interval }
    }
  );
  return response.data.forecast;
}
