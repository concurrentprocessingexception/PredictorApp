import React from 'react';
import { Line } from 'react-chartjs-2';

interface Props {
  symbol: string;
  priceDataLength: number;
  forecastData: any;
  formatDateLabel: (d: string) => string;
  horizonColors: Record<number, string>;
}

const ForecastPriceChart: React.FC<Props> = ({
  symbol,
  priceDataLength,
  forecastData,
  formatDateLabel,
  horizonColors,
}) => {
  if (!forecastData) return null;

  const labels = Object.values(forecastData)[0].series.map((p: any) =>
    formatDateLabel(p.date)
  );

  const datasets = Object.entries(forecastData).flatMap(
    ([horizon, data]: any) => [
      {
        label: `Forecast ${horizon}d`,
        data: data.series.map((p: any) => p.price),
        borderColor: horizonColors[Number(horizon)],
        borderDash: [4, 4],
        tension: 0.4,
      },
      {
        label: `Lower ${horizon}d`,
        data: data.series.map((p: any) => p.lower),
        borderColor: 'rgba(239, 68, 68, 0.4)',
        borderDash: [2, 2],
        tension: 0.4,
      },
      {
        label: `Upper ${horizon}d`,
        data: data.series.map((p: any) => p.upper),
        borderColor: 'rgba(34, 197, 94, 0.4)',
        borderDash: [2, 2],
        tension: 0.4,
      },
    ]
  );

  const data = { labels, datasets };

  const options = {
    responsive: true,
    plugins: {
      legend: { position: 'top' as const },
      title: {
        display: true,
        text: `Forecast (${symbol})`,
      },
    },
  };

  return (
    <div className="border rounded p-4 shadow">
      <Line data={data} options={options} />
    </div>
  );
};

export default ForecastPriceChart;