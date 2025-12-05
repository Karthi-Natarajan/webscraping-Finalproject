import React, { useState } from "react";
import api from "../api";
import { useNavigate } from "react-router-dom";
import SearchBar from "../components/SearchBar";
import ThemeToggle from "../components/ThemeToggle";

export default function Home() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const detectWebsite = (url) => {
    url = url.toLowerCase();
    if (url.includes("flipkart")) return "flipkart";
    if (url.includes("amazon")) return "amazon";
    return "flipkart"; // Default
  };

  const extractKeyword = (url) => {
    // Extract keyword from URL or use the text as is
    if (url.includes("http")) {
      // Try to extract product name from URL
      try {
        const urlObj = new URL(url);
        const pathname = urlObj.pathname;
        // Extract product name from path
        const parts = pathname.split('/');
        const lastPart = parts[parts.length - 1];
        return lastPart.replace(/-/g, ' ').split('?')[0];
      } catch {
        return url;
      }
    }
    return url; // If it's just text, use it as keyword
  };

  const onSearch = async (url) => {
    setLoading(true);
    try {
      const website = detectWebsite(url);
      const keyword = extractKeyword(url);
      
      // Call scrape endpoint with GET and query params
      const res = await api.scrape(keyword, website);
      
      // Check if we got data
      if (!res.data) {
        throw new Error("No data received from scrape");
      }

      // Create product id
      const productId = keyword.replace(/\s+/g, "-").toLowerCase();
      
      // Save the reviews to database
      try {
        await api.saveReviews(
          { 
            name: keyword, 
            website: website,
            url: url.includes("http") ? url : null
          }, 
          res.data.reviews || []
        );
      } catch (saveError) {
        console.warn("Failed to save reviews:", saveError);
        // Continue even if save fails
      }

      // Navigate to product page with data
      navigate(`/product/${productId}`, { 
        state: { 
          meta: { keyword, website },
          reviews: res.data.reviews || []
        } 
      });

    } catch (err) {
      console.error("Scrape error:", err);
      alert("Scrape failed: " + (err.response?.data?.message || err.message || "Unknown error"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home-container">
      <header className="home-header">
        <h1>Product Sentiment Analyzer</h1>
        <ThemeToggle />
      </header>

      <main className="home-main">
        <p>Paste an Amazon or Flipkart product URL, or type product name.</p>
        <SearchBar onSearch={onSearch} loading={loading} />
      </main>
    </div>
  );
}