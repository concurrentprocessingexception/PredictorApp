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
import { getForecastDashboard } from '../services/forecastService';
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

const HORIZON_COLORS: Record<number, string> = {
  5: 'rgb(168, 85, 247)',   // purple
  10: 'rgb(249, 115, 22)', // orange
  20: 'rgb(34, 197, 94)',  // green
};

const StockSearch: React.FC = () => {
  const [symbol, setSymbol] = useState('TSLA');
  const [range, setRange] = useState('1m');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const [priceData, setPriceData] = useState<{
    date: string;
    close: number;
  }[]>([]);

  const [forecastData, setForecastData] = useState<any | null>(null);
  const [trust, setTrust] = useState<any | null>(null);
  const [model, setModel] = useState<'baseline' | 'prophet'>('baseline');

  const formatDateLabel = (dateStr: string) => {
    const d = new Date(dateStr);
    return `${String(d.getDate()).padStart(2, '0')}-${String(
      d.getMonth() + 1
    ).padStart(2, '0')}-${d.getFullYear()}`;
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

      const result = await fetchStockHistory(symbol, startDate, endDate);
      setPriceData(result);

      await loadForecastDashboard(symbol);
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
     Chart Data Preparation
     ======================= */

  const historicalLabels = priceData.map(p =>
    formatDateLabel(p.date)
  );

  const forecastLabels =
    forecastData
      ? Object.values(forecastData)[0].series.map((p: any) =>
          formatDateLabel(p.date)
        )
      : [];

  const combinedLabels = [...historicalLabels, ...forecastLabels];

  const forecastDatasets =
  forecastData
    ? Object.entries(forecastData).flatMap(
        ([horizon, data]: any) => [
          {
            label: `Forecast ${horizon}d`,
            data: [
              ...Array(priceData.length).fill(null),
              ...data.series.map((p: any) => p.price),
            ],
            borderColor: HORIZON_COLORS[Number(horizon)],
            borderDash: [4, 4],
            tension: 0.4,
            yAxisID: 'forecast',
          },
          {
            label: `Lower ${horizon}d`,
            data: [
              ...Array(priceData.length).fill(null),
              ...data.series.map((p: any) => p.lower),
            ],
            borderColor: 'rgba(239, 68, 68, 0.4)',
            borderDash: [2, 2],
            tension: 0.4,
            yAxisID: 'forecast',   // 🔑 SAME AXIS
          },
          {
            label: `Upper ${horizon}d`,
            data: [
              ...Array(priceData.length).fill(null),
              ...data.series.map((p: any) => p.upper),
            ],
            borderColor: 'rgba(34, 197, 94, 0.4)',
            borderDash: [2, 2],
            tension: 0.4,
            yAxisID: 'forecast',   // 🔑 SAME AXIS
          },
        ]
      )
    : [];

  const combinedChartData = {
    labels: combinedLabels,
    datasets: [
      {
        label: 'Historical Close',
        data: [
          ...priceData.map(p => p.close),
          ...Array(forecastLabels.length).fill(null),
        ],
        borderColor: 'rgb(59, 130, 246)',
        tension: 0.4,
      },
      ...forecastDatasets,
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
      y: {
        position: 'left',
        title: {
          display: true,
          text: 'Historical Price',
        },
      },
      forecast: {
        position: 'right',
        grid: {
          drawOnChartArea: false,
        },
        title: {
          display: true,
          text: 'Forecast Price',
        },
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

        <select
          className="border p-2 w-full sm:w-40"
          value={model}
          onChange={e => setModel(e.target.value as 'baseline' | 'prophet')}
        >
          <option value="baseline">Baseline</option>
          <option value="prophet">Prophet</option>
        </select>

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

      {/* 📊 Chart */}
      <div className="border rounded p-4 shadow">
        {priceData.length > 0 && (
          <Line
            data={combinedChartData}
            options={combinedChartOptions}
          />
        )}
      </div>

      {/* 📰 News */}
      <NewsPanel searchSymbol={symbol} />
    </div>
  );
};

export default StockSearch;