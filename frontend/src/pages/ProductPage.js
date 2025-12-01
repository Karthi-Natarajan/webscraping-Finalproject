import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../api";
import ReviewCard from "../components/ReviewCard";
import ThemeToggle from "../components/ThemeToggle";

export default function ProductPage(){
  const { id } = useParams();
  const [reviews, setReviews] = useState([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  const fetch = async (p=1) => {
    setLoading(true);
    try {
      const res = await api.getReviews(id, p, 20);
      setReviews(res.data.data.reviews);
      setTotal(res.data.data.total);
      setPage(p);
    } catch (err) {
      alert("Failed to fetch reviews");
    } finally {
      setLoading(false);
    }
  };

  useEffect(()=>{ fetch(1); }, [id]);

  return (
    <div className="container">
      <header className="header">
        <h1>Product Reviews</h1>

        <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
          <Link to="/" className="back-btn">🏠 Home</Link>
          <Link to={`/dashboard/${id}`} className="back-btn">📊 Dashboard</Link>
          <ThemeToggle />
        </div>
      </header>

      <main>
        {loading ? (
          <div className="loader">Loading reviews...</div>
        ) : (
          <>
            <div className="reviews-grid">
              {reviews.map(r => <ReviewCard key={r._id} review={r} />)}
            </div>

            <div className="pagination">
              <button onClick={()=>fetch(Math.max(1, page-1))} disabled={page<=1}>Previous</button>
              <span>Page {page}</span>
              <button onClick={()=>fetch(page+1)} disabled={(page*20)>=total}>Next</button>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
