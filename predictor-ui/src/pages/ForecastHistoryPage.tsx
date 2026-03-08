import React, { useEffect, useState } from "react";
import { getForecastHistory } from "../services/forecastHistoryService";

type ForecastHistoryRow = {
  run_date: string;
  forecast_date: string;
  predicted_price: number;
  horizon_days: number;
};

const ForecastHistoryPage: React.FC = () => {
  const [symbol, setSymbol] = useState("TSLA");
  const [model, setModel] = useState("prophet");
  const [horizon, setHorizon] = useState<number | "all">("all");

  const [data, setData] = useState<ForecastHistoryRow[]>([]);
  const [loading, setLoading] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);

      const res = await getForecastHistory(
        symbol,
        model,
        horizon === "all" ? undefined : horizon
      );

      setData(res);
    } catch (err) {
      console.error("Failed to load forecast history", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [symbol, model, horizon]);

  return (
    <div className="p-6">

      <h2 className="text-xl font-bold mb-4">
        Forecast History (Last 30 Days)
      </h2>

      {/* Filters */}
      <div className="flex gap-3 mb-4">

        <input
          value={symbol}
          onChange={(e) => setSymbol(e.target.value.toUpperCase())}
          className="border p-2"
          placeholder="Symbol"
        />

        <select
          value={model}
          onChange={(e) => setModel(e.target.value)}
          className="border p-2"
        >
          <option value="baseline">Baseline</option>
          <option value="prophet">Prophet</option>
        </select>

        <select
          className="border p-2"
          value={horizon}
          onChange={(e) =>
            setHorizon(e.target.value === "all" ? "all" : Number(e.target.value))
          }
        >
          <option value="all">All Horizons</option>
          <option value="5">5 Day</option>
          <option value="10">10 Day</option>
          <option value="20">20 Day</option>
        </select>

        <button
          onClick={loadData}
          className="bg-blue-600 text-white px-4 py-2 rounded"
        >
          Reload
        </button>

      </div>

      {/* Table */}
      {loading ? (
        <div>Loading forecast history...</div>
      ) : (
        <table className="w-full border text-sm">

          <thead className="bg-gray-50">
            <tr>
              <th className="p-2 text-center">Run Date</th>
              <th className="p-2 text-center">Forecast Date</th>
              <th className="p-2 text-center">Horizon</th>
              <th className="p-2 text-center">Predicted Price</th>
            </tr>
          </thead>

          <tbody>
            {data.map((row, i) => (
              <tr key={i} className="border-t">
                <td className="p-2 text-center">{row.run_date}</td>
                <td className="p-2 text-center">{row.forecast_date}</td>
                <td className="p-2 text-center">{row.horizon_days}D</td>
                <td className="p-2 text-center">{row.predicted_price}</td>
              </tr>
            ))}
          </tbody>

        </table>
      )}

    </div>
  );
};

export default ForecastHistoryPage;