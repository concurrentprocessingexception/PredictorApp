// StockSearch.tsx

import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import dayjs from 'dayjs';

import { fetchStockHistory } from '../services/stockService';
import { fetchStockForecast } from '../services/forecastService';
import NewsPanel from './NewsPanel';

ChartJS.register(
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Title,
  Tooltip,
  Legend
);

const ranges = [
  { label: '1D', value: '1d', days: 1 },
  { label: '1W', value: '1w', days: 7 },
  { label: '1M', value: '1m', days: 30 },
  { label: '6M', value: '6m', days: 180 },
  { label: '1Y', value: '1y', days: 365 },
];

const StockSearch: React.FC = () => {
  const [symbol, setSymbol] = useState('TSLA');
  const [range, setRange] = useState('1m');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [forecasting, setForecasting] = useState(false);

  const [priceData, setPriceData] = useState<{
    date: string;
    close: number;
  }[]>([]);

  const [forecastData, setForecastData] = useState<{
    date: string;
    prediction: number;
    lower: number;
    upper: number;
  }[]>([]);

  const formatDateLabel = (dateStr: string) => {
    const d = new Date(dateStr);
    return `${String(d.getDate()).padStart(2, '0')}-${String(
      d.getMonth() + 1
    ).padStart(2, '0')}-${d.getFullYear()}`;
  };

  const handleSearch = async () => {
    setLoading(true);
    setError('');

    try {
      const selectedRange = ranges.find(r => r.value === range);
      const days = selectedRange?.days ?? 30;

      const endDate = dayjs().format('YYYY-MM-DD');
      const startDate = dayjs().subtract(days, 'day').format('YYYY-MM-DD');

      const result = await fetchStockHistory(symbol, startDate, endDate);
      setPriceData(result);
      setForecastData([]); // reset forecast on new search
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to fetch data');
      setPriceData([]);
    } finally {
      setLoading(false);
    }
  };

  const forecastStockPrice = async () => {
    setForecasting(true);
    setError('');

    try {
      const result = await fetchStockForecast(symbol, 7, '1d');
      setForecastData(result);
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to fetch forecast');
      setForecastData([]);
    } finally {
      setForecasting(false);
    }
  };

  useEffect(() => {
    handleSearch();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [range]);

  /* =======================
     Combined Chart Logic
     ======================= */

  const historicalLabels = priceData.map(p =>
    formatDateLabel(p.date)
  );
  const forecastLabels = forecastData.map(p =>
    formatDateLabel(p.date)
  );

  const combinedLabels = [...historicalLabels, ...forecastLabels];

  const combinedChartData = {
    labels: combinedLabels,
    datasets: [
      {
        label: 'Historical Close',
        data: [
          ...priceData.map(p => p.close),
          ...Array(forecastData.length).fill(null),
        ],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.15)',
        tension: 0.4,
      },
      {
        label: 'Forecast',
        data: [
          ...Array(priceData.length).fill(null),
          ...forecastData.map(p => p.prediction),
        ],
        borderColor: 'rgb(168, 85, 247)',
        borderDash: [2, 4],
        tension: 0.4,
      },
      {
        label: 'Lower Bound',
        data: [
          ...Array(priceData.length).fill(null),
          ...forecastData.map(p => p.lower),
        ],
        borderColor: 'rgb(239, 68, 68)',
        borderDash: [4, 4],
        tension: 0.4,
      },
      {
        label: 'Upper Bound',
        data: [
          ...Array(priceData.length).fill(null),
          ...forecastData.map(p => p.upper),
        ],
        borderColor: 'rgb(34, 197, 94)',
        borderDash: [4, 4],
        tension: 0.4,
      },
    ],
  };

  const combinedChartOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' as const },
      title: {
        display: true,
        text: `Price History & Forecast for ${symbol.toUpperCase()}`,
      },
    },
    scales: {
      x: {
        ticks: { autoSkip: true },
      },
    },
  };

  return (
    <div className="space-y-6">
      {/* 🔍 Search */}
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

        <button
          className="bg-blue-600 text-white px-4 py-2 rounded"
          onClick={handleSearch}
        >
          {loading ? 'Loading...' : 'Search'}
        </button>
      </div>

      {error && <p className="text-red-600 text-sm">{error}</p>}

      {/* 📊 Combined Chart */}
      <div className="border rounded p-4 shadow">
        {priceData.length > 0 && (
          <Line
            data={combinedChartData}
            options={combinedChartOptions}
          />
        )}

        <button
          className="mt-4 bg-blue-600 text-white px-4 py-2 rounded"
          onClick={forecastStockPrice}
        >
          {forecasting ? 'Forecasting...' : 'Forecast'}
        </button>
      </div>

      {/* 📰 News */}
      <NewsPanel searchSymbol={symbol} />
    </div>
  );
};

export default StockSearch;