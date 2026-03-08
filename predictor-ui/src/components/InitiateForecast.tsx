import React, { useEffect, useState } from "react";
import {
  initiateStockForecasting,
  fetchForecastRuns,
} from "../services/initiateForecasting";
import type { ForecastRun } from "../types/forecast";

const InitiateForecast: React.FC = () => {
  const [symbol, setSymbol] = useState("TSLA");
  const [model, setModel] = useState("prophet");
  const [horizon, setHorizon] = useState(5);

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const [runs, setRuns] = useState<ForecastRun[]>([]);
  const [loadingRuns, setLoadingRuns] = useState(true);

  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");

  /* =========================
     Load previous forecast runs
     ========================= */
  const loadRuns = async () => {
    try {
      setLoadingRuns(true);
      const data = await fetchForecastRuns(20);
      setRuns(data);
    } catch (err) {
      console.error("Failed to load forecast runs", err);
    } finally {
      setLoadingRuns(false);
    }
  };

  useEffect(() => {
    loadRuns();
  }, []);

  /* =========================
     Initiate forecast
     ========================= */
  const handleSubmit = async () => {
    if (!symbol) {
      setMessage("Please enter a symbol");
      return;
    }

    try {
      setLoading(true);
      setMessage(null);

      await initiateStockForecasting({
        symbol,
        model,
        horizon,
        from_date: fromDate || undefined,
        to_date: toDate || undefined,
      });

      setMessage("✅ Forecast initiated successfully");

      // Reload runs so newly queued run appears
      await loadRuns();
    } catch (err: any) {
      setMessage(
        err?.response?.data?.detail || "❌ Failed to initiate forecast"
      );
    } finally {
      setLoading(false);
    }
  };

  /* =========================
     Status badge styling
     ========================= */
  const statusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-100 text-green-800";
      case "running":
        return "bg-blue-100 text-blue-800";
      case "queued":
        return "bg-yellow-100 text-yellow-800";
      case "failed":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <div className="max-w-4xl">
      <h1 className="text-2xl font-bold mb-6">Initiate Forecast</h1>

      {/* =========================
          Initiate Forecast Form
         ========================= */}
      <div className="max-w-xl">
        {/* Symbol */}
        <div className="mb-4">
          <label className="block font-medium mb-1">Symbol</label>
          <input
            className="border rounded px-3 py-2 w-full"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
          />
        </div>

        {/* Model */}
        <div className="mb-6">
          <label className="block font-medium mb-1">Model</label>
          <select
            className="border rounded px-3 py-2 w-full"
            value={model}
            onChange={(e) => setModel(e.target.value)}
          >
            <option value="prophet">Prophet</option>
            <option value="baseline">Baseline</option>
          </select>
        </div>

        {/* Horizon */}
        <div className="mb-4">
          <label className="block font-medium mb-1">Horizon</label>
          <select
            className="border rounded px-3 py-2 w-full"
            value={horizon}
            onChange={(e) => setHorizon(parseInt(e.target.value) || 5)}
          >
            <option value="5">5 Trading Days</option>
            <option value="10">10 Trading Days</option>
            <option value="20">20 Trading Days</option>
          </select>

        </div>

        {/* From Date */}
        <div className="mb-4">
          <label className="block font-medium mb-1">From Date (optional)</label>
          <input
            type="date"
            className="border rounded px-3 py-2 w-full"
            value={fromDate}
            onChange={(e) => setFromDate(e.target.value)}
          />
        </div>

        {/* To Date */}
        <div className="mb-6">
          <label className="block font-medium mb-1">To Date (optional)</label>
          <input
            type="date"
            className="border rounded px-3 py-2 w-full"
            value={toDate}
            onChange={(e) => setToDate(e.target.value)}
          />
        </div>

        <button
            type="button"
            onClick={handleSubmit}
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-2 rounded disabled:opacity-50"
        >
          {loading ? "Running..." : "Initiate Forecast"}
        </button>

        {message && <div className="mt-4 text-sm">{message}</div>}
      </div>

      {/* =========================
          Recent Forecast Runs
         ========================= */}
      <h2 className="text-xl font-semibold mt-10 mb-4">
        Recent Forecast Runs
      </h2>

      {loadingRuns ? (
        <div>Loading runs...</div>
      ) : (
        <table className="w-full border text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="p-2 text-left">Symbol</th>
              <th className="p-2 text-center">Model</th>
              <th className="p-2 text-center">Horizon</th>
              <th className="p-2 text-center">Status</th>
              <th className="p-2 text-center">Started</th>
              <th className="p-2 text-center">Action</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((run) => (
              <tr key={run.run_id} className="border-t">
                <td className="p-2 font-medium">{run.symbol}</td>
                <td className="p-2 text-center">{run.model}</td>
                <td className="p-2 text-center">
                  {run.horizon_days} TD
                </td>
                <td className="p-2 text-center">
                  <span
                    className={`px-2 py-1 rounded ${statusColor(run.status)}`}
                  >
                    {run.status}
                  </span>
                </td>
                <td className="p-2 text-center">
                  {new Date(run.started_at).toLocaleString()}
                </td>
                <td className="p-2 text-center">
                  {run.status === "completed" && (
                    <a
                      href={`/forecast?symbol=${run.symbol}`}
                      className="text-blue-600 underline"
                    >
                      View
                    </a>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default InitiateForecast;