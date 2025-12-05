import React from "react";
import { PieChart, Pie, Cell, Tooltip, Legend } from "recharts";

export default function SentimentChart({ positive, neutral, negative }) {
  const data = [
    { name: "Positive", value: positive },
    { name: "Neutral", value: neutral },
    { name: "Negative", value: negative }
  ];

  const COLORS = ["#28a745", "#ffc107", "#dc3545"];

  return (
    <PieChart width={350} height={300}>
      <Pie
        data={data}
        cx="50%"
        cy="50%"
        label
        outerRadius={90}
        dataKey="value"
      >
        {data.map((_, i) => (
          <Cell key={i} fill={COLORS[i]} />
        ))}
      </Pie>
      <Tooltip />
      <Legend />
    </PieChart>
  );
}
