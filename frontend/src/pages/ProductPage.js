import React, { useEffect, useState } from "react";
import { getReviews } from "../api";
import { useParams, useNavigate } from "react-router-dom";
import { PieChart, Pie, Cell, Tooltip, Legend } from "recharts";
import { vaderSentiment } from "../utils/vader";

export default function ProductPage() {
  const { name } = useParams();
  const productName = decodeURIComponent(name);
  const navigate = useNavigate();

  const [reviews, setReviews] = useState([]);
  const [sentiment, setSentiment] = useState({ pos: 0, neu: 0, neg: 0 });

  useEffect(() => {
    (async () => {
      const r = await getReviews(productName);
      setReviews(r);

      let pos = 0, neu = 0, neg = 0;

      r.forEach(item => {
        const s = vaderSentiment(item.review_text);

        if (s === "positive") pos++;
        else if (s === "neutral") neu++;
        else neg++;
      });

      setSentiment({ pos, neu, neg });
    })();
  }, [productName]);

  const chartData = [
    { name: "Positive", value: sentiment.pos },
    { name: "Neutral", value: sentiment.neu },
    { name: "Negative", value: sentiment.neg }
  ];

  const COLORS = ["#28a745", "#ffc107", "#dc3545"];

  return (
    <div className="container py-4">

      <button className="btn btn-outline-secondary mb-3" onClick={() => navigate(-1)}>
        ⬅ Back
      </button>

      <div className="d-flex justify-content-between align-items-center">
        <div>
          <h2 className="fw-bold">{productName}</h2>
          <p className="text-muted">Total Reviews: {reviews.length}</p>
        </div>

        <button
          className="btn btn-primary"
          onClick={() => navigate(`/analytics/${encodeURIComponent(productName)}`)}
        >
          📊 View Analytics
        </button>
      </div>

      <h4 className="mt-3">Sentiment Breakdown</h4>

      <PieChart width={350} height={300}>
        <Pie data={chartData} dataKey="value" outerRadius={100} label>
          {chartData.map((entry, i) => (
            <Cell key={i} fill={COLORS[i]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>

      <h4 className="mt-4">Reviews</h4>
      {reviews.map((r) => (
        <div key={r.review_id} className="card my-3">
          <div className="card-body">
            <h6 className="fw-bold">{r.reviewer}</h6>
            <p className="text-muted">{r.date}</p>
            <p>{r.review_text}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
