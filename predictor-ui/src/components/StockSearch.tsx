// StockSearch.tsx

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
import { fetchStockForecast } from '../services/forecastService';
import NewsPanel from './NewsPanel';
import dayjs from 'dayjs';

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
    open: number;
    high: number;
    low: number;
    close: number;
    adj_close: number;
    volume: number;
  }[]>([]);


  const handleSearch = async () => {
    setLoading(true);
    setError('');
    try {
      const selectedRange = ranges.find(r => r.value === range);
      const days = selectedRange?.days || 30;
      const endDate = dayjs().format('YYYY-MM-DD');
      const startDate = dayjs().subtract(days, 'day').format('YYYY-MM-DD');

      const result = await fetchStockHistory(symbol, startDate, endDate);
      setPriceData(result);
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to fetch data');
      setPriceData([]);
    } finally {
      setLoading(false);
    }
  };

  const [forecastData, setForecastData] = useState<{
    date: string;
    prediction: number;
    lower: number;
    upper: number;
  }[]>([]);

  const forecastStockPrice = async () => {
    setForecasting(true);
    setError('');
    try {
      // Call forecast API here and update state with forecast data
      const forecastResult = await fetchStockForecast(symbol, 7, '1d');
      setForecastData(forecastResult);
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

  const formatDateLabel = (dateStr: string) => {
    const d = new Date(dateStr);
    const day = String(d.getDate()).padStart(2, "0");
    const month = String(d.getMonth() + 1).padStart(2, "0");
    const year = d.getFullYear();
    return `${day}-${month}-${year}`;
  };


  const labels = priceData.map((item: any) => formatDateLabel(item.date));

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Close',
        data: priceData.map(p => p.close),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        tension: 0.4
      },
      {
        label: 'High',
        data: priceData.map(p => p.high),
        borderColor: 'rgb(34, 197, 94)',
        borderDash: [5, 5],
        fill: false,
        tension: 0.4
      },
      {
        label: 'Low',
        data: priceData.map(p => p.low),
        borderColor: 'rgb(239, 68, 68)',
        borderDash: [5, 5],
        fill: false,
        tension: 0.4
      },
    ]
  };


  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: {
        display: true,
        text: `Price Trend for ${symbol.toUpperCase()}`
      },
    },
    scales: {
      x: {
        ticks: {
          autoSkip: true,
        }
      }
    }
  };

  const forecastLabels = forecastData.map((item) => formatDateLabel(item.date));

  const forecastChartData = {
    labels: forecastLabels,
    datasets: [
      {
        label: 'Prediction',
        data: forecastData.map(p => p.prediction),
        borderColor: 'rgb(168, 85, 247)',
        backgroundColor: 'rgba(168, 85, 247, 0.2)',
        tension: 0.4
      },
      {
        label: 'Lower Bound',
        data: forecastData.map(p => p.lower),
        borderColor: 'rgb(239, 68, 68)',
        borderDash: [5, 5],
        fill: false,
        tension: 0.4
      },
      {
        label: 'Upper Bound',
        data: forecastData.map(p => p.upper),
        borderColor: 'rgb(34, 197, 94)',
        borderDash: [5, 5],
        fill: false,
        tension: 0.4
      }
    ]
  };

  const forecastChartOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: {
        display: true,
        text: `Forecast for ${symbol.toUpperCase()}`
      },
    },
    scales: {
      x: {
        ticks: {
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
      <div className="flex flex-col lg:flex-row items-stretch gap-6">
        {/* Chart */}
        <div className="w-full lg:w-2/3 border rounded p-4 shadow h-full">
          {priceData.length > 0 && <Line data={chartData} options={chartOptions} />}

          <button
            className="bg-blue-600 text-white px-4 py-2 rounded w-full sm:w-auto"
            onClick={forecastStockPrice} >
            {forecasting ? 'Forecasting...' : 'Forecast'}
          </button>
          {forecastData.length > 0 && <Line data={forecastChartData} options={forecastChartOptions} />}
        </div>

        {/* News */}
        <div className="w-full lg:w-1/3 h-full">
          <NewsPanel searchSymbol={symbol} />
        </div>
      </div>
    </div>
  );
};

export default StockSearch;
