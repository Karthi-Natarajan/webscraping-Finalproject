import React, { useState, useEffect } from 'react';
import { useParams, useLocation, Link } from 'react-router-dom';
import api from '../api';
import ThemeToggle from '../components/ThemeToggle';
import ReviewCard from '../components/ReviewCard';

export default function ProductPage() {
  const { id } = useParams();
  const location = useLocation();
  const [reviews, setReviews] = useState([]);
  const [productMeta, setProductMeta] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sentimentFilter, setSentimentFilter] = useState('all');

  // Initialize from location state or fetch from API
  useEffect(() => {
    const initializeData = async () => {
      if (location.state?.reviews) {
        setReviews(location.state.reviews);
        setProductMeta(location.state.meta || {});
      }
      
      try {
        // Always try to fetch fresh data from API
        const res = await api.getReviews(id);
        if (res.data && res.data.reviews) {
          setReviews(res.data.reviews);
        }
        if (res.data && res.data.product) {
          setProductMeta(res.data.product);
        }
      } catch (err) {
        console.warn('Could not fetch fresh reviews:', err);
      } finally {
        setLoading(false);
      }
    };

    initializeData();
  }, [id, location.state]);

  const filteredReviews = reviews.filter(review => {
    if (sentimentFilter === 'all') return true;
    if (sentimentFilter === 'positive') return review.sentiment === 'positive';
    if (sentimentFilter === 'negative') return review.sentiment === 'negative';
    if (sentimentFilter === 'neutral') return review.sentiment === 'neutral';
    return true;
  });

  const sentimentCounts = {
    positive: reviews.filter(r => r.sentiment === 'positive').length,
    negative: reviews.filter(r => r.sentiment === 'negative').length,
    neutral: reviews.filter(r => r.sentiment === 'neutral').length,
  };

  if (loading) {
    return (
      <div className="container">
        <div className="loader">Loading reviews...</div>
      </div>
    );
  }

  return (
    <div className="container">
      <header className="header">
        <h1>
          {productMeta?.name || id.replace(/-/g, ' ')}
          {productMeta?.website && ` (${productMeta.website})`}
        </h1>
        
        <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
          <Link to="/" className="back-btn">🏠 Home</Link>
          <Link to={`/dashboard/${id}`} className="back-btn">📊 Dashboard</Link>
          <ThemeToggle />
        </div>
      </header>

      <main>
        {productMeta?.url && (
          <div className="product-url">
            <a href={productMeta.url} target="_blank" rel="noopener noreferrer">
              View Product on {productMeta.website}
            </a>
          </div>
        )}

        <div className="sentiment-filter">
          <div className="filter-buttons">
            <button 
              className={sentimentFilter === 'all' ? 'active' : ''}
              onClick={() => setSentimentFilter('all')}
            >
              All ({reviews.length})
            </button>
            <button 
              className={sentimentFilter === 'positive' ? 'active' : ''}
              onClick={() => setSentimentFilter('positive')}
            >
              Positive ({sentimentCounts.positive})
            </button>
            <button 
              className={sentimentFilter === 'negative' ? 'active' : ''}
              onClick={() => setSentimentFilter('negative')}
            >
              Negative ({sentimentCounts.negative})
            </button>
            <button 
              className={sentimentFilter === 'neutral' ? 'active' : ''}
              onClick={() => setSentimentFilter('neutral')}
            >
              Neutral ({sentimentCounts.neutral})
            </button>
          </div>
        </div>

        <div className="reviews-container">
          {filteredReviews.length === 0 ? (
            <div className="no-reviews">
              <p>No reviews found for this product.</p>
              <p>Try searching for a different product.</p>
            </div>
          ) : (
            filteredReviews.map((review, index) => (
              <ReviewCard key={index} review={review} />
            ))
          )}
        </div>
      </main>
    </div>
  );
}