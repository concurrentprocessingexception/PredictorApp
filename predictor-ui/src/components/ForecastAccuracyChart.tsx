import React, { useEffect, useState } from "react";
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Tooltip,
    Legend,
} from "chart.js";
import { Line } from "react-chartjs-2";
import { getForecastEvaluation } from "../services/forecastService";

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Tooltip,
    Legend
);

type ForecastAccuracyPoint = {
    date: string;
    actual_price: number;
    predicted_price: number;
};

type Props = {
    symbol: string;
    model: string;
};

const ForecastAccuracyChart: React.FC<Props> = ({ symbol, model }) => {
    const [dataPoints, setDataPoints] = useState<ForecastAccuracyPoint[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const API_BASE = "http://localhost:8000";

    useEffect(() => {
        const fetchAccuracy = async () => {
            setLoading(true);
            setError(null);

            try {
                const data = await getForecastEvaluation(symbol, model);
                setDataPoints(data);
            } catch (err: any) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchAccuracy();
    }, [symbol, model]);

    if (loading) {
        return <div>Loading forecast evaluation...</div>;
    }

    if (error) {
        return <div>Error: {error}</div>;
    }

    if (dataPoints.length === 0) {
        return <div>No evaluation data available</div>;
    }

    const labels = dataPoints.map((p) => p.date);

    const actualPrices = dataPoints.map((p) => p.actual_price);
    const predictedPrices = dataPoints.map((p) => p.predicted_price);

    const chartData = {
        labels,
        datasets: [
            {
                label: "Actual Price",
                data: actualPrices,
                borderColor: "rgb(75,192,192)",
                backgroundColor: "rgba(75,192,192,0.2)",
                tension: 0.3,
            },
            {
                label: "Predicted Price",
                data: predictedPrices,
                borderColor: "rgb(255,99,132)",
                backgroundColor: "rgba(255,99,132,0.2)",
                tension: 0.3,
                borderDash: [6, 4],
            },
        ],
    };

    const options = {
        responsive: true,
        plugins: {
            legend: {
                position: "top" as const,
            },
            tooltip: {
                mode: "index" as const,
                intersect: false,
            },
        },
        interaction: {
            mode: "index" as const,
            intersect: false,
        },
        scales: {
            y: {
                title: {
                    display: true,
                    text: "Price",
                },
            },
            x: {
                title: {
                    display: true,
                    text: "Date",
                },
            },
        },
    };

    return (
        <div style={{ marginTop: "30px" }}>
            <h3>Forecast vs Actual</h3>
            <Line data={chartData} options={options} />
        </div>
    );
};

export default ForecastAccuracyChart;