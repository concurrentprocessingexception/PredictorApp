export type ForecastRunStatus =
  | "queued"
  | "running"
  | "completed"
  | "failed";

export interface ForecastRun {
  run_id: string;
  symbol: string;
  model: string;
  horizon_days: number;
  status: ForecastRunStatus;
  started_at: string;
  completed_at?: string;
  error_message?: string;
}