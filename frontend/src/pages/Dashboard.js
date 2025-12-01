import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../api";
import SentimentPie from "../components/SentimentPie";
import SentimentLine from "../components/SentimentLine";
import WordBar from "../components/WordBar";
import ThemeToggle from "../components/ThemeToggle";

export default function Dashboard(){
  const { id } = useParams();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetch = async () => {
    setLoading(true);
    try {
      const res = await api.getStats(id);
      setStats(res.data.data);
    } catch (err) {
      alert("Failed to fetch stats");
    } finally {
      setLoading(false);
    }
  };

  useEffect(()=>{ fetch(); }, [id]);

  const downloadCSV = async () => {
    const res = await api.export(id, "csv");
    const blob = new Blob([res.data], { type: "text/csv;charset=utf-8;" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `product_${id}_analytics.csv`;
    a.click();
  };

  return (
    <div className="container">
      <header className="header">
        <h1>Sentiment Dashboard</h1>

        <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
          <Link to="/" className="back-btn">🏠 Home</Link>
          <Link to={`/product/${id}`} className="back-btn">🔙 Reviews</Link>
          <ThemeToggle />
        </div>
      </header>

      <main>
        {loading ? (
          <div className="loader">Loading analytics...</div>
        ) : stats && (
          <>
            <div className="charts-row">
              <SentimentPie counts={stats.counts} />
              <SentimentLine trend={stats.trend} />
            </div>

            <div className="charts-row">
              <WordBar words={stats.top_words} />

              <div className="export-panel">
                <button onClick={downloadCSV}>Export CSV</button>
                <a
                  href={`/api/product/${id}/export?format=pdf`}
                  target="_blank"
                  rel="noreferrer"
                >
                  <button>Download PDF</button>
                </a>
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
