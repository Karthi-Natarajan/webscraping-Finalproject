import React, { useState } from "react";
import api from "../api";
import { useNavigate } from "react-router-dom";
import SearchBar from "../components/SearchBar";
import ThemeToggle from "../components/ThemeToggle";

export default function Home(){
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onSearch = async (url) => {
    setLoading(true);
    try {
      const res = await api.scrape(url, 2); // default small pages for fast response
      const productId = res.data.data.product_id;
      navigate(`/product/${productId}`);
    } catch (err) {
      alert("Scrape failed: " + (err.response?.data?.message || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <header className="header">
        <h1>Product Sentiment Analyzer</h1>
        <ThemeToggle />
      </header>
      <main>
        <p>Paste an Amazon or Flipkart product URL below to scrape reviews and get sentiment analytics.</p>
        <SearchBar onSearch={onSearch} loading={loading} />
      </main>
    </div>
  );
}