import axios from "axios";
import type { ForecastRun } from "../types/forecast";

export interface InitiateForecastRequest {
  symbol: string;
  model: string;
  horizon: number;
  from_date?: string;
  to_date?: string;
}

export interface InitiateForecastResponse {
  symbol: string;
  model: string;
  horizons: number[];
  runs: {
    run_id: number;
    horizon_days: number;
    status: string;
  }[];
}

export const initiateStockForecasting = async (
  request: InitiateForecastRequest
): Promise<InitiateForecastResponse> => {
  const response = await axios.post(
    "http://localhost:8000/forecasting/run",
    request
  );
  return response.data;
};

export const fetchForecastRuns = async (
  limit = 20
): Promise<ForecastRun[]> => {
  const res = await axios.get("http://localhost:8000/forecasting/runs", {
    params: { limit },
  });
  return res.data as ForecastRun[];
};