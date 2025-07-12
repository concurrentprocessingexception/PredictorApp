import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Loader2, ChevronDown, ChevronRight } from 'lucide-react';

const UploadPanel: React.FC = () => {
  const [symbol, setSymbol] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [interval, setInterval] = useState('1d');
  const [message, setMessage] = useState('');
  const [status, setStatus] = useState<'success' | 'error' | ''>('');
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false); // collapsed by default

  useEffect(() => {
    const today = new Date();
    const priorDate = new Date();
    priorDate.setDate(today.getDate() - 30);

    const format = (d: Date) => d.toISOString().split('T')[0];
    setStartDate(format(priorDate));
    setEndDate(format(today));
  }, []);

  const handleSubmit = async () => {
    setMessage('');
    setStatus('');
    setLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/fetch-historical', {
        symbol,
        start_date: startDate,
        end_date: endDate,
        interval: interval,
      });

      setStatus('success');
      setMessage(`✅ Inserted: ${response.data.inserted}, Skipped: ${response.data.skipped}`);
    } catch (error: any) {
      setStatus('error');
      setMessage(error?.response?.data?.detail || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 border rounded shadow mt-6 bg-white w-fit max-w-full">
      <div
        className="flex items-center justify-between cursor-pointer"
        onClick={() => setOpen(!open)}
      >
        <h2 className="text-lg font-semibold">📥 Fetch Historical Stock Data</h2>
        {open ? <ChevronDown /> : <ChevronRight />}
      </div>

      {open && (
        <div className="mt-4 flex flex-col gap-4">
          <div className="flex flex-wrap gap-4 items-end">
            <input
              type="text"
              placeholder="Stock symbol (e.g., AAPL)"
              className="border px-3 py-2 rounded w-40"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
            />

            <div className="flex flex-col">
              <label className="text-sm mb-1">Start Date</label>
              <input
                type="date"
                className="border px-3 py-2 rounded w-40"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>

            <div className="flex flex-col">
              <label className="text-sm mb-1">End Date</label>
              <input
                type="date"
                className="border px-3 py-2 rounded w-40"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>

            <div className="flex flex-col">
              <label className="text-sm mb-1">Interval</label>
              <select
                className="border px-3 py-2 rounded w-40"
                value={interval}
                onChange={(e) => setInterval(e.target.value)}
              >
                <option value="1d">1 Day</option>
                <option value="1h">1 Hour</option>
                <option value="1wk">1 Week</option>
                <option value="1m">1 Minute (7 days max)</option>
              </select>
            </div>

            <button
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-2"
              onClick={handleSubmit}
              disabled={!symbol || !startDate || !endDate || loading}
            >
              {loading && <Loader2 className="animate-spin w-4 h-4" />}
              Fetch & Store Data
            </button>
          </div>

          {message && (
            <div
              className={`font-medium ${
                status === 'success' ? 'text-green-700' : 'text-red-600'
              }`}
            >
              {message}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default UploadPanel;
