import React from "react";
import { Line } from "react-chartjs-2";

export default function SentimentLine({ trend }) {
  const labels = trend.map((t) => t.date);
  const pos = trend.map((t) => t.Positive);
  const neg = trend.map((t) => t.Negative);
  const neu = trend.map((t) => t.Neutral);

  const data = {
    labels,
    datasets: [
      { label: "Positive", data: pos, borderColor: "#10b981" },
      { label: "Negative", data: neg, borderColor: "#ef4444" },
      { label: "Neutral", data: neu, borderColor: "#facc15" },
    ],
  };

  const options = {
    responsive: true,
    plugins: { legend: { labels: { color: "var(--text)" } } },
    scales: {
      x: { ticks: { color: "var(--text)" } },
      y: { ticks: { color: "var(--text)" } },
    },
  };

  return (
    <div className="chart-card">
      <Line data={data} options={options} />
    </div>
  );
}
