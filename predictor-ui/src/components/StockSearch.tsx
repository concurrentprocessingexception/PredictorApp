import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { fetchStockHistory } from '../services/stockService';
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
  { label: '1D', value: '1d' },
  { label: '1W', value: '1w' },
  { label: '1M', value: '1m' },
  { label: '6M', value: '6m' },
  { label: '1Y', value: '1y' },
];

const StockSearch: React.FC = () => {
  const [symbol, setSymbol] = useState('AAPL');
  const [range, setRange] = useState('1d');
  const [priceData, setPriceData] = useState<{ date: string; close: number }[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    setLoading(true);
    setError('');
    try {
      const result = await fetchStockHistory(symbol, range);
      setPriceData(result.data);
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to fetch data');
      setPriceData([]);
    } finally {
      setLoading(false);
    }
  };

  // Auto-fetch on load
  useEffect(() => {
    handleSearch();
  }, [range]);

  const chartData = {
    labels: priceData.map(p => p.date),
    datasets: [
      {
        label: `${symbol.toUpperCase()} (${range.toUpperCase()})`,
        data: priceData.map(p => p.close),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        tension: 0.4
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' as const },
      title: {
        display: true,
        text: `Price Trend for ${symbol.toUpperCase()}`
      },
    },
    scales: {
      x: {
        ticks: {
          maxTicksLimit: 10,
          autoSkip: true,
        }
      }
    }
  };

  return (
    <div>
      {/* 🔍 Search + Range */}
      <div className="mb-6 flex flex-col sm:flex-row gap-4">
        <input
          type="text"
          className="border p-2 w-full sm:w-72"
          placeholder="Enter Symbol (e.g., TSLA)"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value.toUpperCase())}
        />
        <select
          className="border p-2 w-full sm:w-40"
          value={range}
          onChange={(e) => setRange(e.target.value)}
        >
          {ranges.map((r) => (
            <option key={r.value} value={r.value}>{r.label}</option>
          ))}
        </select>
        <button
          className="bg-blue-600 text-white px-4 py-2 rounded w-full sm:w-auto"
          onClick={handleSearch}
        >
          {loading ? 'Loading...' : 'Search'}
        </button>
      </div>

      {error && <p className="text-red-600 text-sm mb-4">{error}</p>}

      {/* 📊 Chart + 📰 News Panel */}
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Chart */}
        <div className="w-full lg:w-2/3 border rounded p-4 shadow">
          {priceData.length > 0 && <Line data={chartData} options={chartOptions} />}
        </div>

        {/* News */}
        <div className="w-full lg:w-1/3">
          <NewsPanel searchSymbol={symbol} />
        </div>
      </div>
    </div>
  );
};

export default StockSearch;
