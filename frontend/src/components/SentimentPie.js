import React from "react";
import { Pie } from "react-chartjs-2";

export default function SentimentPie({ counts }) {
  const data = {
    labels: ["Positive", "Negative", "Neutral"],
    datasets: [
      {
        data: [
          counts.Positive || 0,
          counts.Negative || 0,
          counts.Neutral || 0,
        ],
        backgroundColor: ["#10b981", "#ef4444", "#facc15"],
      },
    ],
  };

  return (
    <div className="chart-card">
      <Pie data={data} />
    </div>
  );
}
