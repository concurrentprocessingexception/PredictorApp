import axios from "axios";

const API_BASE = "http://localhost:8000";

/* =========================
   Types (UI-facing only)
   ========================= */

export interface ForecastSeriesPoint {
  date: string;
  price: number;
  lower?: number;
  upper?: number;
}

export interface HorizonForecast {
  series: ForecastSeriesPoint[];
}

export interface ForecastDashboardResponse {
  symbol: string;
  horizons: number[];
  forecasts: {
    [horizon: number]: HorizonForecast;
  };
  trust: {
    agreement: "STRONG" | "MODERATE" | "WEAK";
    per_horizon: {
      [horizon: number]: {
        direction: "UP" | "DOWN" | "FLAT";
        avg_band_width: number;
      };
    };
  };
}

/* =========================
   API Call
   ========================= */

export async function getForecastDashboard(
  symbol: string
): Promise<ForecastDashboardResponse> {
  const response = await axios.get(
    `${API_BASE}/forecast/dashboard/${symbol}`
  );
  return response.data;
}