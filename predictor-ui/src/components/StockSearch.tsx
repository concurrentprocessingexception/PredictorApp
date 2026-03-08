import React, { useEffect, useState } from 'react';
import dayjs from 'dayjs';

import { fetchStockHistory } from '../services/stockService';
import { getForecastDashboard } from '../services/forecastService';

import HistoricalPriceChart from './HistoricalPriceChart';
import ForecastPriceChart from './ForecastPriceChart';
import NewsPanel from './NewsPanel';
import ForecastAccuracyChart from './ForecastAccuracyChart';

const ranges = [
  { label: '1D', value: '1d', days: 1 },
  { label: '1W', value: '1w', days: 7 },
  { label: '1M', value: '1m', days: 30 },
  { label: '6M', value: '6m', days: 180 },
  { label: '1Y', value: '1y', days: 365 },
];

const HORIZON_COLORS: Record<number, string> = {
  5: 'rgb(168, 85, 247)',   // purple
  10: 'rgb(249, 115, 22)', // orange
  20: 'rgb(34, 197, 94)',  // green
};

const StockSearch: React.FC = () => {
  const [symbol, setSymbol] = useState('TSLA');
  const [range, setRange] = useState('1m');
  const [model, setModel] = useState<'baseline' | 'prophet'>('baseline');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [priceData, setPriceData] = useState<
    { date: string; close: number }[]
  >([]);

  const [forecastData, setForecastData] = useState<any | null>(null);
  const [trust, setTrust] = useState<any | null>(null);
  const [recommendedModel, setRecommendedModel] = useState<string | null>(null);
  const [modelComparisonStatus, setModelComparisonStatus] = useState<string | null>(null);

  /* =======================
     Helpers
     ======================= */

  const formatDateLabel = (dateStr: string) => {
    const d = new Date(dateStr);
    return `${String(d.getDate()).padStart(2, '0')}-${String(
      d.getMonth() + 1
    ).padStart(2, '0')}-${d.getFullYear()}`;
  };

  /* =======================
     Data Loaders
     ======================= */

  const loadModelRecommendation = async (sym: string) => {
    try {
      // We use the shortest horizon (5d) as canonical
      const res = await fetch(
        `/models/compare?symbol=${sym}&horizon_days=5`
      );
      const data = await res.json();

      setModelComparisonStatus(data.status);
      setRecommendedModel(data.recommended_model);
    } catch {
      setModelComparisonStatus(null);
      setRecommendedModel(null);
    }
  };

  const loadForecastDashboard = async (sym: string) => {
    try {
      const data = await getForecastDashboard(sym, model);
      setForecastData(data.forecasts);
      setTrust(data.trust);
    } catch {
      setForecastData(null);
      setTrust(null);
    }
  };

  const handleSearch = async () => {
    setLoading(true);
    setError('');

    try {
      const selectedRange = ranges.find(r => r.value === range);
      const days = selectedRange?.days ?? 30;

      const endDate = dayjs().format('YYYY-MM-DD');
      const startDate = dayjs().subtract(days, 'day').format('YYYY-MM-DD');

      const history = await fetchStockHistory(symbol, startDate, endDate);
      setPriceData(history);

      await loadForecastDashboard(symbol);
      await loadModelRecommendation(symbol);
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to fetch data');
      setPriceData([]);
      setForecastData(null);
      setTrust(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleSearch();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [range, model]);

  /* =======================
     Render
     ======================= */

  return (
    <div className="space-y-6">
      {/* 🔍 Search / Controls */}
      <div className="flex flex-col sm:flex-row gap-4">
        <input
          type="text"
          className="border p-2 w-full sm:w-72"
          placeholder="Enter Symbol (e.g., TSLA)"
          value={symbol}
          onChange={e => setSymbol(e.target.value.toUpperCase())}
        />

        <select
          className="border p-2 w-full sm:w-40"
          value={range}
          onChange={e => setRange(e.target.value)}
        >
          {ranges.map(r => (
            <option key={r.value} value={r.value}>
              {r.label}
            </option>
          ))}
        </select>

        <select
          className="border p-2 w-full sm:w-40"
          value={model}
          onChange={e =>
            setModel(e.target.value as 'baseline' | 'prophet')
          }
        >
          <option value="baseline">Baseline</option>
          <option value="prophet">Prophet</option>
        </select>

        {recommendedModel && modelComparisonStatus === 'OK' && (
          <div className="flex items-center gap-2 text-sm mt-1">
            <span className="text-gray-600">Recommended model:</span>

            <span
              className={`px-2 py-0.5 rounded font-semibold ${
                recommendedModel === model
                  ? 'bg-green-100 text-green-800'
                  : 'bg-yellow-100 text-yellow-800'
              }`}
            >
              {recommendedModel.toUpperCase()}
            </span>

            {recommendedModel !== model && (
              <span className="text-xs text-gray-500">
                (based on recent accuracy)
              </span>
            )}
          </div>
        )}

        <button
          className="bg-blue-600 text-white px-4 py-2 rounded"
          onClick={handleSearch}
        >
          {loading ? 'Loading...' : 'Search'}
        </button>
      </div>

      {error && <p className="text-red-600 text-sm">{error}</p>}

      {/* 📊 Trust Indicator */}
      {trust && (
        <div className="text-center">
          <span
            className={`px-3 py-1 rounded text-white font-semibold ${
              trust.agreement === 'STRONG'
                ? 'bg-green-600'
                : trust.agreement === 'MODERATE'
                ? 'bg-yellow-500'
                : 'bg-red-600'
            }`}
          >
            Forecast Confidence: {trust.agreement}
          </span>
        </div>
      )}

      {/* 📈 Charts */}
      {priceData.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <HistoricalPriceChart
            key={`hist-${symbol}-${range}`}
            symbol={symbol}
            priceData={priceData}
            formatDateLabel={formatDateLabel}
          />

          <ForecastPriceChart
            key={`forecast-${symbol}-${model}`}
            symbol={symbol}
            priceDataLength={priceData.length}
            forecastData={forecastData}
            formatDateLabel={formatDateLabel}
            horizonColors={HORIZON_COLORS}
          />
        </div>
      )}

      {/* 📉 Forecast Accuracy */}
      {priceData.length > 0 && (
        <div className="bg-white p-4 rounded shadow">
          <ForecastAccuracyChart symbol={symbol} model={model} />
        </div>
      )}

      {/* 📰 News */}
      <NewsPanel searchSymbol={symbol} />
    </div>
  );
};

export default StockSearch;