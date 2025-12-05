// --- SAME IMPORTS ---
import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getProducts, getReviews } from "../api";

import {
  PieChart, Pie, Cell, Tooltip, Legend,
  BarChart, Bar, XAxis, YAxis,
  LineChart, Line,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis
} from "recharts";

import { vaderSentiment } from "../utils/vader";

const COLORS = ["#28a745", "#ffc107", "#dc3545"];

export default function Analytics() {
  const { name } = useParams();
  const navigate = useNavigate();

  const productName = name ? decodeURIComponent(name) : null;
  const isProductMode = Boolean(productName);

  const [reviews, setReviews] = useState([]);
  const [allReviews, setAllReviews] = useState([]);
  const [productList, setProductList] = useState([]);
  const [loading, setLoading] = useState(true);

  // -------------------------------------------------------------
  // DATA FETCH
  // -------------------------------------------------------------
  useEffect(() => {
    (async () => {
      setLoading(true);

      const products = await getProducts();
      setProductList(products);

      if (isProductMode) {
        const r = await getReviews(productName);
        setReviews(r || []);
      } else {
        const all = [];
        for (const p of products) {
          const r = await getReviews(p);
          if (Array.isArray(r)) all.push(...r);
        }
        setAllReviews(all);
      }

      setLoading(false);
    })();
  }, [productName, isProductMode]);

  if (loading) return <div className="text-center p-5">Loading analytics…</div>;

  // -------------------------------------------------------------
  // PRODUCT ANALYTICS
  // -------------------------------------------------------------
  if (isProductMode) {
    let pos = 0, neu = 0, neg = 0;
    const ratingCount = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };
    const trend = [];

    reviews.forEach((r, i) => {
      const s = vaderSentiment(r.review_text);

      if (s === "positive") pos++;
      else if (s === "neutral") neu++;
      else neg++;

      ratingCount[r.rating]++;

      trend.push({
        index: i + 1,
        sentiment: s === "positive" ? 3 : s === "neutral" ? 2 : 1
      });
    });

    const sentimentData = [
      { name: "Positive", value: pos },
      { name: "Neutral", value: neu },
      { name: "Negative", value: neg },
    ];

    const ratingData = Object.entries(ratingCount).map(([rating, count]) => ({
      rating,
      count
    }));

    return (
      <div className="container py-4">

        <button className="btn btn-outline-secondary mb-3" onClick={() => navigate(-1)}>
          ⬅ Back
        </button>

        <h2 className="fw-bold mb-1">📊 Analytics for: {productName}</h2>
        <p className="text-muted mb-4">Total reviews: {reviews.length}</p>

        <div className="row g-4">

          {/* SENTIMENT PIE */}
          <div className="col-md-6">
            <div className="chart-box">
              <h5 className="text-center">Sentiment Breakdown</h5>
              <PieChart width={360} height={260}>
                <Pie data={sentimentData} dataKey="value" outerRadius={110}>
                  {sentimentData.map((e, i) => (
                    <Cell key={i} fill={COLORS[i]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </div>
          </div>

          {/* RATING BARS */}
          <div className="col-md-6">
            <div className="chart-box">
              <h5 className="text-center">Rating Distribution</h5>
              <BarChart width={360} height={260} data={ratingData}>
                <XAxis dataKey="rating" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#0d6efd" />
              </BarChart>
            </div>
          </div>

          {/* TREND */}
          <div className="col-md-6">
            <div className="chart-box">
              <h5 className="text-center">Sentiment Trend</h5>
              <LineChart width={360} height={260} data={trend}>
                <XAxis dataKey="index" />
                <YAxis domain={[0, 4]} />
                <Tooltip />
                <Line type="monotone" dataKey="sentiment" stroke="#6610f2" strokeWidth={3} />
              </LineChart>
            </div>
          </div>

          {/* RADAR */}
          <div className="col-md-6">
            <div className="chart-box">
              <h5 className="text-center">Sentiment Radar</h5>
              <RadarChart width={360} height={260} outerRadius={110}
                data={[
                  { label: "Positive", value: pos },
                  { label: "Neutral", value: neu },
                  { label: "Negative", value: neg }
                ]}
              >
                <PolarGrid />
                <PolarAngleAxis dataKey="label" />
                <PolarRadiusAxis />
                <Radar dataKey="value" stroke="#0d6efd" fill="#0d6efd" fillOpacity={0.6} />
              </RadarChart>
            </div>
          </div>

          {/* EMPTY BOX (Top keywords removed) */}
          <div className="col-md-12">
            <div className="chart-box">
              <h5 className="text-center">Additional Insights Coming Soon</h5>
            </div>
          </div>

        </div>
      </div>
    );
  }

  // -------------------------------------------------------------
  // GLOBAL ANALYTICS
  // -------------------------------------------------------------
  let pos = 0, neu = 0, neg = 0;
  const ratings = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };

  allReviews.forEach(r => {
    const s = vaderSentiment(r.review_text);
    if (s === "positive") pos++;
    else if (s === "neutral") neu++;
    else neg++;

    ratings[r.rating]++;
  });

  const globalSentiment = [
    { name: "Positive", value: pos },
    { name: "Neutral", value: neu },
    { name: "Negative", value: neg }
  ];

  const globalRatingData = Object.entries(ratings).map(([star, count]) => ({
    star,
    count
  }));

  const categoryData = Object.entries(
    productList.reduce((acc, p) => {
      acc[p.category || "Other"] = (acc[p.category || "Other"] || 0) + 1;
      return acc;
    }, {})
  ).map(([category, count]) => ({ category, count }));

  return (
    <div className="container py-4">

      <button className="btn btn-outline-secondary mb-3" onClick={() => navigate(-1)}>
        ⬅ Back
      </button>

      <h2 className="fw-bold mb-4">🌍 Global Analytics Dashboard</h2>

      <div className="row g-4">

        <div className="col-md-6">
          <div className="chart-box">
            <h5>Global Sentiment Overview</h5>
            <PieChart width={380} height={260}>
              <Pie data={globalSentiment} dataKey="value" outerRadius={110}>
                {globalSentiment.map((e, i) => (
                  <Cell key={i} fill={COLORS[i]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </div>
        </div>

        <div className="col-md-6">
          <div className="chart-box">
            <h5>Global Rating Distribution</h5>
            <BarChart width={380} height={260} data={globalRatingData}>
              <XAxis dataKey="star" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#0d6efd" />
            </BarChart>
          </div>
        </div>

      </div>

      {/* ROW 2 */}
      <div className="row g-4 mt-2">

        <div className="col-md-6">
          <div className="chart-box">
            <h5>Products by Category</h5>
            <BarChart width={380} height={260} data={categoryData}>
              <XAxis dataKey="category" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#ffc107" />
            </BarChart>
          </div>
        </div>

        <div className="col-md-6">
          <div className="chart-box">
            <h5>Global Sentiment Trend</h5>
            <LineChart width={380} height={260} data={[
              { index: 1, sentiment: pos },
              { index: 2, sentiment: neu },
              { index: 3, sentiment: neg },
            ]}>
              <XAxis dataKey="index" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="sentiment" stroke="#6610f2" strokeWidth={3} />
            </LineChart>
          </div>
        </div>

      </div>

      {/* ROW 3 – EMPTY BOX */}
      <div className="row g-4 mt-2">
        <div className="col-md-12">
          <div className="chart-box">
            <h5 className="text-center">More Global Metrics Coming Soon</h5>
          </div>
        </div>
      </div>

    </div>
  );
}
