import React from "react";
import { Bar } from "react-chartjs-2";

export default function WordBar({ words }) {
  const labels = words.map((w) => w[0]);
  const counts = words.map((w) => w[1]);

  const data = {
    labels,
    datasets: [
      {
        label: "Word Frequency",
        data: counts,
        backgroundColor: "rgba(37, 99, 235, 0.7)",
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: {
      x: { ticks: { color: "var(--text)" } },
      y: { ticks: { color: "var(--text)" } },
    },
  };

  return (
    <div className="chart-card" style={{ width: "48%" }}>
      <Bar data={data} options={options} />
    </div>
  );
}
