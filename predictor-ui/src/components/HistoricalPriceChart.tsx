import React from 'react';
import { Line } from 'react-chartjs-2';

interface Props {
  symbol: string;
  priceData: { date: string; close: number }[];
  formatDateLabel: (d: string) => string;
}

const HistoricalPriceChart: React.FC<Props> = ({
  symbol,
  priceData,
  formatDateLabel,
}) => {
  const data = {
    labels: priceData.map(p => formatDateLabel(p.date)),
    datasets: [
      {
        label: 'Historical Close',
        data: priceData.map(p => p.close),
        borderColor: 'rgb(59, 130, 246)',
        tension: 0.4,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { position: 'top' as const },
      title: {
        display: true,
        text: `Historical Prices (${symbol})`,
      },
    },
  };

  return (
    <div className="border rounded p-4 shadow">
      <Line data={data} options={options} />
    </div>
  );
};

export default HistoricalPriceChart;